"""Semantic intent classification for incoming student messages.

Three tiers, cheapest first:

1. **Structural** — message shapes that carry their own meaning regardless of
   wording: a bare URL, a bare number, emoji-only, a yes/no reply.
2. **Lexical similarity** — IDF-weighted coverage of the labelled corpus in
   :mod:`services.nlu.examples`, computed over canonical tokens so that
   phrasing, word order, language, and typos do not change the answer.
3. **LLM few-shot** — only when tier 2 is genuinely uncertain, so the common
   path stays synchronous and free.

The old design let one regex hit decide the route, which meant a synonym or a
typo silently changed behaviour. Here every intent is scored and the winner has
to beat both an absolute floor and its nearest rival.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import replace

from loguru import logger

from services.nlu.arithmetic import evaluate_arithmetic
from services.nlu.examples import INTENT_EXAMPLES, LLM_FEW_SHOT
from services.nlu.intents import IntentResult, StudentIntent
from services.nlu.normalize import (
    canonical_tokens,
    contains_url,
    has_word_characters,
    raw_tokens,
    strip_urls,
)

#: Winning score below this is not trusted on its own.
ACCEPT_THRESHOLD = 0.55
#: Below this the LLM tier is consulted (when available).
LLM_FALLBACK_CEILING = 0.72
#: The winner must beat the runner-up by this margin to be unambiguous.
MARGIN = 0.08

#: A single turn classifies the same message from several call sites (pipeline,
#: decision graph, router, agents). Classification is pure, so memoise it and
#: drop the whole map once it grows rather than tracking per-entry recency.
_CACHE: dict[str, IntentResult] = {}
_CACHE_MAX = 512

_AFFIRM = frozenset(
    {"yes", "y", "yeah", "yep", "yea", "sure", "ok", "okay", "confirm", "agree",
     "proceed", "correct", "right", "please", "yesplease", "goahead", "doit",
     "sendit", "yup", "yas", "ye",
     "oww", "hari", "ඔව්", "ඔව්වා", "හරි", "ஆம்", "ஆமாம்", "சரி"}
)
_DENY = frozenset(
    {"no", "n", "nope", "nah", "nothanks", "dont", "cancel", "nevermind",
     "notright", "wrong", "නෑ", "නැහැ", "එපා", "இல்லை", "வேண்டாம்"}
)
_GREETINGS = frozenset(
    {"hi", "hello", "hey", "hiya", "yo", "thanks", "thankyou", "thx", "bye",
     "goodbye", "morning", "afternoon", "evening", "goodmorning"}
)

#: Question words, time modifiers, and pronouns. They shape a request but never
#: establish one: "what ... today" is shared by "is there class today" and "what
#: is the weather today". A match must overlap on at least one token outside
#: this set, or it is coincidence.
_NON_ANCHORING = frozenset(
    {
        "what", "which", "who", "how", "when", "where", "why", "howmuch",
        "can", "want", "need", "give", "get", "have", "see", "tell", "show",
        "i", "me", "my", "you", "your", "we", "us",
        "today", "tomorrow", "next", "week", "now", "day", "days",
        "about", "detail", "info", "information", "yes", "no",
    }
)


#: One example's token set paired with the summed IDF of those tokens.
_ExampleEntry = tuple[frozenset[str], float]
_Index = dict[StudentIntent, tuple[_ExampleEntry, ...]]


def _build_index() -> tuple[frozenset[str], dict[str, float], _Index]:
    """Precompute vocabulary, IDF weights, and per-example token sets."""
    tokenized: dict[StudentIntent, list[list[str]]] = {}
    document_freq: dict[str, int] = defaultdict(int)
    total_docs = 0

    for intent, phrases in INTENT_EXAMPLES.items():
        docs = [canonical_tokens(phrase) for phrase in phrases]
        tokenized[intent] = docs
        for doc in docs:
            total_docs += 1
            for token in set(doc):
                document_freq[token] += 1

    vocabulary = frozenset(document_freq)
    idf = {
        token: math.log((total_docs + 1) / (freq + 1)) + 1.0
        for token, freq in document_freq.items()
    }

    index: _Index = {}
    for intent, docs in tokenized.items():
        entries: list[_ExampleEntry] = []
        for doc in docs:
            tokens = frozenset(doc)
            weight = sum(idf[t] for t in tokens)
            if weight > 0:
                entries.append((tokens, weight))
        index[intent] = tuple(entries)

    return vocabulary, idf, index


_VOCABULARY, _IDF, _INDEX = _build_index()

#: Weight of a message token absent from the corpus, as a fraction of the
#: median IDF. Tuned so that one unfamiliar topic noun does not sink a clear
#: request, while several of them still mark a message as off-domain.
_OOV_DAMPING = 0.6
_OOV_WEIGHT = _OOV_DAMPING * (sorted(_IDF.values())[len(_IDF) // 2] if _IDF else 1.0)


def vocabulary() -> frozenset[str]:
    """Domain vocabulary used for typo correction."""
    return _VOCABULARY


def score_intents(message: str) -> dict[StudentIntent, float]:
    """IDF-weighted F1 between the message and each intent's best example.

    Recall alone rewards short generic examples ("my class details" is fully
    covered by any message containing *my* and *class*). Precision alone rewards
    long examples. Their harmonic mean, weighted by IDF so that *time* counts
    for more than *class*, separates neighbouring intents reliably.
    """
    tokens = frozenset(canonical_tokens(message, vocabulary=_VOCABULARY))
    if not tokens:
        return {}

    # Unknown words are damped rather than dropped. They are usually topic
    # content ("momentum", "2023") which should not outvote the intent verbs —
    # but ignoring them entirely would make "what is the weather today" look
    # exactly like "is there class today".
    known = tokens & _VOCABULARY
    message_weight = sum(_IDF[t] for t in known) + _OOV_WEIGHT * len(tokens - _VOCABULARY)
    if message_weight <= 0:
        return {}

    scores: dict[StudentIntent, float] = {}
    for intent, entries in _INDEX.items():
        best = 0.0
        for example_tokens, example_weight in entries:
            overlap = known & example_tokens
            if not overlap or not (overlap - _NON_ANCHORING):
                continue
            covered = sum(_IDF[t] for t in overlap)
            recall = covered / example_weight
            precision = covered / message_weight
            f1 = 2 * recall * precision / (recall + precision)
            # A single shared token is coincidence, not intent: "what is the
            # weather today" overlaps "is there class today" on `today` alone.
            # A one-word message ("tutes?") is exempt — one token is all it has.
            needed = min(2, len(example_tokens), len(known))
            support = min(1.0, len(overlap) / needed)
            best = max(best, f1 * support)
        if best > 0:
            scores[intent] = round(min(best, 1.0), 4)
    return scores


def _structural_intent(message: str) -> IntentResult | None:
    """Message shapes whose meaning does not depend on wording."""
    text = (message or "").strip()
    if not text:
        return IntentResult(StudentIntent.UNKNOWN, 1.0, "structural", reasoning="empty message")

    if contains_url(text) and not has_word_characters(strip_urls(text)):
        return IntentResult(
            StudentIntent.LINK_SHARED, 1.0, "structural", reasoning="message is a bare link"
        )

    if not has_word_characters(text):
        return IntentResult(
            StudentIntent.UNKNOWN,
            1.0,
            "structural",
            entities={"non_textual": True},
            reasoning="no letters or digits (emoji or punctuation only)",
        )

    # Arithmetic is squarely on-topic for a tuition centre. Deflecting "2+2?"
    # as off-topic (A5) was the filter overreaching, so it is classified as a
    # lesson question and carries its own answer.
    answer = evaluate_arithmetic(text)
    if answer is not None:
        return IntentResult(
            StudentIntent.LESSON_HELP,
            1.0,
            "structural",
            entities={"arithmetic_answer": answer},
            reasoning="bare arithmetic expression",
        )

    tokens = raw_tokens(text)
    if len(tokens) <= 3:
        collapsed = "".join(tokens)
        if collapsed in _AFFIRM or (len(tokens) == 1 and tokens[0] in _AFFIRM):
            return IntentResult(StudentIntent.AFFIRM, 1.0, "structural", reasoning="affirmative reply")
        if collapsed in _DENY or (len(tokens) == 1 and tokens[0] in _DENY):
            return IntentResult(StudentIntent.DENY, 1.0, "structural", reasoning="negative reply")
        if tokens and all(t in _GREETINGS for t in tokens):
            return IntentResult(StudentIntent.GREETING, 1.0, "structural", reasoning="greeting")
        if len(tokens) == 1 and tokens[0].isdigit():
            return IntentResult(
                StudentIntent.UNKNOWN,
                1.0,
                "structural",
                entities={"selection_number": int(tokens[0])},
                reasoning="numeric selection reply",
            )
    return None


def classify(message: str) -> IntentResult:
    """Classify without any LLM call. Safe to use on hot synchronous paths."""
    cached = _CACHE.get(message)
    if cached is not None:
        return _copy_result(cached)
    result = _classify_uncached(message)
    if len(_CACHE) >= _CACHE_MAX:
        _CACHE.clear()
    _CACHE[message] = result
    return _copy_result(result)


def _copy_result(result: IntentResult) -> IntentResult:
    # Callers treat the result as their own, so never hand out the cached
    # instance itself -- entities in particular get read and enriched downstream.
    return replace(result, entities=dict(result.entities))


def _classify_uncached(message: str) -> IntentResult:
    structural = _structural_intent(message)
    if structural is not None:
        return structural

    scores = score_intents(message)
    if not scores:
        return IntentResult(StudentIntent.UNKNOWN, 0.0, "lexical", reasoning="no known concepts")

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_intent, top_score = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0.0

    if top_score < ACCEPT_THRESHOLD or (top_score - runner_up) < MARGIN:
        return IntentResult(
            StudentIntent.UNKNOWN,
            top_score,
            "lexical",
            entities={"candidates": [(i.value, s) for i, s in ranked[:3]]},
            reasoning=f"ambiguous (top={top_intent.value}@{top_score:.2f}, next={runner_up:.2f})",
        )

    return IntentResult(
        top_intent,
        top_score,
        "lexical",
        reasoning=f"lexical match {top_score:.2f} (next {runner_up:.2f})",
    )


_LLM_SYSTEM_PROMPT = f"""\
You classify one WhatsApp message from a student of a Sri Lankan tuition centre \
into exactly one intent label.

Labels:
  class_list        - asking which classes/subjects/courses the centre offers
  class_detail      - asking the fee, price, or details of a specific class
  enroll            - wants to join, register, or sign up for a class
  my_enrollments    - asking which classes THEY are already signed up for
  cancel_enrollment - wants to cancel, stop, drop, or withdraw from a class
  tutor_info        - asking about the tutor, teacher, staff, or team
  centre_info       - asking about the centre itself (location, contact, about)
  schedule          - asking class times, days, timetable, next class
  resource_files    - asking for past papers, tutes, notes, textbooks, syllabus
  lesson_help       - asking to explain an academic topic or concept
  payment_submit    - sending/announcing a payment, or asking how to pay
  payment_status    - asking whether their payment was received or approved
  escalation        - wants a human: speak to tutor, complaint, urgent matter
  profile_lookup    - asking about their own stored profile details
  greeting          - greeting, thanks, or small talk
  off_topic         - not about tuition, or abusive/profane in any form
  unknown           - genuinely unclear

Rules:
- Classify by MEANING, not by keywords. Word order, synonyms, typos, and \
Sinhala/Tamil/Singlish mixing must not change the label.
- A message is off_topic if it is abusive or profane, whether phrased as a \
question or a statement.
- "What classes do you offer" is class_list; "What classes am I in" is \
my_enrollments. Do not confuse them.

Examples:
{LLM_FEW_SHOT}
Answer with the label only."""


async def aclassify(message: str, *, llm=None) -> IntentResult:
    """Classify, escalating to the LLM only when lexical matching is uncertain."""
    result = classify(message)
    confident_enough = (
        result.source == "structural"
        or (result.intent is not StudentIntent.UNKNOWN and result.confidence >= LLM_FALLBACK_CEILING)
    )
    if confident_enough or llm is None:
        return result

    try:
        response = await llm.ainvoke(
            [
                {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                {"role": "user", "content": (message or "").strip()[:1000]},
            ]
        )
    except Exception as exc:
        logger.warning("Intent LLM failed ({}); keeping lexical result.", exc)
        return result

    raw = (response.content if hasattr(response, "content") else str(response)).strip().lower()
    label = re.sub(r"[^a-z_]", "", raw.split()[0] if raw.split() else "")
    try:
        intent = StudentIntent(label)
    except ValueError:
        logger.debug("Intent LLM returned unusable label {!r}", raw[:60])
        return result

    return IntentResult(intent, 0.85, "llm", reasoning=f"LLM label {label}")

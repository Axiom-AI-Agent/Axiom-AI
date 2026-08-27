"""Text normalization for intent classification.

Incoming student messages are WhatsApp-grade: typos, emoji, mixed English with
Sinhala/Tamil script, and romanized Singlish/Tanglish. Everything here reduces a
message to a bag of *canonical English concept tokens* so that downstream
matching compares meaning rather than surface spelling.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

# Sinhala script, Tamil script, and romanized particles all collapse onto the
# same English concept token so one example corpus serves every language.
_LEXICON: dict[str, str] = {
    # ── class / course ────────────────────────────────────────────────
    "පන්ති": "class",
    "පන්තිය": "class",
    "පන්තියට": "class",
    "පන්තියක්": "class",
    "වගුප්": "class",
    "வகுப்பு": "class",
    "வகுப்பில்": "class",
    "வகுப்புகள்": "class",
    "panthi": "class",
    "panthiya": "class",
    "panthiyata": "class",
    # ── enrol / join / register ───────────────────────────────────────
    "ලියාපදිංචි": "enroll",
    "ලියාපදිංචිය": "enroll",
    "එකතු": "join",
    "සම්බන්ධ": "join",
    "பதிவு": "enroll",
    "பதிவுசெய்": "enroll",
    "சேர": "join",
    "சேர்க்கை": "join",
    "join": "join",
    "karanna": "do",
    "wenna": "become",
    "enroll": "enroll",
    # ── papers / tutes / notes / books ────────────────────────────────
    "පේපර්": "paper",
    "පේපර්ස්": "paper",
    "ටියුට්": "tute",
    "ටියුෂන්": "tuition",
    "නෝට්ස්": "notes",
    "පාඩම්": "lesson",
    "පෙළපොත්": "textbook",
    "පාඩම": "lesson",
    "பேப்பர்": "paper",
    "தாள்": "paper",
    "பாடத்தாள்": "paper",
    "குறிப்பு": "notes",
    "பாடம்": "lesson",
    "பாடநூல்": "textbook",
    "பாடக்குறிப்பு": "notes",
    "பாடத்திட்டம்": "syllabus",
    "tute": "tute",
    "tutes": "tute",
    # ── fees / payment ────────────────────────────────────────────────
    "ගාස්තු": "fee",
    "ගාස්තුව": "fee",
    "ගෙවීම": "payment",
    "ගෙවුවා": "paid",
    "ගෙවන්න": "pay",
    "රිසිට්": "receipt",
    "රිසිට්පත": "receipt",
    "බැංකු": "bank",
    "கட்டணம்": "fee",
    "பணம்": "payment",
    "ரசீது": "receipt",
    "வங்கி": "bank",
    "கட்டி": "paid",
    "gaasthu": "fee",
    "ganan": "fee",
    "gewuwa": "paid",
    "geewuwa": "paid",
    "gewanna": "pay",
    "kattanum": "pay",
    "kattiten": "paid",
    "kattitten": "paid",
    "slip": "slip",
    # ── tutor / staff ─────────────────────────────────────────────────
    "ගුරුවරයා": "tutor",
    "ගුරුවරය": "tutor",
    "ගුරු": "tutor",
    "ගුරුතුමා": "tutor",
    "සර්": "tutor",
    "ஆசிரியர்": "tutor",
    "ஆசிரிய": "tutor",
    "ஆசிரியரை": "tutor",
    "sir": "tutor",
    "madam": "tutor",
    "teacher": "tutor",
    "aasiriyar": "tutor",
    "asiriyar": "tutor",
    # ── talk to / contact a person ────────────────────────────────────
    "කතා": "talk",
    "කථා": "talk",
    "பேச": "talk",
    "பேசு": "talk",
    "katha": "talk",
    "kata": "talk",
    "pesa": "talk",
    "pesanum": "talk",
    "pesanam": "talk",
    # ── schedule / time ───────────────────────────────────────────────
    "වේලාව": "time",
    "කාලසටහන": "timetable",
    "වෙලාව": "time",
    "අද": "today",
    "හෙට": "tomorrow",
    "ඊළඟ": "next",
    "සතිය": "week",
    "நேரம்": "time",
    "அட்டவணை": "timetable",
    "இன்று": "today",
    "நாளை": "tomorrow",
    "அடுத்த": "next",
    "வாரம்": "week",
    "welawa": "time",
    "ada": "today",
    "heta": "tomorrow",
    "issarahata": "next",
    # ── cancel / stop ─────────────────────────────────────────────────
    "අවලංගු": "cancel",
    "නවත්වන්න": "stop",
    "නැවැත්වීම": "stop",
    "ரத்து": "cancel",
    "நிறுத்த": "stop",
    "nawaththanna": "stop",
    # ── yes / no ──────────────────────────────────────────────────────
    "ඔව්": "yes",
    "ඔව්වා": "yes",
    "හරි": "yes",
    "නෑ": "no",
    "නැහැ": "no",
    "එපා": "no",
    "ஆம்": "yes",
    "ஆமாம்": "yes",
    "சரி": "yes",
    "இல்லை": "no",
    "வேண்டாம்": "no",
    "oww": "yes",
    "hari": "yes",
    "nehe": "no",
    # ── question / help words ─────────────────────────────────────────
    "මොකක්ද": "what",
    "කොහොමද": "how",
    "කීයද": "howmuch",
    "කවුද": "who",
    "කොහෙද": "where",
    "උදව්": "help",
    "පැහැදිලි": "explain",
    "විස්තර": "detail",
    "කියන්න": "tell",
    "කියලා": "tell",
    "තියෙනවද": "available",
    "පුළුවන්ද": "can",
    "එවන්න": "send",
    "යවන්න": "send",
    "යවනවා": "send",
    "එවනවා": "send",
    "ඕන": "want",
    "ඕනේ": "want",
    "අවශ්": "want",
    "என்ன": "what",
    "எப்படி": "how",
    "யார்": "who",
    "எங்கே": "where",
    "உதவி": "help",
    "விளக்கு": "explain",
    "விவரம்": "detail",
    "சொல்": "tell",
    "சொல்லுங்கள்": "tell",
    "இருக்கா": "available",
    "அனுப்பு": "send",
    "வேண்டும்": "want",
    "mokakda": "what",
    "mokada": "what",
    "kohomada": "how",
    "kiyada": "howmuch",
    "kawuda": "who",
    "koheda": "where",
    "kiyanna": "tell",
    "kiyala": "tell",
    "kiyapan": "tell",
    "thiyenawada": "available",
    "thiyanawada": "available",
    "thiyenawa": "available",
    "puluwanda": "can",
    "ewanna": "send",
    "evanna": "send",
    "yawanawa": "send",
    "yavanava": "send",
    "ewanawa": "send",
    "anuppu": "send",
    "anuppunga": "send",
    "anuppuren": "send",
    "ona": "want",
    "oona": "want",
    "oney": "want",
    "sollu": "tell",
    "sollunga": "tell",
    "venum": "want",
    "vendum": "want",
    "pannanum": "want",
    "irukka": "available",
    "enakku": "me",
    "vaguppu": "class",
    "vakuppu": "class",
    # ── filler particles that carry no intent ─────────────────────────
    "eka": "",
    "ekata": "",
    "ekak": "",
    "එක": "",
    "වෙන්න": "",
    "කරන්න": "",
    "නම්": "",
    "ஒரு": "",
    "பண்ண": "",
    "mata": "me",
    "mage": "my",
    "මට": "me",
    "මගේ": "my",
    "මම": "me",
    "ඔබ": "you",
    "எனக்கு": "me",
    "என்": "my",
    "நான்": "me",
    "tika": "",
    "tike": "",
    "ටික": "",
    "මේ": "",
    "මෙම": "",
    "kitta": "",
    "la": "",
    "panna": "",
    "இடம்": "",
    "denna": "give",
    "dennako": "give",
    "gena": "about",
    "unga": "your",
}

# Words that are grammatically necessary but intent-neutral. Dropping them keeps
# short paraphrases ("what classes do you teach" vs "which classes are taught")
# from being penalised for filler mismatch.
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "am",
        "do",
        "does",
        "did",
        "to",
        "of",
        "in",
        "on",
        "at",
        "for",
        "with",
        "and",
        "or",
        "but",
        "if",
        "so",
        "as",
        "by",
        "from",
        "that",
        "this",
        "these",
        "those",
        "there",
        "here",
        "it",
        "its",
        "please",
        "pls",
        "just",
        "some",
        "any",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "im",
        "ive",
        "id",
        "s",
        "t",
        "re",
        "ll",
        "ve",
    }
)

# Surface variants that must collapse before matching so "sign up", "signup" and
# "sign-up" are one concept.
_PHRASES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bsign\s*[- ]?\s*up\b"), "signup"),
    (re.compile(r"\bhow\s+much\b"), "howmuch"),
    (re.compile(r"\ba\s*/?\s*l\b"), "al"),
    (re.compile(r"\bo\s*/?\s*l\b"), "ol"),
    (re.compile(r"\badvanced\s+level\b"), "al"),
    (re.compile(r"\bordinary\s+level\b"), "ol"),
    (re.compile(r"\bpast\s+papers?\b"), "pastpaper"),
    (re.compile(r"\bmodel\s+papers?\b"), "pastpaper"),
    (re.compile(r"\btext\s*books?\b"), "textbook"),
    (re.compile(r"\btime\s*table\b"), "timetable"),
    (re.compile(r"\bbank\s+slip\b"), "bankslip"),
    (re.compile(r"\bpayment\s+slip\b"), "bankslip"),
    (re.compile(r"\bclass\s+eka\b"), "class"),
    # Romanized "ඕන/வேணும்" is spelled "one" in Singlish, which collides with
    # the English numeral. Only the verb-plus-"one" shape is the Sinhala word.
    # Runs before the verb collapses below, which would otherwise eat the verb
    # and leave a bare "one".
    (re.compile(r"\b(?:karanna|kranna|panna|wenna|venna)\s+one\b"), "ona"),
    (re.compile(r"\bjoin\s+karanna\b"), "join"),
    (re.compile(r"\benroll\s+wenna\b"), "enroll"),
)

# Morphological suffixes stripped so "classes"/"class" and "cancelling"/"cancel"
# share a token. Order matters: longest first.
_SUFFIXES = ("ings", "ing", "ies", "es", "ed", "s")

_IRREGULAR_STEMS = {
    "classes": "class",
    "clases": "class",
    "class": "class",
    "fees": "fee",
    "details": "detail",
    "notes": "notes",
    "papers": "paper",
    "does": "do",
    "was": "be",
    "teaches": "teach",
    "taught": "teach",
    "teaching": "teach",
    "enrolment": "enroll",
    "enrollment": "enroll",
    "enrolled": "enroll",
    "enrolling": "enroll",
    "registration": "enroll",
    "registered": "enroll",
    "cancellation": "cancel",
    "cancelling": "cancel",
    "canceling": "cancel",
    "cancelled": "cancel",
    "available": "available",
    "availability": "available",
    "scheduled": "schedule",
    "schedules": "schedule",
    "payments": "payment",
    "receipts": "receipt",
    "tutors": "tutor",
    "teachers": "tutor",
    "lessons": "lesson",
    "subjects": "subject",
    "courses": "course",
}

_EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
    (0xFE00, 0xFE0F),
    (0x1F1E6, 0x1F1FF),
    (0x2190, 0x21FF),
    (0x2B00, 0x2BFF),
)

_URL_RE = re.compile(r"https?://\S+|www\.\S+|\b\S+\.(?:com|org|net|lk|io|co|edu|gov)\b/?\S*", re.IGNORECASE)

# ``\w`` excludes combining marks, which would split every Sinhala and Tamil
# word at its vowel signs (පන්තිය → පන, ත, ය). Admitting both scripts wholesale
# keeps those words intact.
_TOKEN_RE = re.compile(r"(?:[^\W_]|[\u0B80-\u0BFF\u0D80-\u0DFF])+", re.UNICODE)


def is_emoji(char: str) -> bool:
    code = ord(char)
    return any(low <= code <= high for low, high in _EMOJI_RANGES)


def strip_emoji(text: str) -> str:
    return "".join(ch for ch in text if not is_emoji(ch))


def contains_url(text: str) -> bool:
    return bool(_URL_RE.search(text or ""))


def strip_urls(text: str) -> str:
    return _URL_RE.sub(" ", text or "")


def has_word_characters(text: str) -> bool:
    """True when the text contains at least one letter or digit in any script."""
    return any(unicodedata.category(ch)[0] in {"L", "N"} for ch in strip_emoji(text or ""))


# Openers that make a message a request rather than a statement. Used to tell a
# slot answer apart from a new question: "My name is Mirco" and "What is my
# name" share every content word, and only the shape distinguishes them.
_QUESTION_OPENERS = frozenset(
    {
        "what", "which", "who", "whose", "whom", "how", "when", "where", "why",
        "can", "could", "may", "do", "does", "did", "is", "are", "am", "was",
        "were", "will", "would", "should", "any", "have", "has",
        "mokakda", "mokada", "monawada", "kohomada", "kawuda", "koheda", "kiyada",
        "මොකක්ද", "මොනවද", "කොහොමද", "කවුද", "කොහෙද", "කීයද",
        "என்ன", "எப்படி", "யார்", "எங்கே",
    }
)

_REQUEST_VERBS = frozenset(
    {
        "explain", "send", "share", "show", "tell", "give", "list", "help",
        "teach", "download", "cancel", "join", "enroll", "register", "sign",
        "signup", "connect", "speak", "talk", "check", "find", "need", "want",
        "ewanna", "evanna", "denna", "kiyanna", "anuppu", "anuppunga",
        "එවන්න", "යවන්න", "කියන්න", "පැහැදිලි",
        "அனுப்பு", "சொல்", "விளக்கு",
    }
)


def looks_like_request(text: str) -> bool:
    """True when the message asks for something rather than states a value.

    A tuition centre's onboarding asks a question every turn, so almost any
    reply shares vocabulary with some intent. Requiring a request shape before
    a classified intent is allowed to abandon slot collection keeps "My name is
    Mirco Fernando" and "A/L Physics" as answers instead of new questions.
    """
    stripped = (text or "").strip()
    if not stripped:
        return False
    if "?" in stripped:
        return True
    tokens = raw_tokens(stripped)
    if not tokens:
        return False
    if tokens[0] in _QUESTION_OPENERS:
        return True
    return any(token in _REQUEST_VERBS for token in tokens)


def _stem(token: str) -> str:
    if token in _IRREGULAR_STEMS:
        return _IRREGULAR_STEMS[token]
    if len(token) <= 4:
        return token
    for suffix in _SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[: -len(suffix)]
    return token


# Sinhala and Tamil are agglutinative: case and definiteness are glued onto the
# stem (ගාස්තු → ගාස්තුව, வகுப்பு → வகுப்பில்). Matching the longest lexicon
# entry that prefixes the token recovers the stem without a full morphology
# table.
_SCRIPT_LEXICON_KEYS = tuple(
    sorted((key for key in _LEXICON if not key.isascii()), key=len, reverse=True)
)


def _lookup(token: str) -> str:
    mapped = _LEXICON.get(token)
    if mapped is not None:
        return mapped
    if not token.isascii():
        for key in _SCRIPT_LEXICON_KEYS:
            if token.startswith(key):
                return _LEXICON[key]
    return token


def raw_tokens(text: str) -> list[str]:
    """Lowercased word tokens with emoji and URLs removed, no lexicon applied."""
    cleaned = strip_emoji(strip_urls(text or ""))
    cleaned = unicodedata.normalize("NFKC", cleaned).lower()
    for pattern, replacement in _PHRASES:
        cleaned = pattern.sub(replacement, cleaned)
    return _TOKEN_RE.findall(cleaned)


def canonical_tokens(text: str, *, vocabulary: frozenset[str] | None = None) -> list[str]:
    """Reduce a message to canonical concept tokens.

    Applies, in order: emoji/URL removal, phrase collapsing, the multilingual
    lexicon, stopword removal, stemming, and (when a ``vocabulary`` is supplied)
    typo correction against that vocabulary.
    """
    out: list[str] = []
    for token in raw_tokens(text):
        mapped = _lookup(token)
        if not mapped:
            continue
        stemmed = _stem(mapped)
        if stemmed in _STOPWORDS or not stemmed:
            continue
        if vocabulary is not None and stemmed not in vocabulary:
            corrected = closest_term(stemmed, vocabulary)
            if corrected:
                stemmed = corrected
        out.append(stemmed)
    return out


def closest_term(token: str, vocabulary: frozenset[str], *, cutoff: float = 0.82) -> str | None:
    """Nearest vocabulary term for a possible typo ("clss" → "class").

    Short tokens are skipped: at three characters or fewer, edit distance is not
    evidence of a typo and correction does more harm than good.
    """
    if len(token) <= 3:
        return None
    best: str | None = None
    best_score = cutoff
    for term in vocabulary:
        if abs(len(term) - len(token)) > 3:
            continue
        score = SequenceMatcher(None, token, term).ratio()
        if score > best_score:
            best_score = score
            best = term
    return best

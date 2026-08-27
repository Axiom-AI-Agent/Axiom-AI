"""Ad-hoc benchmark for the NLU layer's import and per-call cost."""

from __future__ import annotations

import statistics
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.stdout.reconfigure(encoding="utf-8")

tracemalloc.start()
t0 = time.perf_counter()
from services.nlu import classify  # noqa: E402
from services.nlu.classifier import _INDEX, _VOCABULARY  # noqa: E402

import_ms = (time.perf_counter() - t0) * 1000
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

examples = sum(len(v) for v in _INDEX.values())
print(f"import + index build : {import_ms:.1f} ms")
print(f"corpus               : {examples} examples across {len(_INDEX)} intents")
print(f"vocabulary           : {len(_VOCABULARY)} tokens")
print(f"resident after import: {current / 1024:.0f} KB (peak {peak / 1024:.0f} KB)")

MESSAGES = [
    "What classes do you teach?",
    "I want to join another class",
    "Can I get some information on the tutor?",
    "What is the schedule for my physics clss",
    "ගාස්තු ගෙවුවා, slip එක යවනවා",
    "Yes",
    "https://docs.google.com/document/d/abc123/edit",
    "Explain momentum from the uploaded notes and the past papers from 2023",
]

for message in MESSAGES:
    classify(message)  # warm

print()
timings = []
for message in MESSAGES:
    samples = []
    for _ in range(2000):
        t = time.perf_counter()
        classify(message)
        samples.append((time.perf_counter() - t) * 1_000_000)
    median = statistics.median(samples)
    timings.append(median)
    print(f"{median:8.1f} µs  {message[:52]}")

print(f"\nmedian across messages: {statistics.median(timings):.1f} µs")

from services.nlu.classifier import _CACHE, _classify_uncached  # noqa: E402

cold, warm = [], []
for message in MESSAGES:
    for _ in range(2000):
        t = time.perf_counter()
        _classify_uncached(message)
        cold.append((time.perf_counter() - t) * 1_000_000)
        _CACHE[message] = _classify_uncached(message)
        t = time.perf_counter()
        classify(message)
        warm.append((time.perf_counter() - t) * 1_000_000)

print(f"uncached median : {statistics.median(cold):.1f} µs")
print(f"cache-hit median: {statistics.median(warm):.1f} µs")

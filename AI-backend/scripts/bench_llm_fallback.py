"""Measure how many real student messages still need an LLM round trip."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from agents.router import _ROUTE_CONFIDENCE_FLOOR  # noqa: E402
from services.nlu import classify  # noqa: E402

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
LOG = Path(r"C:\Users\HP\Desktop\Student side Testing log.xlsx")


def read_cells(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ElementTree.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{NS}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{NS}t")))
        sheet = ElementTree.fromstring(zf.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.iter(f"{NS}row"):
            cells = []
            for c in row.findall(f"{NS}c"):
                v = c.find(f"{NS}v")
                if v is None or v.text is None:
                    cells.append("")
                elif c.get("t") == "s":
                    cells.append(shared[int(v.text)])
                else:
                    cells.append(v.text)
            rows.append(cells)
        return rows


rows = read_cells(LOG)
header = [h.strip().lower() for h in rows[0]]
try:
    col = next(i for i, h in enumerate(header) if "input" in h or "message" in h or "query" in h)
except StopIteration:
    print("columns:", header)
    raise SystemExit(1)

messages = []
for row in rows[1:]:
    if col < len(row) and row[col].strip():
        text = re.sub(r"\s+", " ", row[col]).strip()
        if len(text) > 1:
            messages.append(text)

confident = 0
by_intent: dict[str, int] = {}
unresolved: list[str] = []
for message in messages:
    result = classify(message)
    by_intent[result.intent.value] = by_intent.get(result.intent.value, 0) + 1
    if result.confidence >= _ROUTE_CONFIDENCE_FLOOR:
        confident += 1
    else:
        unresolved.append(f"{result.confidence:.2f}  {message[:70]}")

total = len(messages)
print(f"real student messages sampled : {total}")
print(f"resolved without LLM router   : {confident} ({confident / total:.0%})")
print(f"still need LLM router         : {total - confident} ({(total - confident) / total:.0%})")
print("\nintent distribution:")
for intent, count in sorted(by_intent.items(), key=lambda kv: -kv[1]):
    print(f"  {count:4d}  {intent}")
print("\nmessages still falling through to the LLM:")
for line in unresolved[:25]:
    print("  " + line)

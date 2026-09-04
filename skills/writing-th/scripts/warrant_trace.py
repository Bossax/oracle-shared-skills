"""Partial mechanical check: does each approved argument unit's claim show up
in the draft at all?

This is deliberately a weak, cheap check -- token overlap, not meaning. It
catches the case where a unit was silently dropped from verbalization
entirely. It cannot tell you whether the draft faithfully carries a unit's
*warrant* (the reasoning), only whether the unit's subject matter is present
somewhere. Genuine Tier 2 fidelity judgment stays with th-editorial-reviewer.

Usage:
    warrant_trace.py <argument-map.json> <draft.md>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv import reexec_if_needed

reexec_if_needed("pythainlp")
from pythainlp.tokenize import word_tokenize

THAI_OR_LATIN_WORD = re.compile(r"[฀-๿]+|[A-Za-z]{3,}")
STOPWORDS = {
    "การ", "ความ", "และ", "ของ", "ใน", "ที่", "เป็น", "ให้", "ได้", "จะ",
    "มี", "ไม่", "ต่อ", "กับ", "จาก", "นี้", "นั้น", "ซึ่ง", "โดย", "ด้วย",
    "แต่", "หรือ", "ก็", "ว่า", "อยู่", "ทั้ง", "แล้ว", "อีก", "คือ",
}


def content_terms(text: str) -> set[str]:
    tokens = word_tokenize(text, engine="newmm")
    return {t for t in tokens if t not in STOPWORDS and THAI_OR_LATIN_WORD.fullmatch(t)}


def load_json(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def trace(map_path: str, draft_path: str) -> tuple[bool, list[str]]:
    data = load_json(map_path)
    draft_text = Path(draft_path).read_text(encoding="utf-8")
    draft_terms = content_terms(draft_text)

    units = data.get("argument_units", [])
    if not units:
        return False, ["argument-map.json has no argument_units -- nothing to trace"]

    findings = []
    missing = 0
    for unit in units:
        unit_id = unit.get("unit_id", "?")
        claim = unit.get("claim", "")
        terms = content_terms(claim)
        if not terms:
            findings.append(f"  {unit_id}: claim has no traceable content terms -- skipped")
            continue
        hits = terms & draft_terms
        coverage = len(hits) / len(terms)
        if coverage == 0:
            missing += 1
            findings.append(f"  {unit_id}: NOT FOUND -- no claim terms appear in the draft "
                             f"({sorted(terms)[:5]}...)")
        elif coverage < 0.34:
            findings.append(f"  {unit_id}: WEAK ({coverage:.0%} term overlap) -- "
                             f"verify by hand, may be paraphrased or dropped")
        else:
            findings.append(f"  {unit_id}: present ({coverage:.0%} term overlap)")

    ok = missing == 0
    return ok, findings


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: warrant_trace.py <argument-map.json> <draft.md>")
        return 2
    map_path, draft_path = sys.argv[1], sys.argv[2]
    try:
        ok, findings = trace(map_path, draft_path)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"REFUSED: {err}")
        return 1

    print(f"warrant_trace: {map_path} -> {draft_path}")
    for line in findings:
        print(line)

    if ok:
        print("\nAll argument units have some term presence in the draft. "
              "This is a coverage floor, not a fidelity judgment -- "
              "the Stage 5 reviewer still has to read it.")
        return 0
    print("\nWARRANT TRACE FAILED -- at least one argument unit's claim has "
          "zero term overlap with the draft. Either it was dropped, or the "
          "verbalization used entirely different vocabulary worth a manual check.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

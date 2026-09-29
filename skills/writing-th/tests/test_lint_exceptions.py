"""Per-entry `exceptions` on literal lexicon rules: masking and validation."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from _venv import child_python
from lint_thai_writing import find_literal, token_boundaries


def hits(text, needle, exceptions=()):
    return find_literal(text, needle, token_boundaries(text), exceptions)


def validate(entry):
    lex = {"context": "TEST", "version": "0", "lexicon": [entry]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as fh:
        json.dump(lex, fh, ensure_ascii=False)
    try:
        return subprocess.run([child_python(), str(SCRIPTS / "validate_lexicon.py"), fh.name],
                              capture_output=True, text=True, encoding="utf-8").returncode
    finally:
        Path(fh.name).unlink(missing_ok=True)


def main():
    base = {"banned": "ฉบับ", "preferred": "รายการ", "reason": "t", "kind": "literal", "scope": "report"}
    checks = [
        ("no exceptions: classifier use fires", hits("ส่งมอบรายงาน 4 ฉบับ", "ฉบับ") != []),
        ("no exceptions: name use fires", hits("รายงานฉบับกลาง", "ฉบับ") != []),
        ("exception masks name use", hits("รายงานฉบับกลาง", "ฉบับ", ["รายงานฉบับกลาง"]) == []),
        ("exception leaves real violation",
         len(hits("รายงานฉบับกลาง และเอกสาร 4 ฉบับ", "ฉบับ", ["รายงานฉบับกลาง"])) == 1),
        ("latin literal honours exceptions", hits("the DCCE Act", "DCCE", ["DCCE Act"]) == []),
        ("validator accepts good exceptions", validate({**base, "exceptions": ["ฉบับที่"]}) == 0),
        ("validator rejects exception without banned term", validate({**base, "exceptions": ["กลาง"]}) == 1),
        ("validator rejects non-list", validate({**base, "exceptions": "ฉบับที่"}) == 1),
        ("validator rejects exceptions on regex",
         validate({**base, "kind": "regex", "pattern": "ฉบับ", "exceptions": ["ฉบับที่"]}) == 1),
    ]
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    print(f"lint exceptions: {len(checks) - len(failed)}/{len(checks)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

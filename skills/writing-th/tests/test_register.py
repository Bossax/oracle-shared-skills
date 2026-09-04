"""Regression tests for register.py's rationale-gate status column (2026-08-30).

Covers the three things the migration/gate must get right:
  1. Legacy rows (pre-existing before the `status` column) are grandfathered
     in and still reach `ready` under the old count-only threshold.
  2. `mechanical` reaches `ready` on the first sighting, bypassing the 2x wait.
  3. `one_off` / `content_correction` never reach `ready`, regardless of count.

Every subprocess call points WRITING_TH_REGISTER at a throwaway temp file --
never the real ψ/memory/style/miss_register.db.
"""
from __future__ import annotations

import os
import subprocess
import sqlite3
import sys
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
from _venv import child_python

REGISTER = SCRIPTS / "register.py"


def run(db_path, *args):
    env = dict(os.environ)
    env["WRITING_TH_REGISTER"] = str(db_path)
    proc = subprocess.run(
        [child_python(), str(REGISTER), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return proc.returncode, proc.stdout + proc.stderr


def expect(condition, message, failures):
    if not condition:
        failures.append(message)


def test_legacy_backfill(failures):
    """Rows present before the status column existed become 'legacy' and
    still reach `ready` at the old 2x threshold -- nothing near promotion
    should silently stall when this migration lands on a real, populated db."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "register.db"
        con = sqlite3.connect(db)
        con.execute("""CREATE TABLE candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, pattern TEXT NOT NULL,
            source TEXT, fix TEXT, note TEXT, layer TEXT DEFAULT 'lexical')""")
        con.execute("CREATE TABLE promotions (pattern TEXT PRIMARY KEY, ts TEXT NOT NULL, layer TEXT DEFAULT 'lexical')")
        con.execute("CREATE TABLE runs (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, draft TEXT, lexicon TEXT, scope TEXT, tokens INTEGER, sentences INTEGER, verdict TEXT)")
        con.execute("CREATE TABLE misses (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, rule TEXT, kind TEXT)")
        # pre-existing candidate, seen twice, no `status` column yet -- simulates a real db before this migration
        con.execute("INSERT INTO candidates (ts, pattern, source, layer) VALUES ('2026-01-01T00:00:00', 'old-pattern', 'legacy-file.md', 'lexical')")
        con.execute("INSERT INTO candidates (ts, pattern, source, layer) VALUES ('2026-01-02T00:00:00', 'old-pattern', 'legacy-file2.md', 'lexical')")
        con.commit()
        con.close()

        code, out = run(db, "ready")
        expect(code == 0, f"ready exited {code} on legacy db: {out}", failures)
        expect("old-pattern" in out, f"legacy pattern did not reach ready: {out}", failures)
        expect("[legacy]" in out, f"legacy pattern not tagged as legacy status: {out}", failures)


def test_mechanical_bypasses_threshold(failures):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "register.db"
        run(db, "init")
        code, out = run(db, "observe", "สินทรัพย์->ทรัพย์สิน", "--status", "mechanical", "--source", "test")
        expect(code == 0, f"observe exited {code}: {out}", failures)
        expect("AT THRESHOLD" in out, f"mechanical pattern did not hit threshold on first sighting: {out}", failures)

        code, out = run(db, "ready")
        expect("สินทรัพย์->ทรัพย์สิน" in out, f"mechanical pattern not in ready after 1 sighting: {out}", failures)
        expect("bypassed 2x threshold" in out, f"ready output missing bypass note: {out}", failures)


def test_unconfirmed_blocked_until_confirm(failures):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "register.db"
        run(db, "init")
        run(db, "observe", "judgment-call-pattern", "--source", "test")
        run(db, "observe", "judgment-call-pattern", "--source", "test2")  # 2x, but unconfirmed

        code, out = run(db, "ready")
        expect("judgment-call-pattern" not in out, f"unconfirmed pattern reached ready at 2x without confirm: {out}", failures)

        run(db, "confirm", "judgment-call-pattern", "--status", "confirmed_generalizable")
        code, out = run(db, "ready")
        expect("judgment-call-pattern" in out, f"confirmed_generalizable pattern did not reach ready after confirm: {out}", failures)


def test_one_off_never_reaches_ready(failures):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "register.db"
        run(db, "init")
        for i in range(5):  # well past any threshold
            run(db, "observe", "domain-fact-pattern", "--source", f"test{i}")
        run(db, "confirm", "domain-fact-pattern", "--status", "one_off")

        code, out = run(db, "ready", "--threshold", "1")
        expect("domain-fact-pattern" not in out, f"one_off pattern reached ready despite confirm: {out}", failures)


def test_content_correction_never_reaches_ready(failures):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "register.db"
        run(db, "init")
        run(db, "observe", "factual-fix-pattern", "--source", "test")
        run(db, "observe", "factual-fix-pattern", "--source", "test2")
        run(db, "confirm", "factual-fix-pattern", "--status", "content_correction")

        code, out = run(db, "ready")
        expect("factual-fix-pattern" not in out, f"content_correction pattern reached ready: {out}", failures)


def test_confirm_unknown_pattern_fails_cleanly(failures):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "register.db"
        run(db, "init")
        code, out = run(db, "confirm", "never-observed", "--status", "mechanical")
        expect(code != 0, f"confirm on unknown pattern should fail, got exit {code}: {out}", failures)


def main():
    failures = []
    test_legacy_backfill(failures)
    test_mechanical_bypasses_threshold(failures)
    test_unconfirmed_blocked_until_confirm(failures)
    test_one_off_never_reaches_ready(failures)
    test_content_correction_never_reaches_ready(failures)
    test_confirm_unknown_pattern_fails_cleanly(failures)

    if failures:
        print(f"FAILED: {len(failures)} register.py case(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASSED: 6 register.py rationale-gate scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())

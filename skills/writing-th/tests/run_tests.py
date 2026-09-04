"""Regression suite for the writing-th gates. No pytest dependency.

Each fixture is written to a temp file and run through the real linter, so the
suite exercises the same code path a draft does.

Usage:
    run_tests.py [--lexicon <path>] [-v]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from _venv import child_python

DEFAULT_LEXICON = TESTS.parents[3] / "ψ" / "memory" / "style" / "LEXICON_TH.json"


def run_case(case, lexicon, verbose):
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as fh:
        fh.write(case["text"])
        path = fh.name

    # fixtures must never write into the real miss register
    env = dict(os.environ)
    env["WRITING_TH_REGISTER"] = str(Path(tempfile.gettempdir()) / "writing_th_test_register.db")

    try:
        proc = subprocess.run(
            [child_python(), str(SCRIPTS / "lint_thai_writing.py"), path, str(lexicon)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    finally:
        Path(path).unlink(missing_ok=True)

    if proc.returncode == 2:
        return "ERROR", proc.stdout + proc.stderr

    actual = "pass" if proc.returncode == 0 else "fail"
    review_ok = not case.get("expect_review") or case["expect_review"] in (proc.stdout or "")
    ok = actual == case["expect"] and review_ok
    detail = ""
    if not ok or verbose:
        detail = "\n".join(
            l for l in (proc.stdout or "").splitlines()
            if l.strip().startswith("-")
            or "MECHANICAL GATE" in l
            or "[ARTIFACT]" in l
            or "[META]" in l)
        if not review_ok:
            detail += f"\nmissing expected review marker: {case['expect_review']}"
    return ("OK" if ok else "FAIL"), detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lexicon", default=str(DEFAULT_LEXICON))
    ap.add_argument("-v", "--verbose", action="store_true")
    ns = ap.parse_args()

    lexicon = Path(ns.lexicon)
    if not lexicon.exists():
        print(f"ERROR: lexicon not found at {lexicon}")
        sys.exit(2)

    data = json.loads((TESTS / "fixtures.json").read_text(encoding="utf-8"))
    cases = data["cases"]

    print(f"lexicon: {lexicon.name}")
    print(f"cases  : {len(cases)}\n")

    failed, errored = [], []
    for c in cases:
        status, detail = run_case(c, lexicon, ns.verbose)
        mark = {"OK": "ok  ", "FAIL": "FAIL", "ERROR": "ERR "}[status]
        note = f"   [{c['defect']}]" if c.get("defect") else ""
        print(f"  {mark}  expect {c['expect']:4}  {c['name']}{note}")
        if detail:
            for line in detail.splitlines():
                print(f"          {line}")
        if status == "FAIL":
            failed.append(c["name"])
        elif status == "ERROR":
            errored.append(c["name"])

    print()
    if errored:
        print(f"ERRORED: {len(errored)} case(s) could not run -- {errored}")
        sys.exit(2)
    if failed:
        print(f"FAILED: {len(failed)}/{len(cases)} -- {failed}")
        sys.exit(1)
    print(f"PASSED: {len(cases)}/{len(cases)} mechanical cases")

    harness = subprocess.run(
        [child_python(), str(TESTS / "test_editorial_gate.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if harness.stdout:
        print(harness.stdout.rstrip())
    if harness.stderr:
        print(harness.stderr.rstrip())
    if harness.returncode:
        sys.exit(harness.returncode)

    argument_harness = subprocess.run(
        [child_python(), str(TESTS / "test_argument_gate.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if argument_harness.stdout:
        print(argument_harness.stdout.rstrip())
    if argument_harness.stderr:
        print(argument_harness.stderr.rstrip())
    if argument_harness.returncode:
        sys.exit(argument_harness.returncode)

    subagent_harness = subprocess.run(
        [child_python(), str(TESTS / "test_subagent_specs.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if subagent_harness.stdout:
        print(subagent_harness.stdout.rstrip())
    if subagent_harness.stderr:
        print(subagent_harness.stderr.rstrip())
    if subagent_harness.returncode:
        sys.exit(subagent_harness.returncode)

    register_harness = subprocess.run(
        [child_python(), str(TESTS / "test_register.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if register_harness.stdout:
        print(register_harness.stdout.rstrip())
    if register_harness.stderr:
        print(register_harness.stderr.rstrip())
    sys.exit(register_harness.returncode)


if __name__ == "__main__":
    main()


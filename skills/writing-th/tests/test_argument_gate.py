"""Regression tests for argument_gate.py -- the v6.1 argument-map validator."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from argument_gate import validate_map


def payload(claim="pc", facts=None, mechanism="pm", consequence="pcq"):
    return {
        "claim": claim,
        "key_facts": facts if facts is not None else ["f1"],
        "mechanism": mechanism,
        "consequence": consequence,
    }


def base_map():
    return {
        "schema_version": "1.1",
        "section_id": "test",
        "governing_thought": "X causes Y and requires Z",
        "narrative_scqa": {"situation": "s", "complication": "c", "question": "q", "answer": "a"},
        "governing_thought_components": ["X causes Y", "requires Z"],
        "argument_units": [
            {"unit_id": "arg-01", "order": 1, "paragraph_job": "diagnose",
             "claim": "c1", "grounds": "g1", "warrant": "w1",
             "application_to_design": "a1", "verbalization_payload": payload(),
             "supports": "X causes Y"},
            {"unit_id": "arg-02", "order": 2, "paragraph_job": "conclude",
             "claim": "c2", "grounds": "g2", "warrant": "w2",
             "application_to_design": "a2", "verbalization_payload": payload(),
             "supports": "requires Z"},
        ],
        "approval": {"status": "pending", "approved_by": "", "approved_at": ""},
    }


def expect(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []

    ok_map = base_map()
    errors, advisories = validate_map(ok_map)
    expect(not errors, f"well-formed map rejected: {errors}", failures)
    expect(not advisories, f"well-formed map raised advisories: {advisories}", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["warrant"] = ""
    errors, _ = validate_map(d)
    expect(any("warrant must be a non-empty string" in e for e in errors),
           "empty warrant was not caught", failures)

    d = copy.deepcopy(base_map())
    del d["argument_units"][0]["application_to_design"]
    errors, _ = validate_map(d)
    expect(any("missing key(s)" in e and "application_to_design" in e for e in errors),
           "missing application_to_design key was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][1]["unit_id"] = "arg-01"
    errors, _ = validate_map(d)
    expect(any("duplicate unit_id" in e for e in errors),
           "duplicate unit_id was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["paragraph_job"] = "mandate"
    errors, _ = validate_map(d)
    expect(any("paragraph_job" in e and "not in" in e for e in errors),
           "paragraph_job outside enum was not caught", failures)

    d = copy.deepcopy(base_map())
    d["governing_thought_components"] = ["X causes Y", "requires Z", "uncovered part"]
    errors, _ = validate_map(d)
    expect(any("MECE coverage is incomplete" in e for e in errors),
           "incomplete MECE coverage was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][1]["order"] = 1
    errors, _ = validate_map(d)
    expect(any("duplicate order" in e for e in errors),
           "duplicate order was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["supports"] = "not a real component"
    errors, _ = validate_map(d)
    expect(any("does not match any entry in governing_thought_components" in e for e in errors),
           "supports value outside governing_thought_components was not caught", failures)

    # -- v1.1 verbalization_payload cases --

    d = copy.deepcopy(base_map())
    d["schema_version"] = "1.0"
    errors, _ = validate_map(d)
    expect(any("schema_version must be 1.1" in e for e in errors),
           "old schema_version 1.0 was not rejected", failures)

    d = copy.deepcopy(base_map())
    del d["argument_units"][0]["verbalization_payload"]
    errors, _ = validate_map(d)
    expect(any("missing key(s)" in e and "verbalization_payload" in e for e in errors),
           "missing verbalization_payload key was not caught", failures)

    for key in ("claim", "mechanism", "consequence"):
        d = copy.deepcopy(base_map())
        d["argument_units"][0]["verbalization_payload"][key] = ""
        errors, _ = validate_map(d)
        expect(any(f"verbalization_payload.{key} must be a non-empty string" in e for e in errors),
               f"empty verbalization_payload.{key} was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["verbalization_payload"]["key_facts"] = []
    errors, _ = validate_map(d)
    expect(any("key_facts must be a non-empty list" in e for e in errors),
           "empty key_facts was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["verbalization_payload"]["key_facts"] = ["f1", "f2", "f3", "f4"]
    errors, _ = validate_map(d)
    expect(any("key_facts has 4 entries" in e and "capped at 3" in e for e in errors),
           "key_facts exceeding the cap of 3 was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["verbalization_payload"]["key_facts"] = ["f1", ""]
    errors, _ = validate_map(d)
    expect(any("key_facts[1] must be a non-empty string" in e for e in errors),
           "empty key_facts entry was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["verbalization_payload"] = "just a string, not an object"
    errors, _ = validate_map(d)
    expect(any("verbalization_payload must be an object" in e for e in errors),
           "non-object verbalization_payload was not caught", failures)

    d = copy.deepcopy(base_map())
    d["argument_units"][0]["verbalization_payload"]["consequence"] = "x" * 601
    errors, advisories = validate_map(d)
    expect(not errors, f"oversized (but valid) payload field was rejected as an error: {errors}", failures)
    expect(any("verbalization_payload.consequence is 601 characters" in a for a in advisories),
           "oversized verbalization_payload field did not raise an advisory", failures)

    if failures:
        print(f"FAILED: {len(failures)} argument-gate case(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASSED: 16 argument-gate scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())

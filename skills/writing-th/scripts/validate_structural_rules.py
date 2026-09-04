"""Validate structural rules JSON before it is consumed by argument mapper.

Usage:
    validate_structural_rules.py <structural_rules.json>
"""
import json
import sys
from pathlib import Path

REQUIRED_KEYS = ("id", "name", "scope", "section_job", "trigger_condition", "mandatory_structure", "counter_pattern")
ALLOWED_JOBS = {"intro_scope", "compare", "diagnose", "define", "conclude", "mandate"}
ALLOWED_SCOPES = {"executive_summary", "literature_review", "system_design", "architecture_overview", "universal", "report"}


def validate(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors, warnings = [], []

    for key in ("context", "version", "rules"):
        if key not in data:
            errors.append(f"missing top-level key: {key}")
    if errors:
        report(errors, warnings)

    seen_ids = set()
    for i, r in enumerate(data.get("rules", [])):
        tag = f"[{i}] {r.get('id', 'MISSING_ID')}"
        
        missing = [k for k in REQUIRED_KEYS if k not in r]
        if missing:
            errors.append(f"{tag}: missing key(s) {missing}")
            continue

        rid = r["id"]
        if rid in seen_ids:
            errors.append(f"{tag}: duplicate rule id {rid}")
        seen_ids.add(rid)

        if r["section_job"] not in ALLOWED_JOBS:
            errors.append(f"{tag}: section_job {r['section_job']!r} not in {sorted(ALLOWED_JOBS)}")
        if r["scope"] not in ALLOWED_SCOPES:
            errors.append(f"{tag}: scope {r['scope']!r} not in {sorted(ALLOWED_SCOPES)}")
        if not isinstance(r.get("mandatory_structure"), dict):
            errors.append(f"{tag}: mandatory_structure must be a dict")

    report(errors, warnings, data)


def report(errors, warnings, data=None):
    if warnings:
        print(f"{len(warnings)} warning(s):", file=sys.stderr)
        for w in warnings:
            print(f"  warn: {w}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if data:
        n = len(data.get("rules", []))
        print(f"rules   : {n} valid structural rules")
    print("PASSED")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_structural_rules.py <structural_rules.json>")
        sys.exit(1)
    validate(sys.argv[1])

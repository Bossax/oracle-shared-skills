"""Validate and scaffold argument-map.json, writing-th v6.0's missing artifact.

This is the stage v5.0 never had: a logical spine, approved by a human,
that must exist before a single Thai sentence is drafted. The script checks
structure -- MECE coverage, warrant presence, unit-id uniqueness -- it does
not judge whether the reasoning is actually good. That judgment belongs to
the human at the Stage 2 gate and to th-editorial-reviewer at Stage 5.

Usage:
    argument_gate.py prepare <contract> --out <map> [--force]
    argument_gate.py validate <map>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA_VERSION = "1.0"
PARAGRAPH_JOBS = {"define", "diagnose", "compare", "conclude"}

UNIT_REQUIRED = (
    "unit_id",
    "order",
    "paragraph_job",
    "claim",
    "grounds",
    "warrant",
    "application_to_design",
    "supports",
)


def load_json(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return data


def validate_map(data: dict) -> list[str]:
    errors = []

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    governing_thought = data.get("governing_thought")
    if not isinstance(governing_thought, str) or not governing_thought.strip():
        errors.append("governing_thought must be a non-empty string")

    scqa = data.get("narrative_scqa")
    if not isinstance(scqa, dict):
        errors.append("narrative_scqa must be an object")
        scqa = {}
    for key in ("situation", "complication", "question", "answer"):
        if not isinstance(scqa.get(key), str) or not scqa[key].strip():
            errors.append(f"narrative_scqa.{key} must be a non-empty string")

    components = data.get("governing_thought_components")
    if not isinstance(components, list) or not components:
        errors.append("governing_thought_components must be a non-empty list -- "
                       "this is what argument_units.supports is checked against for MECE coverage")
        components = []
    component_set = set(components)
    if len(component_set) != len(components):
        errors.append("governing_thought_components has duplicate entries")

    units = data.get("argument_units")
    if not isinstance(units, list) or not units:
        errors.append("argument_units must be a non-empty list")
        units = []

    seen_ids: dict[str, int] = {}
    seen_orders: dict[int, int] = {}
    covered = set()
    for i, unit in enumerate(units):
        tag = f"argument_units[{i}]"
        if not isinstance(unit, dict):
            errors.append(f"{tag} must be an object")
            continue

        missing = [k for k in UNIT_REQUIRED if k not in unit]
        if missing:
            errors.append(f"{tag}: missing key(s) {missing}")
            continue

        for key in ("claim", "grounds", "warrant", "application_to_design"):
            if not isinstance(unit[key], str) or not unit[key].strip():
                errors.append(f"{tag}.{key} must be a non-empty string")

        unit_id = unit["unit_id"]
        if not isinstance(unit_id, str) or not unit_id.strip():
            errors.append(f"{tag}.unit_id must be a non-empty string")
        elif unit_id in seen_ids:
            errors.append(f"{tag}: duplicate unit_id {unit_id!r} (also at [{seen_ids[unit_id]}])")
        else:
            seen_ids[unit_id] = i

        order = unit["order"]
        if not isinstance(order, int):
            errors.append(f"{tag}.order must be an integer")
        elif order in seen_orders:
            errors.append(f"{tag}: duplicate order {order} (also at [{seen_orders[order]}])")
        else:
            seen_orders[order] = i

        job = unit["paragraph_job"]
        if job not in PARAGRAPH_JOBS:
            errors.append(f"{tag}.paragraph_job {job!r} not in {sorted(PARAGRAPH_JOBS)}")

        supports = unit["supports"]
        if not isinstance(supports, str) or not supports.strip():
            errors.append(f"{tag}.supports must be a non-empty string")
        elif component_set and supports not in component_set:
            errors.append(
                f"{tag}.supports {supports!r} does not match any entry in "
                f"governing_thought_components -- every unit must support a named part "
                f"of the governing thought"
            )
        else:
            covered.add(supports)

    uncovered = component_set - covered
    if uncovered:
        errors.append(
            f"governing_thought_components not supported by any unit: {sorted(uncovered)} -- "
            f"MECE coverage is incomplete"
        )

    return errors


def command_validate(ns: argparse.Namespace) -> int:
    try:
        data = load_json(ns.map)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"REFUSED: {err}")
        return 1
    errors = validate_map(data)
    if errors:
        print(f"ARGUMENT GATE FAILED -- {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"ARGUMENT GATE PASSED ({len(data.get('argument_units', []))} unit(s))")
    return 0


def scaffold(contract_path: str) -> dict:
    contract = load_json(contract_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "section_id": contract.get("profile", "") + "-" + Path(contract_path).parent.name,
        "governing_thought": "",
        "narrative_scqa": {"situation": "", "complication": "", "question": "", "answer": ""},
        "governing_thought_components": [],
        "argument_units": [],
        "approval": {"status": "pending", "approved_by": "", "approved_at": ""},
    }


def command_prepare(ns: argparse.Namespace) -> int:
    output = Path(ns.out)
    if output.exists() and not ns.force:
        print(f"REFUSED: {output} already exists; use --force to replace the scaffold")
        return 1
    try:
        data = scaffold(ns.contract)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"REFUSED: {err}")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ARGUMENT MAP SCAFFOLD CREATED: {output}")
    print("Fill governing_thought, narrative_scqa, governing_thought_components, and argument_units.")
    print("approval.status stays 'pending' until the Stage 2 human gate approves it -- "
          "the draft-write hook blocks on that field.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("contract")
    prepare.add_argument("--out", required=True)
    prepare.add_argument("--force", action="store_true")
    prepare.set_defaults(fn=command_prepare)

    validate = sub.add_parser("validate")
    validate.add_argument("map")
    validate.set_defaults(fn=command_validate)

    ns = parser.parse_args()
    return ns.fn(ns)


if __name__ == "__main__":
    sys.exit(main())

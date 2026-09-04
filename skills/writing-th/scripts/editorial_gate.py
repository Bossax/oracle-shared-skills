"""Prepare and verify hash-bound editorial review receipts.

The script validates artifacts; it does not pretend to judge prose. A reviewer
must complete the rubric after reading the exact draft and approved contract.

Usage:
    editorial_gate.py prepare <draft> <contract> --out <review>
        [--reviewer-mode independent|self] [--force]
    editorial_gate.py verify <draft> <contract> <review>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
RUBRIC_VERSION = "6.0.0"
LEGACY_RUBRIC_VERSIONS = {"5.0.0"}  # pre-v6.0 receipts, e.g. the 12 merged
                                     # crdb-exec-summary-* reviews -- accepted
                                     # read-only so verify does not retroactively
                                     # break receipts written before argument-map
                                     # gating existed.
PROFILES = {"executive-summary", "report", "article", "letter"}
MODES = {"rewrite", "synthesis", "new"}
CORE_DIMENSIONS = (
    "section_job",
    "audience_decision_value",
    "evidence_payload",
    "causal_logic",
    "argument_fidelity",
    "reader_facing_appropriateness",
    "terminology_agency",
    "source_fidelity",
    "form_readability",
)
LEGACY_CORE_DIMENSIONS = tuple(d for d in CORE_DIMENSIONS if d != "argument_fidelity")
PROFILE_DIMENSIONS = {
    "executive-summary": ("altitude", "headline_conclusion", "findings_over_process"),
    "report": (),
    "article": (),
    "letter": (),
}
CONTRACT_KEYS = (
    "schema_version",
    "profile",
    "transformation_mode",
    "audience",
    "decision_use",
    "section_job",
    "target_altitude",
    "inclusions",
    "exclusions",
    "evidence_policy",
    "required_concepts",
    "terminology",
    "required_structures",
    "source_paths",
    "reference_samples",
    "approval",
)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return data


def validate_contract(contract: dict) -> list[str]:
    errors = []
    missing = [key for key in CONTRACT_KEYS if key not in contract]
    if missing:
        errors.append(f"contract missing key(s): {missing}")
        return errors

    if contract["schema_version"] != SCHEMA_VERSION:
        errors.append(f"contract schema_version must be {SCHEMA_VERSION}")
    if contract["profile"] not in PROFILES:
        errors.append(f"contract profile must be one of {sorted(PROFILES)}")
    if contract["transformation_mode"] not in MODES:
        errors.append(f"transformation_mode must be one of {sorted(MODES)}")

    for key in ("audience", "decision_use", "section_job", "target_altitude", "evidence_policy"):
        if not isinstance(contract[key], str) or not contract[key].strip():
            errors.append(f"contract {key} must be a non-empty string")
    for key in (
        "inclusions",
        "exclusions",
        "required_concepts",
        "required_structures",
        "source_paths",
        "reference_samples",
    ):
        if not isinstance(contract[key], list):
            errors.append(f"contract {key} must be a list")
    if not isinstance(contract["terminology"], dict):
        errors.append("contract terminology must be an object")

    approval = contract["approval"]
    if not isinstance(approval, dict):
        errors.append("contract approval must be an object")
    else:
        if approval.get("status") != "approved":
            errors.append("contract approval.status must be 'approved'")
        for key in ("approved_by", "approved_at"):
            if not isinstance(approval.get(key), str) or not approval[key].strip():
                errors.append(f"contract approval.{key} must be a non-empty string")

    if contract["transformation_mode"] == "rewrite" and not contract["source_paths"]:
        errors.append("rewrite mode requires at least one source_paths entry")
    return errors


def required_dimensions(profile: str, rubric_version: str = RUBRIC_VERSION) -> tuple[str, ...]:
    core = LEGACY_CORE_DIMENSIONS if rubric_version in LEGACY_RUBRIC_VERSIONS else CORE_DIMENSIONS
    return core + PROFILE_DIMENSIONS.get(profile, ())


def scaffold(draft_path: str, contract_path: str, reviewer_mode: str) -> dict:
    contract = load_json(contract_path)
    errors = validate_contract(contract)
    if errors:
        raise ValueError("; ".join(errors))
    assurance = "standard" if reviewer_mode == "independent" else "degraded"
    return {
        "schema_version": SCHEMA_VERSION,
        "rubric_version": RUBRIC_VERSION,
        "draft_sha256": sha256_file(draft_path),
        "contract_sha256": sha256_file(contract_path),
        "profile": contract["profile"],
        "reviewer_mode": reviewer_mode,
        "assurance": assurance,
        "reviewer": "",
        "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dimensions": {
            key: {"verdict": "pending", "evidence": ""}
            for key in required_dimensions(contract["profile"])
        },
        "findings": [],
        "mechanical_reviews": [],
        "verdict": "fail",
    }


def verify_review(
    draft_path: str | Path,
    contract_path: str | Path,
    review_path: str | Path,
    mechanical_reviews: list[str] | None = None,
) -> tuple[bool, dict, list[str], list[str]]:
    errors, warnings = [], []
    try:
        contract = load_json(contract_path)
        review = load_json(review_path)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        return False, {}, [str(err)], warnings

    errors.extend(validate_contract(contract))
    if review.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"review schema_version must be {SCHEMA_VERSION}")
    review_rubric_version = review.get("rubric_version")
    allowed_rubric_versions = {RUBRIC_VERSION} | LEGACY_RUBRIC_VERSIONS
    if review_rubric_version not in allowed_rubric_versions:
        errors.append(f"review rubric_version must be one of {sorted(allowed_rubric_versions)}")
    try:
        current_draft_hash = sha256_file(draft_path)
        current_contract_hash = sha256_file(contract_path)
    except OSError as err:
        return False, review, errors + [str(err)], warnings
    if review.get("draft_sha256") != current_draft_hash:
        errors.append("review draft_sha256 does not match the current draft")
    if review.get("contract_sha256") != current_contract_hash:
        errors.append("review contract_sha256 does not match the current contract")
    if review.get("profile") != contract.get("profile"):
        errors.append("review profile does not match the contract")

    mode = review.get("reviewer_mode")
    assurance = review.get("assurance")
    expected_assurance = {"independent": "standard", "self": "degraded"}.get(mode)
    if expected_assurance is None:
        errors.append("reviewer_mode must be 'independent' or 'self'")
    elif assurance != expected_assurance:
        errors.append(f"{mode} review must use assurance '{expected_assurance}'")
    if mode == "self":
        warnings.append("DEGRADED ASSURANCE: semantic review was performed by the drafting agent")

    for key in ("reviewer", "reviewed_at"):
        if not isinstance(review.get(key), str) or not review[key].strip():
            errors.append(f"review {key} must be a non-empty string")

    dimensions = review.get("dimensions")
    if not isinstance(dimensions, dict):
        errors.append("review dimensions must be an object")
        dimensions = {}
    for name in required_dimensions(contract.get("profile", ""), review_rubric_version or RUBRIC_VERSION):
        entry = dimensions.get(name)
        if not isinstance(entry, dict):
            errors.append(f"missing review dimension: {name}")
            continue
        verdict = entry.get("verdict")
        evidence = entry.get("evidence")
        allow_na = name == "source_fidelity" and contract.get("transformation_mode") == "new"
        if verdict != "pass" and not (allow_na and verdict == "not_applicable"):
            errors.append(f"dimension {name} must pass" + (" or be not_applicable" if allow_na else ""))
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"dimension {name} requires concrete evidence")

    findings = review.get("findings")
    if not isinstance(findings, list):
        errors.append("review findings must be a list")
        findings = []
    for index, finding in enumerate(findings):
        tag = f"finding[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{tag} must be an object")
            continue
        severity = finding.get("severity")
        status = finding.get("status")
        if severity not in {"critical", "major", "minor"}:
            errors.append(f"{tag} has invalid severity")
        if status not in {"resolved", "accepted", "unresolved"}:
            errors.append(f"{tag} has invalid status")
        for key in ("location", "issue", "disposition"):
            if not isinstance(finding.get(key), str) or not finding[key].strip():
                errors.append(f"{tag}.{key} must be a non-empty string")
        if severity in {"critical", "major"} and status != "resolved":
            errors.append(f"{tag} {severity} finding must be resolved")

    recorded_reviews = review.get("mechanical_reviews")
    if not isinstance(recorded_reviews, list):
        errors.append("review mechanical_reviews must be a list")
        recorded_reviews = []
    dispositions = {}
    for index, item in enumerate(recorded_reviews):
        if not isinstance(item, dict):
            errors.append(f"mechanical_reviews[{index}] must be an object")
            continue
        message, disposition = item.get("message"), item.get("disposition")
        if not isinstance(message, str) or not message.strip():
            errors.append(f"mechanical_reviews[{index}].message must be non-empty")
        elif not isinstance(disposition, str) or not disposition.strip():
            errors.append(f"mechanical_reviews[{index}] requires a disposition")
        else:
            dispositions[message.strip()] = disposition.strip()
    for message in mechanical_reviews or []:
        if message.strip() not in dispositions:
            errors.append(f"mechanical review lacks disposition: {message.strip()}")

    if review.get("verdict") != "pass":
        errors.append("review verdict must be 'pass'")
    return not errors, review, errors, warnings


def command_prepare(ns: argparse.Namespace) -> int:
    output = Path(ns.out)
    if output.exists() and not ns.force:
        print(f"REFUSED: {output} already exists; use --force to replace the scaffold")
        return 1
    try:
        data = scaffold(ns.draft, ns.contract, ns.reviewer_mode)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"REFUSED: {err}")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"REVIEW SCAFFOLD CREATED: {output}")
    print(f"assurance: {data['assurance']}")
    print("verdict : fail (complete the rubric before verification)")
    return 0


def command_verify(ns: argparse.Namespace) -> int:
    ok, review, errors, warnings = verify_review(ns.draft, ns.contract, ns.review)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if not ok:
        print(f"EDITORIAL GATE FAILED -- {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"EDITORIAL GATE PASSED ({review['assurance']} assurance)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("draft")
    prepare.add_argument("contract")
    prepare.add_argument("--out", required=True)
    prepare.add_argument("--reviewer-mode", choices=("independent", "self"), default="independent")
    prepare.add_argument("--force", action="store_true")
    prepare.set_defaults(fn=command_prepare)

    verify = sub.add_parser("verify")
    verify.add_argument("draft")
    verify.add_argument("contract")
    verify.add_argument("review")
    verify.set_defaults(fn=command_verify)
    ns = parser.parse_args()
    return ns.fn(ns)


if __name__ == "__main__":
    sys.exit(main())

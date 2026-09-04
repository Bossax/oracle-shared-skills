"""Merge a mechanically checked and editorially approved isolated draft.

The gates run HERE, not somewhere upstream that a caller has to remember. The
editorial receipt is bound to the exact draft and content contract by SHA-256.
If any gate fails, the destination is never touched.

Usage:
    merge_draft.py <draft> <dest> --lexicon <path> --contract <path>
        --review <path> [--source <path>]
    merge_draft.py <draft> <dest> --skip-gates
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from _venv import child_python
from editorial_gate import load_json, verify_review

REVIEW_PREFIXES = ("[STRUCTURAL]", "[PARENTHETICAL]", "[ARTIFACT]", "[META]")


def run_gate(name, args):
    """Run a gate script. Returns (passed, combined output)."""
    proc = subprocess.run(
        [child_python(), str(SCRIPTS / name)] + [str(a) for a in args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    for line in out.rstrip().splitlines():
        print(f"    {line}")
    return proc.returncode == 0, out


def review_items(output):
    """Extract the current linter's non-blocking editorial review messages."""
    return [
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith(REVIEW_PREFIXES)
    ]


def merge(
    draft_path,
    dest_path,
    lexicon_path=None,
    contract_path=None,
    review_path=None,
    source_path=None,
    skip_gates=False,
):
    draft = Path(draft_path)
    dest = Path(dest_path)

    if not draft.exists():
        print(f"MERGE REFUSED: draft not found at {draft_path}")
        sys.exit(1)

    if skip_gates:
        print("!" * 66)
        print("!!  WARNING: --skip-gates -- merging WITHOUT validation.")
        print("!!  Mechanical checks and hash-bound editorial review are bypassed.")
        print("!" * 66)
    else:
        missing = [name for name, value in (
            ("--lexicon", lexicon_path),
            ("--contract", contract_path),
            ("--review", review_path),
        ) if not value]
        if missing:
            print(f"MERGE REFUSED: required argument(s) missing: {', '.join(missing)}")
            print("Use --skip-gates only as a deliberate human-authorized override.")
            sys.exit(1)

        try:
            contract = load_json(contract_path)
        except Exception as err:
            print(f"MERGE REFUSED: cannot read contract: {err}")
            sys.exit(1)
        mode = contract.get("transformation_mode")
        if mode == "rewrite" and not source_path:
            print("MERGE REFUSED: rewrite mode requires --source for the size heuristic.")
            sys.exit(1)

        print(f"Gate 1/3  mechanical lint  {draft.name}")
        lint_ok, lint_output = run_gate("lint_thai_writing.py", [draft, lexicon_path])
        if not lint_ok:
            print(f"\nMERGE REFUSED: mechanical gate failed. {dest_path} was NOT modified.")
            sys.exit(1)

        if mode == "rewrite":
            print(f"Gate 2/3  rewrite size heuristic  {draft.name}")
            density_ok, _ = run_gate("check_density.py", [source_path, draft])
            if not density_ok:
                print(f"\nMERGE REFUSED: rewrite size heuristic failed. {dest_path} was NOT modified.")
                sys.exit(1)
        else:
            print(f"Gate 2/3  size heuristic skipped (transformation_mode={mode})")

        print(f"Gate 3/3  hash-bound editorial review  {Path(review_path).name}")
        ok, review, errors, warnings = verify_review(
            draft, contract_path, review_path, mechanical_reviews=review_items(lint_output)
        )
        for warning in warnings:
            print(f"    WARNING: {warning}")
        if not ok:
            for error in errors:
                print(f"    - {error}")
            print(f"\nMERGE REFUSED: editorial gate failed. {dest_path} was NOT modified.")
            sys.exit(1)
        print(f"    EDITORIAL GATE PASSED ({review['assurance']} assurance)")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(draft, dest)

    print("\nMERGE SUCCESSFUL")
    print(f"  source: {draft_path}")
    print(f"  target: {dest_path}")
    print(f"\nThe scratch directory may now be archived: {draft.parent}")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge a gated draft over its target file.")
    parser.add_argument("draft", help="path to the draft in the isolation directory")
    parser.add_argument("dest", help="path to the real target file")
    parser.add_argument("--lexicon", help="lexicon JSON the linter validates against")
    parser.add_argument("--contract", help="approved writing-contract.json")
    parser.add_argument("--review", help="hash-bound editorial-review.json")
    parser.add_argument("--source", help="original source doc, required for rewrite mode")
    parser.add_argument("--skip-gates", action="store_true",
                        help="merge without validating -- deliberate override only")
    ns = parser.parse_args()

    merge(
        ns.draft,
        ns.dest,
        ns.lexicon,
        ns.contract,
        ns.review,
        ns.source,
        ns.skip_gates,
    )

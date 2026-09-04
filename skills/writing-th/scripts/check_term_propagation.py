"""Find files still using a term that was just superseded in the lexicon.

On 2026-08-30, `เมทะดาตา` / `มาตรฐานข้อมูลกำกับ` was superseded by
`ข้อมูลอภิพันธ์` in LEXICON_TH.json and STYLE_PACK_TH.md, but the old term
was still live in five other draft files (section 4.3, 4.4, 3.2, 1.4, 1.1)
and several writing-contract.json/plan-slice.md files. Finding them took an
ad-hoc Grep the agent happened to think to run. This script makes that a
required, scripted step instead: whenever a lexicon entry supersedes a
previously-canonical term, run this against the live draft tree and report
what it finds so the affected files can be surfaced to the user rather than
silently left stale.

This only searches file contents for the literal old term(s) -- it does not
edit anything. Reporting an affected file is not the same as deciding to fix
it; that stays a human/agent judgment call (a draft mid-revision may
legitimately still carry the old term until its own pass).

Usage:
    check_term_propagation.py <old_term> [<old_term> ...] [--dir <path> ...]

Default search directory (if --dir omitted): ψ/incubate/drafts/
"""
import argparse
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def repo_root():
    for parent in SKILL_ROOT.parents:
        if (parent / "AGENTS.md").exists() and (parent / "ψ").is_dir():
            return parent
    return None


def default_dirs():
    root = repo_root()
    if root is None:
        return []
    return [root / "ψ" / "incubate" / "drafts"]


def search(terms, dirs):
    hits = {}  # term -> list of (file, line_no, line_text)
    for term in terms:
        hits[term] = []
    for d in dirs:
        if not d.exists():
            continue
        for path in d.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in (".md", ".json", ".txt"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                for term in terms:
                    if term in line:
                        hits[term].append((path, line_no, line.strip()))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("terms", nargs="+", help="superseded term(s) to search for")
    ap.add_argument("--dir", action="append", dest="dirs", help="directory to search (repeatable)")
    ns = ap.parse_args()

    dirs = [Path(d) for d in ns.dirs] if ns.dirs else default_dirs()
    if not dirs:
        print("could not resolve repo root and no --dir given -- pass --dir explicitly")
        sys.exit(1)

    hits = search(ns.terms, dirs)
    total = sum(len(v) for v in hits.values())

    if total == 0:
        print(f"no remaining usages of {ns.terms} found under {[str(d) for d in dirs]}.")
        sys.exit(0)

    print(f"{total} remaining usage(s) of superseded term(s) found -- surface these to the user:\n")
    for term, rows in hits.items():
        if not rows:
            continue
        files = sorted({str(r[0]) for r in rows})
        print(f"  {term!r} -- {len(rows)} line(s) across {len(files)} file(s):")
        for path, line_no, line in rows:
            snippet = line[:80] + ("..." if len(line) > 80 else "")
            print(f"    {path}:{line_no}  {snippet}")
        print()
    sys.exit(0)


if __name__ == "__main__":
    main()

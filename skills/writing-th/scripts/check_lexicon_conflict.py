"""Check whether a term/concept already has a different canonical mapping.

On 2026-08-30, `เมทะดาตา -> ข้อมูลอภิพันธ์` was added to LEXICON_TH.json's
lexicon array while STYLE_PACK_TH.md's Technical Terminology Mapping still
had `Metadata Standard -> มาตรฐานข้อมูลกำกับ` -- two live Thai mappings for
the same English concept, caught only by chance re-reading the pack header.
validate_lexicon.py checks for exact-duplicate `banned` strings but has no
semantic/near-duplicate check, and the two sources (LEXICON_TH.json's
technical_terms array and STYLE_PACK_TH.md's hand-written prose table) are
not cross-checked against each other at all.

This is a substring/keyword check, not fuzzy ML matching -- it only needs to
catch "the same English concept already has a different existing Thai
mapping somewhere," which is what happened. It cannot catch a conflict where
neither side names the shared English concept in a matching way; treat a
clean report as "no conflict found by this heuristic," not a formal proof.

Usage:
    check_lexicon_conflict.py <term-or-concept> [--lexicon <path>] [--pack <path>]

Exit code 0 always (this is advisory, not a gate) -- it prints what it finds
and leaves the decision to the agent/user.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def repo_root():
    for parent in SKILL_ROOT.parents:
        if (parent / "AGENTS.md").exists() and (parent / "ψ").is_dir():
            return parent
    return None


def default_paths():
    root = repo_root()
    if root is None:
        return None, None
    style_dir = root / "ψ" / "memory" / "style"
    return style_dir / "LEXICON_TH.json", style_dir / "STYLE_PACK_TH.md"


def normalize(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()


def check_lexicon(query, lexicon_path):
    hits = []
    if not lexicon_path or not Path(lexicon_path).exists():
        return hits
    data = json.loads(Path(lexicon_path).read_text(encoding="utf-8"))
    q = normalize(query)

    for e in data.get("lexicon", []):
        banned, preferred = e.get("banned", ""), e.get("preferred", "")
        if q in normalize(banned) or q in normalize(preferred):
            hits.append(("lexicon", banned, preferred, e.get("reason", "")))

    for t in data.get("technical_terms", []):
        term, definition = t.get("term", ""), t.get("definition", "")
        if q in normalize(term) or q in normalize(definition):
            hits.append(("technical_terms", term, definition, ""))

    return hits


def check_pack(query, pack_path):
    hits = []
    if not pack_path or not Path(pack_path).exists():
        return hits
    text = Path(pack_path).read_text(encoding="utf-8")
    q = normalize(query)

    # Technical Terminology Mapping bullets look like:
    #   * **Metadata Standard** -> มาตรฐานข้อมูลกำกับ (Metadata Standard)
    for line in text.splitlines():
        if line.strip().startswith("*") and "->" in line and q in normalize(line):
            hits.append(("STYLE_PACK_TH.md (Technical Terminology Mapping)", line.strip(), "", ""))

    # Lexicon & Diction table rows: | banned | preferred | reason |
    for line in text.splitlines():
        if line.strip().startswith("|") and q in normalize(line) and "Banned/Common" not in line and ":---" not in line:
            hits.append(("STYLE_PACK_TH.md (§5 Lexicon & Diction table)", line.strip(), "", ""))

    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("query", help="term or English concept to check, e.g. 'metadata' or 'เมทะดาตา'")
    ap.add_argument("--lexicon", help="path to LEXICON_<CONTEXT>.json (default: LEXICON_TH.json)")
    ap.add_argument("--pack", help="path to STYLE_PACK_<CONTEXT>.md (default: STYLE_PACK_TH.md)")
    ns = ap.parse_args()

    default_lexicon, default_pack = default_paths()
    lexicon_path = ns.lexicon or default_lexicon
    pack_path = ns.pack or default_pack

    lex_hits = check_lexicon(ns.query, lexicon_path)
    pack_hits = check_pack(ns.query, pack_path)
    all_hits = lex_hits + pack_hits

    if not all_hits:
        print(f"no existing mapping found for {ns.query!r} in {lexicon_path} or {pack_path}.")
        print("(substring heuristic only -- absence here is not proof of no conflict.)")
        sys.exit(0)

    print(f"{len(all_hits)} existing entr(y/ies) touch {ns.query!r} -- check before writing a new mapping:\n")
    for source, a, b, reason in all_hits:
        if b:
            print(f"  [{source}]  {a}  ->  {b}")
        else:
            print(f"  [{source}]  {a}")
        if reason:
            print(f"      reason: {reason}")
    print("\nIf your new entry maps the same concept to a different Thai term, "
          "confirm with the user which one is canonical before writing it -- "
          "do not let both stand.")
    sys.exit(0)


if __name__ == "__main__":
    main()

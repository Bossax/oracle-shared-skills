"""Computed word-level diff table between a draft and its edited version.

style-capture SKILL.md step 4 requires a mandatory "zero-drop" word-by-word
scan of every human edit. On 2026-08-30 that scan was skipped on a live run --
paragraph-level cuts were caught, every word-level swap inside a rewritten
sentence (สินทรัพย์ -> ทรัพย์สิน, งาน -> ภารกิจ, the metadata term change,
etc.) was missed until the user asked "did you capture the lexicon level
styles?" A checklist sentence is not a forcing function; this script is: it
does the mechanical extraction, so the agent's job becomes classifying rows
already on a table instead of noticing changes by re-reading prose.

Two-level diff: lines are aligned first (difflib.SequenceMatcher on the line
list, same idea git diff uses), then within every 'replace' pair of lines,
tokens are diffed with the same PyThaiNLP tokenizer lint_thai_writing.py
uses, so a swap shows up as its own row instead of being buried inside a
full-line replacement.

Usage:
    diff_word_table.py --before <file> --after <file>
    diff_word_table.py --git <path>          # HEAD version vs working copy, for a tracked file
    diff_word_table.py --before-text "..." --after-text "..."   # ad hoc / test use
"""
import argparse
import difflib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv import reexec_if_needed

reexec_if_needed("pythainlp")
from pythainlp.tokenize import word_tokenize

SKILL_ROOT = Path(__file__).resolve().parent.parent


def repo_root():
    for parent in SKILL_ROOT.parents:
        if (parent / "AGENTS.md").exists() and (parent / "ψ").is_dir():
            return parent
    return None


def lines_of(text):
    return text.replace("\r\n", "\n").split("\n")


def tokenize(text):
    return word_tokenize(text, engine="newmm")


def word_diff_rows(before_line, after_line, line_no):
    before_toks = tokenize(before_line)
    after_toks = tokenize(after_line)
    sm = difflib.SequenceMatcher(a=before_toks, b=after_toks, autojunk=False)
    rows = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        removed = "".join(before_toks[i1:i2])
        added = "".join(after_toks[j1:j2])
        rows.append((line_no, tag, removed, added))
    return rows


def diff_word_table(before_text, after_text):
    before_lines = lines_of(before_text)
    after_lines = lines_of(after_text)
    sm = difflib.SequenceMatcher(a=before_lines, b=after_lines, autojunk=False)
    rows = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            for k in range(i1, i2):
                if before_lines[k].strip():
                    rows.append((k + 1, "delete-line", before_lines[k].strip(), ""))
            continue
        if tag == "insert":
            for k in range(j1, j2):
                if after_lines[k].strip():
                    rows.append((k + 1, "insert-line", "", after_lines[k].strip()))
            continue
        # replace: pair up aligned lines 1:1 as far as they go, word-diff each pair
        before_block = before_lines[i1:i2]
        after_block = after_lines[j1:j2]
        pairs = min(len(before_block), len(after_block))
        for k in range(pairs):
            rows.extend(word_diff_rows(before_block[k], after_block[k], i1 + k + 1))
        for k in range(pairs, len(before_block)):
            if before_block[k].strip():
                rows.append((i1 + k + 1, "delete-line", before_block[k].strip(), ""))
        for k in range(pairs, len(after_block)):
            if after_block[k].strip():
                rows.append((j1 + k + 1, "insert-line", "", after_block[k].strip()))
    return rows


def git_before_after(path):
    """Working-copy diff: HEAD version vs the file currently on disk."""
    root = repo_root()
    cwd = str(root) if root else None
    rel = path
    if root:
        try:
            rel = str(Path(path).resolve().relative_to(root)).replace("\\", "/")
        except ValueError:
            rel = path  # already relative, or outside repo_root -- pass through
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    before_text = result.stdout if result.returncode == 0 else ""
    after_text = Path(path).read_text(encoding="utf-8")
    return before_text, after_text


def print_table(rows):
    if not rows:
        print("no word-level differences found")
        return
    print(f"{'line':>5}  {'op':<12}  {'removed':<40}  added")
    print("-" * 100)
    for line_no, tag, removed, added in rows:
        r = removed.replace("\n", " ")[:40]
        a = added.replace("\n", " ")
        print(f"{line_no:>5}  {tag:<12}  {r:<40}  {a}")
    print(f"\n{len(rows)} row(s). Every row must be dispositioned before step 4b "
          f"(lexical category, or explicitly marked 'not lexical -- structural').")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--before")
    ap.add_argument("--after")
    ap.add_argument("--before-text")
    ap.add_argument("--after-text")
    ap.add_argument("--git", help="path to a tracked file; diffs HEAD version vs working copy")
    ns = ap.parse_args()

    if ns.git:
        before_text, after_text = git_before_after(ns.git)
    elif ns.before_text is not None or ns.after_text is not None:
        before_text, after_text = ns.before_text or "", ns.after_text or ""
    elif ns.before and ns.after:
        before_text = Path(ns.before).read_text(encoding="utf-8")
        after_text = Path(ns.after).read_text(encoding="utf-8")
    else:
        ap.error("provide --before/--after, --before-text/--after-text, or --git <path>")
        return

    rows = diff_word_table(before_text, after_text)
    print_table(rows)


if __name__ == "__main__":
    main()

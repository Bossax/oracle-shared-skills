"""Lexicon and structure gate for Thai institutional drafts.

Thai writes without spaces between words, so byte-level substring matching cannot
tell a real term from a fragment. Every match here is checked against real token
boundaries from PyThaiNLP, and every regex rule is scoped to a single sentence.

Rule dispatch follows the lexicon's `kind` field:
    literal    -> exact string, matched at token boundaries (Latin uses word boundaries)
    regex      -> `pattern`, applied per sentence
    structural -> reported for human review, never blocks

Usage:
    lint_thai_writing.py <draft_path> <lexicon_json> [--scope report|article|letter]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv import reexec_if_needed

reexec_if_needed("pythainlp")
from pythainlp.tokenize import word_tokenize, sent_tokenize


def sentences_of(text):
    """Segment into sentences, degrading to whitespace if crfcut is unavailable."""
    try:
        return sent_tokenize(text)
    except Exception:
        return [x for x in text.replace(chr(13), chr(10)).split(chr(10)) if x.strip()]

THAI = re.compile(r"[฀-๿]")
LATIN = re.compile(r"[A-Za-z]")

# Parentheticals the style pack explicitly allows: schema names and official acronyms.
ACRONYM = re.compile(r"[A-Z0-9_]{2,}( +v?[0-9][0-9.]*)?")
ACRONYM_PLURAL = re.compile(r"[A-Z]{2,}s")
VERSION = re.compile(r"v?[0-9][0-9.]*")


# Spans that are not prose and must not be linted: code, link targets, paths, URLs.
# A banned term inside a file path is not a style violation -- that false positive
# is why README.md failed on `[[ψ/incubate/DCCE/CRDB/...]]`.
NON_PROSE = [
    re.compile(r"```.*?```", re.S),          # fenced code
    re.compile(r"`[^`\n]+`"),                 # inline code
    re.compile(r"<!--.*?-->", re.S),          # html comments
    re.compile(r"\[\[([^\]|]+)\|"),           # wiki-link target, keeps the label
    re.compile(r"\]\(([^)\s]+)\)"),           # markdown link target, keeps the text
    re.compile(r"https?://\S+"),              # bare urls
    re.compile(r"(?<![A-Za-z0-9])[\w./\\-]*[/\\][\w./\\-]+"),  # bare file paths
]


def strip_non_prose(text):
    """Blank out non-prose spans, preserving length so offsets stay valid."""
    out = text
    for rx in NON_PROSE:
        def blank(m):
            # if the pattern has a capture group, blank only that group
            if m.groups():
                s, e = m.span(1)
                return m.group(0)[: s - m.start()] + " " * (e - s) + m.group(0)[e - m.start():]
            return " " * len(m.group(0))
        out = rx.sub(blank, out)
    return out


def token_boundaries(text):
    """Character offsets where a token starts or ends."""
    bounds, pos = {0}, 0
    for tok in word_tokenize(text, engine="newmm"):
        pos += len(tok)
        bounds.add(pos)
    return bounds


def find_literal(text, needle, bounds):
    """Occurrences of `needle` that align to token boundaries.

    Latin terms use word boundaries directly -- `DCCE` must not fire inside
    `DCCE_ARCHIVE` or a URL, and the tokenizer is not reliable on Latin runs.
    """
    if LATIN.search(needle) and not THAI.search(needle):
        pattern = r"(?<![A-Za-z0-9])" + re.escape(needle) + r"(?![A-Za-z0-9])"
        return [m.start() for m in re.finditer(pattern, text)]

    hits = []
    for m in re.finditer(re.escape(needle), text):
        if m.start() in bounds and m.end() in bounds:
            hits.append(m.start())
    return hits


def check_parentheticals(text, translations):
    """Latin parentheticals with no known Thai equivalent, raised for review.

    A term the lexicon can translate is already blocked by the literal rule
    wherever it appears, parentheses included -- reporting it here too would
    just say the same thing twice. What is left is the genuinely undecided
    case: technical vocabulary with no settled Thai form. Those pass, and the
    writer is told, rather than the script guessing.
    """
    reviews = []
    for m in re.finditer(r"\(([^)]{1,80})\)", text):
        c = m.group(1).strip()
        if not LATIN.search(c) or THAI.search(c):
            continue
        if ACRONYM.fullmatch(c) or ACRONYM_PLURAL.fullmatch(c) or VERSION.fullmatch(c):
            continue
        if c.casefold() in translations:
            continue  # the lexicon rule already blocks this one
        reviews.append(
            f"[PARENTHETICAL] '({c})' -- no Thai equivalent in the lexicon, so it is allowed. "
            f"If it should have one, add it via /style-capture and it will block next time.")
    return reviews


def check_sentence_structures(sentences):
    """Structural patterns that must be scoped to one sentence, not one paragraph."""
    errors = []
    contrast = re.compile(r"ไม่ได้.{0,60}?แต่|ไม่ใช่.{0,60}?แต่|ไม่ควรถูกมองเป็น.{0,60}?แต่")
    passive = re.compile(r"ถูก(ดำเนินการ|จัดทำ|สร้าง|พัฒนา|มองว่า|ถือว่า|ออกแบบให้)")

    for s in sentences:
        if contrast.search(s):
            errors.append(
                f"[CONTRAST] translated contrast scaffolding in: '{s.strip()[:70]}...' "
                f"State the affirmative directly.")
        m = passive.search(s)
        if m:
            errors.append(
                f"[PASSIVE] '{m.group(0)}' -- name the institutional actor "
                f"(e.g. 'กรมฯ ดำเนินการ...') in: '{s.strip()[:60]}...'")
    return errors


def check_editorial_review_patterns(sentences):
    """Surface semantic-risk patterns for mandatory editorial disposition.

    These are deliberately review items, not blockers: the same surface form can
    be legitimate in an internal plan and wrong in reader-facing prose.
    """
    reviews = []
    roadmap = re.compile(
        r"(ส่วนที่เหลือของ(บท|รายงาน)|"
        r"(หัวข้อ|ส่วน)(ถัดไป|ต่อไป|ที่\s*\d+).{0,80}(กล่าวถึง|นำเสนอ|ครอบคลุม)|"
        r"รายงานฉบับนี้.{0,80}(จัดเรียงเนื้อหา|ประกอบด้วยหัวข้อ))"
    )
    for sentence in sentences:
        clean = sentence.strip()
        if clean.count("→") >= 2:
            reviews.append(
                f"[ARTIFACT] inline arrow chain may be a diagram rendered as prose: "
                f"'{clean[:90]}...'"
            )
        if roadmap.search(clean):
            reviews.append(
                f"[META] possible report-roadmap commentary; state the subject matter instead: "
                f"'{clean[:90]}...'"
            )
    return reviews


def lint(draft_path, lexicon_path, scope="report", register_run=False):
    raw = Path(draft_path).read_text(encoding="utf-8")
    text = strip_non_prose(raw)
    data = json.loads(Path(lexicon_path).read_text(encoding="utf-8"))

    lexicon = data.get("lexicon", [])
    if lexicon and "kind" not in lexicon[0]:
        print(f"ERROR: {lexicon_path} predates the typed schema (no `kind` field).")
        print("       Run validate_lexicon.py -- an untyped lexicon silently drops rules.")
        sys.exit(2)

    active = [e for e in lexicon if e["scope"] in ("universal", scope)]
    skipped = len(lexicon) - len(active)

    bounds = token_boundaries(text)
    sentences = sentences_of(text)

    errors, review, fired = [], [], []
    dormant = 0

    for e in active:
        kind, banned = e["kind"], e["banned"]

        if kind == "literal":
            if find_literal(text, banned, bounds):
                errors.append(
                    f"[LEXICON] '{banned}' -> use '{e['preferred']}'. ({e['reason']})")
                fired.append((banned, "literal"))

        elif kind == "regex":
            rx = re.compile(e["pattern"])
            for s in sentences:
                m = rx.search(s)
                if m:
                    errors.append(
                        f"[PATTERN] {banned}: matched '{m.group(0)[:40]}' "
                        f"-> use '{e['preferred']}'. ({e['reason']})")
                    fired.append((banned, "regex"))
                    break

        elif kind == "structural":
            stem = banned.split("...")[0].split("[")[0].strip()
            if stem and stem in text:
                review.append(f"[STRUCTURAL] '{stem}' present -> consider '{e['preferred']}'. ({e['reason']})")
            else:
                dormant += 1

    translations = {e["banned"].casefold(): e["preferred"]
                    for e in active if e["kind"] == "literal"}

    struct_errs = check_sentence_structures(sentences)
    review += check_parentheticals(text, translations)
    review += check_editorial_review_patterns(sentences)
    errors += struct_errs
    for msg in struct_errs:
        fired.append((msg.split("]")[0].lstrip("[").lower(), "structure"))

    print(f"draft    : {draft_path}")
    print(f"lexicon  : {data.get('context')} v{data.get('version')} "
          f"-- {len(active)} rules active at scope '{scope}', {skipped} out of scope")
    print(f"tokenized: {len(bounds) - 1} tokens, {len(sentences)} sentences")

    if review:
        seen = {}
        for r in review:
            seen[r] = seen.get(r, 0) + 1
        print(f"\n{len(seen)} item(s) for your review (not blocking):")
        for r, n in sorted(seen.items(), key=lambda kv: -kv[1]):
            print(f"  {r}" + (f"   [x{n}]" if n > 1 else ""))
    if dormant:
        print(f"\n{dormant} structural rule(s) not applicable to this draft.")

    verdict = "fail" if errors else "pass"
    if register_run:
        try:
            from register import log_run
            log_run(draft_path, f"{data.get('context')} v{data.get('version')}", scope,
                    len(bounds) - 1, len(sentences), verdict, fired)
        except Exception:
            pass  # a logging failure must never change a gate's verdict

    if errors:
        print(f"\nMECHANICAL GATE FAILED -- {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        print("\nFix these before the draft can merge.")
        sys.exit(1)

    print("\nMECHANICAL GATE PASSED")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lexicon and structure gate for Thai drafts.")
    parser.add_argument("draft")
    parser.add_argument("lexicon")
    parser.add_argument("--scope", default="report", choices=["report", "article", "letter"],
                        help="which scoped rules apply on top of the universal set")
    parser.add_argument("--register", action="store_true",
                        help="record the run in the style miss register (off by default)")
    ns = parser.parse_args()
    lint(ns.draft, ns.lexicon, ns.scope, ns.register)

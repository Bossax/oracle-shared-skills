"""Validate a lexicon before the linter is ever allowed to load it.

This is the gate on the rule-producing side. `style-capture` writes the lexicon;
the linter consumes it. Without this check a malformed rule becomes a silently
dead gate -- which is how three rules from the 2026-08-05 round never fired.

Usage:
    validate_lexicon.py <lexicon.json>
"""
import json
import re
import sys
from pathlib import Path

KINDS = {"literal", "regex", "structural"}
SCOPES = {"universal", "report", "article", "letter"}
REQUIRED = ("banned", "preferred", "reason", "kind", "scope")

# characters whose presence in a "literal" almost always means someone wrote a
# prose description of a rule into a field meant for an exact string
DESCRIPTION_TELLS = "[](){}"


def validate(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors, warnings = [], []

    for key in ("context", "version", "lexicon"):
        if key not in data:
            errors.append(f"missing top-level key: {key}")
    if errors:
        report(errors, warnings)

    seen = {}
    for i, e in enumerate(data.get("lexicon", [])):
        tag = f"[{i}] {str(e.get('banned'))[:40]!r}"

        missing = [k for k in REQUIRED if k not in e]
        if missing:
            errors.append(f"{tag}: missing key(s) {missing}")
            continue

        kind, scope, banned = e["kind"], e["scope"], e["banned"]

        if kind not in KINDS:
            errors.append(f"{tag}: kind {kind!r} not in {sorted(KINDS)}")
        if scope not in SCOPES:
            errors.append(f"{tag}: scope {scope!r} not in {sorted(SCOPES)}")
        if not str(banned).strip():
            errors.append(f"{tag}: banned is empty")

        if banned in seen:
            errors.append(f"{tag}: duplicate of entry [{seen[banned]}]")
        else:
            seen[banned] = i

        if kind == "literal":
            # the trap: applying the prescribed fix still trips the rule -> infinite loop
            if banned and banned in str(e["preferred"]):
                errors.append(
                    f"{tag}: preferred contains its own banned string -- "
                    f"the prescribed fix cannot pass this rule (infinite loop). "
                    f"Reclassify as structural or rewrite preferred.")
            hits = [c for c in DESCRIPTION_TELLS if c in banned]
            if hits:
                errors.append(
                    f"{tag}: literal contains {hits} -- this reads as a prose "
                    f"description, not an exact string. Use kind=regex with a pattern.")
            if "..." in banned or "…" in banned:
                errors.append(
                    f"{tag}: literal contains an ellipsis -- that is wildcard intent. "
                    f"Either ban the stem exactly, or use kind=regex with a pattern.")
            if len(banned) > 80:
                warnings.append(f"{tag}: literal is {len(banned)} chars -- suspiciously long for a term")

        elif kind == "regex":
            if "pattern" not in e:
                errors.append(f"{tag}: kind=regex requires a `pattern` field")
            else:
                try:
                    rx = re.compile(e["pattern"])
                except re.error as err:
                    errors.append(f"{tag}: pattern does not compile -- {err}")
                else:
                    if rx.search("") and not e["pattern"]:
                        warnings.append(f"{tag}: pattern matches the empty string")

        elif kind == "structural":
            if "pattern" in e:
                warnings.append(f"{tag}: structural entries are never matched; `pattern` is ignored")

    counts = {}
    for e in data.get("lexicon", []):
        k = e.get("kind", "?")
        counts[k] = counts.get(k, 0) + 1

    print(f"lexicon  : {path}")
    print(f"context  : {data.get('context')}  version {data.get('version')}")
    print(f"entries  : {len(data.get('lexicon', []))}  {counts}")
    report(errors, warnings)


def report(errors, warnings):
    for w in warnings:
        print(f"  WARN   {w}")
    if errors:
        print()
        for e in errors:
            print(f"  ERROR  {e}")
        print(f"\nFAILED: {len(errors)} error(s)")
        sys.exit(1)
    print(f"\nPASSED{'' if not warnings else f' with {len(warnings)} warning(s)'}")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_lexicon.py <lexicon.json>")
        sys.exit(2)
    validate(sys.argv[1])

"""PreToolUse gate: no Thai prose before its argument map is approved.

Claude Code invokes this as a hook, feeding a JSON payload on stdin and
reading a JSON decision on stdout. It must fail OPEN on anything outside the
governed drafts tree -- a hook that blocks unrelated writes is not a gate, it
is an outage.

Governed path shape: ψ/incubate/drafts/**/*draft*.md
Sibling gate file:    argument-map.json in the same directory as the draft.

Usage (as a hook, not interactively):
    check_draft_preconditions.py < payload.json

The same output contract works for Claude Code and Codex. Claude commonly
provides `tool_input.file_path`; Codex's `apply_patch` hook provides the patch
in `tool_input.command`, so patch paths are extracted before checking them.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DRAFT_PATH_RE = re.compile(r"[\\/]ψ[\\/]incubate[\\/]drafts[\\/].*draft.*\.md$", re.IGNORECASE)


def decision(permission: str, reason: str = "") -> dict:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": permission,
        }
    }
    if reason:
        out["hookSpecificOutput"]["permissionDecisionReason"] = reason
    return out


def allow(reason: str = "") -> dict:
    return decision("allow", reason)


def deny(reason: str) -> dict:
    return decision("deny", reason)


def patch_text(payload: dict) -> str:
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, str):
        return tool_input
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "patch", "input"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def target_paths(payload: dict) -> list[str]:
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, dict):
        direct = tool_input.get("file_path") or tool_input.get("path")
        if isinstance(direct, str) and direct:
            return [direct]

    patch = patch_text(payload)
    if not patch:
        return []

    paths = []
    # OpenAI/Claude apply_patch format: *** Update File: path
    for match in re.finditer(r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", patch, re.MULTILINE):
        paths.append(match.group(1).strip())
    # Unified diff format, retained for wrappers that serialize patches this way.
    for match in re.finditer(r"^\+\+\+\s+b/(.+?)\s*$", patch, re.MULTILINE):
        paths.append(match.group(1).strip())
    return list(dict.fromkeys(paths))


def check(path_str: str) -> dict:
    path = Path(path_str)
    if not DRAFT_PATH_RE.search(str(path).replace("\\", "/")):
        return allow()

    map_path = path.parent / "argument-map.json"
    if not map_path.exists():
        return deny(
            "CRITICAL GATE FAILURE: argument-map.json is missing beside "
            f"{path.name}. Draft prose cannot be written or revised before "
            "the argument map is built and approved (writing-th v6.0 Stage 2)."
        )

    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        return deny(f"CRITICAL GATE FAILURE: argument-map.json is unreadable ({err}).")

    status = (data.get("approval") or {}).get("status")
    if status != "approved":
        return deny(
            f"CRITICAL GATE FAILURE: argument-map.json approval.status is "
            f"{status!r}, not 'approved'. No prose before the logic is "
            "signed off."
        )

    return allow()


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        # A hook that cannot parse its own input must not block unrelated work.
        print(json.dumps(allow("could not parse hook payload; failing open")))
        return 0

    paths = target_paths(payload)
    if not paths:
        print(json.dumps(allow()))
        return 0

    for path in paths:
        result = check(path)
        if result["hookSpecificOutput"]["permissionDecision"] == "deny":
            print(json.dumps(result))
            return 0

    print(json.dumps(allow()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

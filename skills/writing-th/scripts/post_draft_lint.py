"""PostToolUse hook: auto-lint a Thai draft after Write/Edit. Advisory only.

Reads the hook JSON payload on stdin. If a direct path or an apply_patch path is
under ψ/incubate/drafts/, runs lint_thai_writing.py against it and returns the
findings as additionalContext. Never denies -- a linter is not a gate; the gate
is merge_draft.py, which reruns this same check and can refuse to merge.

Usage (as a hook, not interactively):
    post_draft_lint.py < payload.json
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parents[3]  # scripts -> writing-th -> skills -> .agents -> repo root
LEXICON = REPO_ROOT / "ψ" / "memory" / "style" / "LEXICON_TH.json"
DRAFTS_MARKER = "ψ/incubate/drafts/"


def target_paths(payload: dict) -> list[str]:
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, dict):
        direct = tool_input.get("file_path") or tool_input.get("path")
        if isinstance(direct, str) and direct:
            return [direct]
        patch = next(
            (tool_input.get(key) for key in ("command", "patch", "input")
             if isinstance(tool_input.get(key), str)),
            "",
        )
    elif isinstance(tool_input, str):
        patch = tool_input
    else:
        patch = ""

    paths = []
    for match in re.finditer(r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", patch, re.MULTILINE):
        paths.append(match.group(1).strip())
    for match in re.finditer(r"^\+\+\+\s+b/(.+?)\s*$", patch, re.MULTILINE):
        paths.append(match.group(1).strip())
    return list(dict.fromkeys(paths))


def additional_context(text: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": text,
        }
    }


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        return 0

    tool_input = payload.get("tool_input") or {}
    paths = target_paths(payload)
    if not paths:
        return 0

    if not LEXICON.exists():
        return 0

    outputs = []
    for path_str in paths:
        normalized = str(Path(path_str)).replace("\\", "/")
        if DRAFTS_MARKER not in normalized or not path_str.lower().endswith(".md"):
            continue
        if not Path(path_str).exists():
            continue
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "lint_thai_writing.py"), path_str, str(LEXICON), "--scope", "report"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        if output.strip():
            outputs.append(f"{path_str}:\n{output.strip()}")

    output = "\n\n".join(outputs)
    if output.strip():
        print(json.dumps(additional_context(f"lint_thai_writing.py advisory:\n{output.strip()}")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Guard against the two SKILL.md copies diverging.

`.agents/skills/` is canonical (read by the other agent runtime).
`.claude/skills/` is the copy Claude Code actually routes from.

Both copies must stay identical. Run after any skill edit.
Use --sync to overwrite the .claude copy from the canonical one.
"""
import sys
import difflib
from pathlib import Path

PAIRS = [
    ("writing-th", "SKILL.md"),
    ("writing-th", "references/editorial-rubric.md"),
    ("writing-th", "references/artifact-schemas.md"),
    ("writing-th", "references/prose-kernel.md"),
    ("writing-th", "references/subagent-prompts.md"),
    ("writing-th", "references/revision-mode.md"),
    ("style-capture", "SKILL.md"),
]


def repo_root():
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "AGENTS.md").exists() and (parent / ".agents").is_dir():
            return parent
    print("ERROR: could not locate repo root (needs AGENTS.md + .agents/)")
    sys.exit(2)


def check(sync=False):
    root = repo_root()
    drifted = []

    for skill, fname in PAIRS:
        canonical = root / ".agents" / "skills" / skill / fname
        installed = root / ".claude" / "skills" / skill / fname

        if not canonical.exists():
            print(f"MISSING canonical: {canonical.relative_to(root)}")
            drifted.append(skill)
            continue

        if not installed.exists():
            if sync:
                installed.parent.mkdir(parents=True, exist_ok=True)
                installed.write_bytes(canonical.read_bytes())
                print(f"SYNCED  (created) {skill}/{fname}")
                continue
            print(f"MISSING installed: {installed.relative_to(root)} -- /{skill} will not route")
            drifted.append(skill)
            continue

        a = canonical.read_text(encoding="utf-8").splitlines()
        b = installed.read_text(encoding="utf-8").splitlines()

        if a == b:
            print(f"OK      {skill}/{fname} ({len(a)} lines)")
            continue

        if sync:
            installed.write_bytes(canonical.read_bytes())
            print(f"SYNCED  {skill}/{fname} ({len(a)} lines)")
            continue

        drifted.append(skill)
        print(f"DRIFT   {skill}/{fname}: {len(a)} lines canonical vs {len(b)} installed")
        diff = list(difflib.unified_diff(a, b, ".agents", ".claude", lineterm="", n=1))
        for line in diff[:20]:
            print(f"        {line}")
        if len(diff) > 20:
            print(f"        ... {len(diff) - 20} more diff lines")

    if drifted:
        print(f"\nFAILED: {len(drifted)} skill(s) out of sync -- run with --sync to fix")
        sys.exit(1)

    print("\nPASSED: all skill copies identical")
    sys.exit(0)


if __name__ == "__main__":
    check(sync="--sync" in sys.argv)

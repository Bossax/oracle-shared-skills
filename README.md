# oracle-shared-skills

Single, version-controlled source of truth for writing skills shared across Oracle
persona projects (`Susu_Ocean`, `Arun_Creagy`, and future ones). Currently holds
`style-capture`, `writing-th`, and `shared-skill-release` (the release tooling for
this repo itself).

## Releasing a change

Made and validated an improvement to a skill while working in a consuming project?
Use the `shared-skill-release` skill (`skills/shared-skill-release/SKILL.md`) rather
than doing the git steps by hand — it walks the switch-off-detached-HEAD step, tags
and pushes, and propagates the bump to every project listed in `consumers.json`,
flagging the two things junctions don't cover (subagent defs, hooks) along the way.

## Why this exists

`style-capture` and `writing-th` used to be hand-copied between project repos with
no version control — copies diverged silently. This repo is now the only place
their content is authored. Consuming projects reference it, they don't fork it.

## How a project consumes this repo

1. Add as a git submodule at the project root, pinned to a tag:
   ```
   git submodule add https://github.com/Bossax/oracle-shared-skills.git .oracle-shared-skills
   cd .oracle-shared-skills && git checkout <tag> && cd ..
   ```
2. Create NTFS junctions (not copies, not symlinks) from the project's skill
   folders into the submodule checkout:
   ```
   New-Item -ItemType Junction -Path ".claude\skills\style-capture" -Target ".oracle-shared-skills\skills\style-capture"
   New-Item -ItemType Junction -Path ".claude\skills\writing-th"    -Target ".oracle-shared-skills\skills\writing-th"
   New-Item -ItemType Junction -Path ".agents\skills\style-capture" -Target ".oracle-shared-skills\skills\style-capture"
   New-Item -ItemType Junction -Path ".agents\skills\writing-th"    -Target ".oracle-shared-skills\skills\writing-th"
   ```
   Junctions need no admin rights or Developer Mode (unlike symlinks), and they
   resolve transparently for any AI agent that reads a skills folder — Claude Code,
   Antigravity, Codex, etc.
3. Run `scripts\sync-agents.ps1 -ProjectRoot <project root>` to copy the shared
   subagent definitions into `.claude\agents\` (these are small individual files
   mixed into a directory that also holds project-specific agents, so they're
   copied, not junctioned — see "Why subagents are copied, not junctioned" below).
4. Apply `skills\writing-th\setup\settings.local.hooks.json` to the project's
   `.claude\settings.local.json` (merge the `hooks` key in by hand, or run
   `skills\writing-th\setup\merge-hooks.ps1`). This wires the PreToolUse/PostToolUse
   gates that actually enforce `writing-th`'s draft-preconditions/lint rules.
5. Set up the Python environment writing-th's scripts need:
   ```
   python -m venv .oracle-shared-skills\skills\writing-th\.venv
   .oracle-shared-skills\skills\writing-th\.venv\Scripts\python -m pip install -r .oracle-shared-skills\skills\writing-th\scripts\requirements.txt
   ```
6. Verify: `python .oracle-shared-skills\skills\writing-th\tests\run_tests.py -v`

## The path-depth invariant (important — don't restructure lightly)

`writing-th`'s own scripts locate the project root by walking a fixed number of
parent directories from their own file location (e.g. `scripts/post_draft_lint.py`
uses `Path(__file__).resolve().parents[3]`, `tests/run_tests.py` and
`tests/test_editorial_gate.py` do the same). This assumes the layout:

```
<project root>/<one-segment-mount>/skills/<skill-name>/{scripts,tests}/...
```

i.e. exactly 4 directories between the project root and a script file. Windows
resolves NTFS junctions to their physical target when Python calls
`Path.resolve()`, so mounting this repo at a **single path segment** directly
under each project root (`.oracle-shared-skills/`) keeps that math correct with
zero script changes — the resolved physical path is still
`<project root>/.oracle-shared-skills/skills/writing-th/scripts/...`, 4 levels deep.

**Do not** nest the submodule deeper (e.g. `.oracle/shared-skills/`) or rename
`skills/<name>/scripts` or `skills/<name>/tests` without updating every script
that computes `parents[3]` (currently: `post_draft_lint.py`, `run_tests.py`,
`test_editorial_gate.py`; also `check_draft_preconditions.py` if it does the same
— check before changing).

## Why subagents are copied, not junctioned

`.claude/agents/` in a consuming project can hold both shared subagent defs
(the 3 files in `agents/` here) and project-specific ones (e.g. Arun_Creagy also
has `wp2-demand-scorer.md`, a CRDB-project-specific subagent that must never be
part of this shared repo). NTFS junctions only work on whole directories, so
junctioning `.claude/agents/` itself would either miss files or leak an unrelated
project's agent into another project. `scripts/sync-agents.ps1` copies only the
files that live in this repo's own `agents/` folder — it never touches anything
else in the target directory.

## Scope — what does and doesn't live here

**In scope:** skill definitions (`SKILL.md`), their scripts, references, tests,
and the subagents that exist purely to serve them.

**Out of scope, deliberately:**
- Generic Oracle skills (`forward`, `recap`, `rrr`, `trace`, etc.) — those are
  distributed separately via `oracle-skills-cli` into `~/.claude/skills/`.
- Captured style *content* (`STYLE_PACK_TH.md`, `LEXICON_TH.json`,
  `STRUCTURAL_RULES_TH.json`, `miss_register.db`, writing samples, evidence
  files) — that's each project's own generated voice data, kept in that
  project's `ψ/memory/style/` and `ψ/archive/style/`, never in this repo.
- Project-specific subagents (e.g. `wp2-demand-scorer.md`).

## Versioning and updates

Tags on `main` are the version registry (`v1.0.0`, `v1.1.0`, ...). See
`CHANGELOG.md`. To roll a new version out to a consuming project:

```
cd .oracle-shared-skills
git fetch --tags
git checkout <new tag>
cd ..
git add .oracle-shared-skills
git commit -m "bump oracle-shared-skills to <new tag>"
scripts\sync-agents.ps1 -ProjectRoot <project root>   # only if agents/*.md changed
```

Junctions never need to be recreated for an ordinary content change — only if
this repo's internal folder layout changes (see the path-depth invariant above).

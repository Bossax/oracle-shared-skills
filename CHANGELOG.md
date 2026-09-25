# Changelog

## v1.2.2 — 2026-09-25

**Bug fix (writing-th)**: `lint_thai_writing.py`'s STYLE_PACK_TH §7 contrast
check ("ไม่ใช่ [X] แต่ [Y]" / contrastive negative scaffolding, a CRITICAL
DON'T Boss confirmed 2026-08-30) only matched the two-clause `...แต่...`
template within 60 characters. Found via a live CRDB §5.1 draft
(`draft-v2.md`, 2026-09-25) with 5 instances of this already-established
rule violated, none caught by the old regex — all were the standalone
form: a clause negating an alternative reading (`...ไม่ใช่ [NP]`) with no
`แต่` anchor nearby. Added `ไม่ใช่ว่า` (an unambiguous idiom marker) to the
blocking regex outright, and added the bare standalone form as a new
non-blocking `[CONTRAST-STANDALONE]` review item — non-blocking because a
bare `ไม่ใช่ NP` is sometimes plain factual negation and needs human/agent
judgment rather than a mechanical fail.

**Content addition (writing-th)**: recovered a commit made in a parallel
session ("learn writingstyle from 2.3.1 chapter") that had gone orphaned
on a detached-HEAD checkout and would otherwise have been lost on the next
fast-forward. Adds dimension 10, `reader_onboarding_and_transition`, to
`editorial-rubric.md`'s Tier 2 review, and a matching "Mandatory
reader-onboarding bridge" section to `prose-kernel.md` — both require that
prose establish a reader-visible function/problem and why the preceding
artifact can't resolve it alone before introducing an unfamiliar technical
model, framework, or classification.

No interface or CLI change in either fix.

## v1.2.1 — 2026-09-05

**Bug fix**: every `powershell -File ...` invocation documented in
`shared-skill-release`'s SKILL.md, and the two internal script-to-script calls
in `propagate.ps1`, now use `pwsh -File ...` instead. `powershell` resolves to
legacy Windows PowerShell 5.1, which doesn't support `ConvertFrom-Json
-AsHashtable` (used throughout this repo's JSON-merge logic) - it hard-fails
loudly when actually needed. Also removed stray em-dash characters from 4
`.ps1` files (`detect-drift.ps1`, `propagate.ps1`, `release.ps1`,
`merge-hooks.ps1`) - legacy `powershell.exe` misreads non-ASCII bytes without
an explicit encoding, corrupting string literals mid-parse. Found via
`mcp-registry`'s sibling bug in the exact same pattern - fixed there too, in
`~/.claude/skills/mcp-registry/SKILL.md`.

No interface or behavior change - scripts always worked when invoked through a
PowerShell 7 host (e.g. via the `&` call operator from another pwsh session);
this only fixes the documented/scripted `powershell -File` invocation path.

## v1.2.0 — 2026-09-05

**Architecture correction**: `.agents\skills\<name>` was a junction, same as
`.claude\skills\<name>`. Confirmed empirically this breaks Antigravity: with the
junction in place, Codex resolved the 3 skills fine, but Antigravity's skill
scanner showed none of them, while every plain-directory skill in the same
folder showed up correctly for both agents. Since Antigravity and Codex both
read `.agents\skills\`, the fix can't be "give Antigravity a different path" —
it has to be a real directory there, which works for any scanner.

- Added `scripts/sync-skills.ps1` — copies skill folders into a consuming
  project's `.agents\skills\`, replacing any prior junction there.
- `.claude\skills\<name>` is unaffected — still junctioned, still correct
  (Claude Code resolves junctions fine).
- `shared-skill-release`'s `propagate.ps1` now always re-runs `sync-skills.ps1`
  for every consumer project on every release, not conditionally.

Consuming projects need to re-run the migration once: remove the `.agents\skills\*`
junctions, run `scripts/sync-skills.ps1 -ProjectRoot <project>`.

## v1.1.0 — 2026-09-04

Added `skills/shared-skill-release/` — a skill (SKILL.md + 3 PowerShell scripts:
`detect-drift.ps1`, `release.ps1`, `propagate.ps1`) plus a root `consumers.json`
registry, for propagating a validated change made in one consumer project to this
repo and out to every other consumer, without hand-running the git steps. Additive,
backward-compatible — no change to `style-capture` or `writing-th`.

## v1.0.0 — 2026-09-04

Initial canonical baseline. Seeded from `Arun_Creagy`'s `.agents/skills/` copies
(the git-tracked canonical source there — `.claude/skills/` in Arun_Creagy is
gitignored and had drifted stale) and its `.claude/agents/` subagent defs.

- `skills/style-capture/SKILL.md` — 202-line portable version (Claude Code +
  Antigravity/Codex aware).
- `skills/writing-th/` — v6.2.0, Stage 0–6 argument-map pipeline, 17 scripts,
  5 references, 6-file test suite.
- `agents/th-argument-mapper.md`, `agents/th-editorial-reviewer.md`,
  `agents/th-verbalizer.md` — the 3 subagents `writing-th` depends on.

Consuming projects at this version: `Susu_Ocean`, `Arun_Creagy` (both wired via
submodule + junctions, replacing their prior independent, diverged copies).

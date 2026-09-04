# Changelog

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

---
name: shared-skill-release
description: >
  v1.0.0 | Release a change made to a skill in oracle-shared-skills (style-capture,
  writing-th, or a future one) and propagate it to every consumer project. Use when
  the user says "release shared skill", "publish skill change", "sync shared skill",
  "propagate skill update", or has just finished validating an edit made through a
  project's junctioned .claude/skills/ path and is ready to make it durable and shared.
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /shared-skill-release — publish a validated change, propagate it everywhere

This skill exists because editing a shared skill through a project's junction is easy
(the file just changes), but making that change *durable and shared* has several easy
ways to go wrong: the submodule checkout is in detached HEAD, two things silently
don't propagate through junctions at all (subagent defs, hook config), and it's easy
to forget to bump every consumer project in lockstep.

**Run this only after you've already validated the change works** — actually
exercised it in the project where you made it. This skill commits, tags, pushes, and
rewrites other projects' submodule pins; it is not a place to iterate.

## Step 0 — Identify the source project and the shared repo checkout

Ask the user (if not obvious from context) which project they were working in when
they made the change (e.g. `Arun_Creagy`). The shared repo checkout to release from
is `<that project>\.oracle-shared-skills`.

## Step 1 — Get off detached HEAD safely

```
cd <project>\.oracle-shared-skills
git status
```

If `git branch --show-current` prints nothing (detached HEAD, the normal submodule
state), run:

```
git switch main
git pull
```

Uncommitted working-tree changes survive this switch as long as `main` doesn't
conflict with the tag you were on (it won't, in the ordinary case where `main` is
just ahead of that tag). If git reports a conflict here, stop and resolve it with the
user rather than forcing past it — do not use `git checkout -f` or similar to bulldoze
local changes.

## Step 2 — Detect drift in the two things that don't auto-propagate

Run:

```
powershell -File skills\shared-skill-release\scripts\detect-drift.ps1 -ProjectRoot <project root>
```

This checks two categories that junctions do **not** cover:

1. **Subagent defs** — files in `<project>\.claude\agents\*.md` that are new or
   changed relative to `oracle-shared-skills\agents\`.
2. **Hooks** — whether `<project>\.claude\settings.local.json`'s `hooks` key differs
   from `skills\writing-th\setup\settings.local.hooks.json`.

For anything it reports, ask the user (AskUserQuestion) whether it belongs in this
release:
- A new/changed subagent file the user actually wants shared → copy it into
  `oracle-shared-skills\agents\<name>.md`.
- A new/changed hook the user wants shared → update
  `skills\writing-th\setup\settings.local.hooks.json` (or the equivalent setup file
  for whichever skill owns it) to match.
- Anything the user says is project-specific → leave it alone, don't copy it in.

## Step 3 — Review the diff and decide the version bump

```
git status
git diff
```

Summarize the change for the user and ask (AskUserQuestion) for the semver bump:
- **Patch** (`vX.Y.Z+1`) — bug fix, no interface change.
- **Minor** (`vX.Y+1.0`) — new tool/script/hook/subagent, additive, backward-compatible.
- **Major** (`vX+1.0.0`) — breaks the path-depth invariant (moving/renaming
  `skills/<name>/scripts` or `tests`, changing the mount point) or changes a script's
  CLI interface.

Update `CHANGELOG.md` with an entry for the new version describing what changed and
why, in the style of the existing entries.

## Step 4 — Commit, tag, and push the shared repo

```
powershell -File skills\shared-skill-release\scripts\release.ps1 -SharedRepoPath <project>\.oracle-shared-skills -Version vX.Y.Z -Message "<commit message>"
```

## Step 5 — Record the source project's own submodule bump

```
cd <project>
git add .oracle-shared-skills
git commit -m "bump oracle-shared-skills to vX.Y.Z"
```

## Step 6 — Propagate to every other consumer project

```
powershell -File <project>\.oracle-shared-skills\skills\shared-skill-release\scripts\propagate.ps1 -Tag vX.Y.Z -ExcludeProjectPaths <project> -SyncAgents:<$true if Step 2 added/changed a subagent file, else $false>
```

This walks `consumers.json`, and for every project other than the one just released
from: fetches the tag, checks it out in that project's submodule, and commits the
pointer bump in that project.

## Step 7 — Hooks need a human per project, always

If Step 2/3 changed anything in `settings.local.hooks.json`, this is never
auto-applied to another project's `settings.local.json` — tell the user explicitly
which other projects need it, and give them the exact command:

```
powershell -File <that project>\.oracle-shared-skills\skills\writing-th\setup\merge-hooks.ps1 -SettingsPath <that project>\.claude\settings.local.json
```

Remind them it backs up the existing file and only replaces the `hooks` key — they
should review the diff, especially if that project has other hooks configured.

## Step 8 — Verify

If any consumer project has real lexicon content (currently `Arun_Creagy`), run its
`tests/run_tests.py` one more time post-propagation to confirm nothing broke.

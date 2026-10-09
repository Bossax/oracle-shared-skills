---
name: maw-doctor
description: >
  Fleet Health, Snoop & Trap Detector for MAW. Inspects awake status across Oracles,
  peeks into active agent thinking panes, and diagnoses common MAW traps (e.g. panes dropping
  to raw bash prompt, broken symlinks, git branch conflicts).
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /maw-doctor — Fleet Health, Snoop & Trap Detector for MAW

> "Monitor without disrupting. Peek without attaching. Catch traps before dispatch."

## 1. When to Use
Use `/maw-doctor` when:
- You want to see which Oracles in the fleet are awake or asleep.
- You want to peek at what an Oracle is thinking/doing right now without attaching to its tmux session.
- A dispatched ticket returned `command not found` or didn't respond.
- You suspect git branch collisions or dead worktrees.

---

## 2. Quick Commands

```powershell
# Full fleet scan and health check
pwsh -File .agents/skills/maw-doctor/scripts/scan_fleet.ps1

# Detailed session metrics (tokens, uptime)
pwsh -File .agents/skills/maw-doctor/scripts/scan_fleet.ps1 -Detailed

# Inspect/peek into a specific Oracle
pwsh -File .agents/skills/maw-doctor/scripts/scan_fleet.ps1 -Target "keth"
```

---

## 3. Verified Traps & Remedies (From 2026-10-07 Cheatsheet)

| Trap / Error Symptom | Root Cause | Remedy |
| :--- | :--- | :--- |
| `[local:...]: command not found` | The target pane dropped back to a raw `bash` shell (e.g., agent CLI crashed or exited). Injecting prompts via `maw hey` executes text as shell commands. | Run `/maw-doctor -Target <name>` to verify pane state. Attach (`maw a <name>`) and restart `agy` before dispatching. |
| `unknown subcommand: show` | `maw team show` is not a valid subcommand in current `maw-js`. | Use `maw team ls` to list teams and `maw ls -v` to see live session metrics. |
| `not in tmux and no session exists` | Attempting to run `maw team bring` before initializing the canvas session. | Use `/maw-room` or run `maw new <team>` first to create the tmux canvas, then bring members. |
| `no oracle members in team` | Attempting to bring an uninvited member. | Use `maw team oracle-invite <oracle> --team <team>` first. |

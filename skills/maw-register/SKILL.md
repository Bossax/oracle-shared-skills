---
name: maw-register
description: >
  Register a local Windows Oracle repository into WSL MAW (ghq symlink,
  maw oracle register, and maw.config.json agent mapping). Use when adding
  a newly awakened Oracle to the local MAW fleet.
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /maw-register

Register a Windows Oracle repository into WSL MAW so peer Oracles can discover, wake, and message it.

## Prerequisites

- Target repo exists on Windows and contains a `ψ/` folder.
- WSL (`Ubuntu`) has `maw` installed at `~/.bun/bin/maw`.

## Usage

Run from the target Oracle repo root (or pass `-RepoPath`):

```powershell
# Preview changes without modifying WSL
pwsh -File .agents/skills/maw-register/scripts/register_oracle.ps1 -Name "aon" -DryRun

# Register the Oracle in WSL MAW
pwsh -File .agents/skills/maw-register/scripts/register_oracle.ps1 -Name "aon"

# Optional: set a custom launch command in maw.config.json (default is "agy")
pwsh -File .agents/skills/maw-register/scripts/register_oracle.ps1 -Name "aon" -Command "codex"
```

## What It Does

1. Translates the Windows repo path to `/mnt/<drive>/...` and creates `/home/sitth/Code/github.com/local/<name>-oracle` as a symlink in WSL.
2. Runs `maw oracle register <name>` to add the Oracle to `~/.maw/oracles.json` (skips if already registered).
3. Adds `"<name>": "local"` under `"agents"` in `~/.config/maw/maw.config.json` (and `"commands.<name>"` when `-Command` is provided).
4. Verifies registration with `maw locate <name>` and `maw oracle ls`.

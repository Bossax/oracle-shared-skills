---
name: maw-room
description: >
  Safe Tmux Canvas Lifecycle for MAW Teams. Automates team room provisioning,
  member invitations, and multi-pane tiling in tmux while avoiding initialization traps.
  Use when Boss wants a side-by-side visual workspace for multiple Oracles.
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /maw-room — Safe Canvas & Tmux Team Lifecycle

> "Provision without errors. Tile without traps. Detach cleanly."

## 1. When to Use
Use `/maw-room` when Boss wants to visually observe multiple Oracles working side-by-side in a split-pane tmux canvas, or when setting up a shared visual room for collaborative team tasks.

---

## 2. Quick Commands

```powershell
# Provision a new visual team canvas with specific members
pwsh -File .agents/skills/maw-room/scripts/provision_room.ps1 `
    -Team "climate-policy" `
    -Members @("arun", "keth", "jiu")

# Clean teardown of the room
pwsh -File .agents/skills/maw-room/scripts/provision_room.ps1 `
    -Team "climate-policy" `
    -Teardown
```

---

## 3. The 4-Step Verified Sequence (Cheatsheet Trap Avoidance)

The provisioning script automates the exact sequence required by `maw-js`:
1. `maw team create <team>`: Registers team in configuration.
2. `maw team oracle-invite <oracle> --team <team>`: Binds sovereign members to the team.
3. `maw new <team>`: **Creates the tmux canvas room first** (prevents `not in tmux and no session exists`).
4. `maw team bring <team>`: Docks and tiles all members side-by-side into split panes.

---

## 4. Tmux Navigation Reference (for Human / Boss)

Once attached to the session (`maw a <team>`):
- **Switch Pane**: `Ctrl+b` then Arrow keys.
- **Zoom Pane (Full Screen)**: `Ctrl+b` then `z` (press again to restore).
- **Detach Safely**: `Ctrl+b` then `d` (leaves agents running in background).
- **Close Pane**: `Ctrl+b` then `x`.

# Agent Instructions for `oracle-shared-skills`

This repository is the single version-controlled source of truth for shared AI skills, subagent definitions, and provisioning tooling across the Oracle fleet (`Arun_Creagy`, `Susu_Ocean`, `Keth-goverment-agent`, `Jiu-climate-risk-and-resilience`, and `Lauren-data-architect`).

---

## 1. Repository Layout & Taxonomy

The repository adheres to a strict, non-nested taxonomy:

```
oracle-shared-skills/
├── agents/             # All shared subagent personas live here
│   ├── thai-writer.md        # Claude Code & Antigravity (Markdown)
│   └── thai-writer.toml      # OpenAI Codex CLI (TOML)
├── skills/             # Skills catalog (each skill self-contained)
│   ├── writing-th/           # Thai institutional writing & quality gating
│   │   ├── references/       # Taxonomies & rubrics
│   │   ├── scripts/          # Node.js linters & hooks (.mjs)
│   │   ├── setup/            # Client hook configs
│   │   └── SKILL.md
│   ├── style-capture/        # Style-pack extraction & learning
│   ├── oracle-bootstrap/     # New Oracle repo bootstrapping & Docker MCP
│   └── shared-skill-release/ # Release, tag, and fleet propagation tooling
│       └── scripts/
│           ├── detect-drift.ps1
│           ├── release.ps1
│           └── propagate.ps1
├── tools/              # Central repository provisioning tools
│   └── sync-skills.ps1       # Multi-client local provisioner
├── consumers.json      # Fleet registry of active consumer projects
├── AGENTS.md           # This architecture & lifecycle guide
├── CLAUDE.md           # Pointer to AGENTS.md (@AGENTS.md)
├── CHANGELOG.md        # Semantic versioning changelog
└── README.md           # Overview & usage documentation
```

### Architectural Rules
1. **Never Nest Agents in Skills:** All shared agent definitions belong exclusively in the top-level `agents/` folder. Do not create `skills/<name>/agents/` folders.
2. **Every Skill Owns its Execution Scripts:** Skill-specific scripts (linters, pre-conditions, gates) live inside `skills/<name>/scripts/`.
3. **Repo-Level Utilities Live in `tools/`:** General setup and sync tools that operate on the repository or projects live in `tools/`.

---

## 2. Multi-Client Discovery Architecture

AI agents running in consumer projects discover skills and subagents through different mechanisms:

| Client Runtime | Skills Discovery Path | Subagent Discovery Path | Format | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | `<project>/.claude/skills/<name>` | `<project>/.claude/agents/<name>.md` | Markdown | Resolves NTFS Junctions cleanly. |
| **Google Antigravity** | `<project>/.agents/skills/<name>` | `<project>/.agents/agents/<name>.md` | Markdown | **Skips NTFS Junctions** on Windows; requires real physical folder copies. |
| **OpenAI Codex CLI** | `<project>/.agents/skills/<name>` | `<project>/.codex/agents/<name>.toml` | TOML | Reads skills from `.agents/skills` and subagents from `.codex/agents/*.toml`. |

---

## 3. Development & Release Lifecycle

To maintain fleet integrity and avoid uncommitted divergence, follow the 4-stage lifecycle:

### Stage 1: Local Iteration & Validation
* Work in an active consumer project (e.g. `Arun_Creagy`).
* Claude Code interacts through `.claude/skills/` (an NTFS junction pointing directly to `.oracle-shared-skills/skills/`). Changes made here update the shared submodule immediately on disk.
* Antigravity interacts directly with `.oracle-shared-skills/` or runs `tools/sync-skills.ps1` to update its `.agents/skills/` mirror.
* Always validate changes against real documents or test scripts before tagging.

### Stage 2: Git Branch Integrity Check
* Never cut a release from detached HEAD.
* Ensure `.oracle-shared-skills` is on branch `main` and up to date:
  ```powershell
  git -C .oracle-shared-skills switch main
  git -C .oracle-shared-skills pull
  ```

### Stage 3: Release & Fleet Propagation
* Trigger the release using the `shared-skill-release` skill:
  ```powershell
  # 1. Commit and Tag in shared submodule
  pwsh -File skills\shared-skill-release\scripts\release.ps1 -SharedRepoPath . -Version vX.Y.Z -Message "..."
  
  # 2. Push to GitHub
  git push origin main --tags
  
  # 3. Propagate to all projects in consumers.json
  pwsh -File skills\shared-skill-release\scripts\propagate.ps1 -Tag vX.Y.Z -ExcludeProjectPaths "<SourceProject>"
  ```

### Stage 4: Submodule Commit in Host Project
* In the source project (e.g. `Arun_Creagy`), commit the updated submodule commit pointer:
  ```powershell
  git add .oracle-shared-skills
  git commit -m "bump oracle-shared-skills to vX.Y.Z"
  ```

---

## 4. How to Use the `tools/` Folder

The `tools/` directory contains central scripts that manage file distribution and synchronization across projects:

### `tools/sync-skills.ps1`
**Purpose:** Declarative Multi-Client Provisioner and Cleaner.

**Syntax:**
```powershell
pwsh -File .oracle-shared-skills\tools\sync-skills.ps1 -ProjectRoot "C:\Users\sitth\OracleWorkspace\<ProjectName>"
```

**Actions Executed:**
1. **Syncs Skills:** Mirrors `skills/` into `<ProjectRoot>/.agents/skills/` as physical folders (so Antigravity and Codex scanners can read them). Excludes `.venv`, `__pycache__`, and temporary build artifacts.
2. **Provisions Subagents:**
   - Copies `agents/*.md` to `<ProjectRoot>/.claude/agents/` (Claude Code) and `<ProjectRoot>/.agents/agents/` (Antigravity).
   - Copies `agents/*.toml` to `<ProjectRoot>/.codex/agents/` (OpenAI Codex).
3. **Purges Retired Agents:** Automatically detects and removes dead legacy agent files (`th-argument-mapper.*`, `th-verbalizer.*`, `th-editorial-reviewer.*`) from all client directories.

**When to Run:**
* Automatically executed by `propagate.ps1` during fleet releases.
* Manually run when setting up a new repository via `oracle-bootstrap`.
* Manually run during local testing to immediately refresh `.agents/skills/` and agent files.

---

## 5. Core Invariants

* **No Em Dash:** Never use em dashes (`—`) in documentation, instructions, or code comments. Use colons, parentheses, or separate sentences.
* **Zero Overhead Runtime:** Migrate away from Python virtual environments (`.venv`) for utility scripts. Prefer zero-dependency Node.js (`.mjs`) utilizing native APIs like `Intl.Segmenter`.
* **Single Source of Truth:** Never copy skills manually between consumer projects without updating `oracle-shared-skills`.

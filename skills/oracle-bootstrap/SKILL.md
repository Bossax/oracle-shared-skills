---
name: oracle-bootstrap
description: >
  Set up Docker container, multi-client MCP configs (Codex, Antigravity, Claude Code),
  shared skills synchronization, and behavioral guardrails for a newly awakened Oracle repo.
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /oracle-bootstrap — New Oracle Provisioning & Behavioral Setup

Set up a new Oracle repository for dual-client support (Claude Code, Codex, Antigravity) with persistent Docker MCP integration, shared skills, and clean behavioral rules.

## Step 0: Prerequisites Check

1. Confirm Ollama is running on the host at `http://host.docker.internal:11434` with the embedding model installed (`ollama list` shows `bge-m3`).
2. Verify Docker engine is running.
3. Verify this command is run from the target project root (e.g. `C:\Users\sitth\OracleWorkspace\<Your-Oracle-Repo>`).

---

## Step 1: Tone & Behavioral Guardrails Choice

The `/awaken` ritual generates `AGENTS.md` and resonance files that often contain mythic or poetic ancestor text. Past sessions proved that poetic framing primes verbose output and em dash usage.

Ask the user:
> *"Do you want to preserve the mythic/poetic framing in your active `AGENTS.md`, or move it into `ψ/memory/resonance/` so your active rules use grounded, plain language with no em dashes?"*

### If the user selects Grounded (Recommended):
Ensure `ψ/memory/resonance/<oracle-name>.md` holds the birth narrative and poetic identity (honoring *Nothing is Deleted*), and format `<project root>/AGENTS.md` into the clean 3-tier ruleset (< 80 lines):

```markdown
# [Oracle Name]

## Goal
[State the exact purpose and human served in plain language. No fluff.]

## Response Style
**Always**
- Use plain, direct language. No fluff.
- Use concrete, everyday language first.
- Create clickable links for referenced files and code symbols using markdown links.

**Never**
- Use em dash.
- Use negating sentence structure (for example: "it is X, not Y").
- Use stacking domain jargon as the primary explanation.

## Operating Rules
1. **Nothing is deleted.** Supersede, do not erase. Maintain durable records.
2. **Compare actual state, not stated intent.** Trust live evidence over conversational memory.
3. **Surface, don't decide.** Never mark open questions answered with inferred defaults. Surface ambiguities for human decision.

## Boundaries
**Never**
- \`git push --force\`.
- \`rm -rf\` without backup.
- Commit secrets or credentials.

**Ask first**
- Before any \`git push\`.
- Before merging PRs.
- Before force-overwriting user files.
```

### Ensure Root Pointer:
Ensure `<project root>/CLAUDE.md` contains only:
```markdown
@AGENTS.md
```

---

## Step 2: Multi-Client MCP Configuration

Create client directories and provision configuration files pointing to the new Docker service container.

```powershell
# Create client configuration directories
New-Item -ItemType Directory -Force -Path ".agents", ".gemini", ".codex"
```

### 1. Claude Code: `<project root>/.mcp.json`
```json
{
  "mcpServers": {
    "oracle-v2": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "oracle-<name>",
        "bun",
        "src/index.ts"
      ],
      "env": {}
    }
  }
}
```

### 2. Antigravity: `<project root>/.gemini/mcp_config.json` and `<project root>/.agents/mcp_config.json`
```json
{
  "mcpServers": {
    "oracle-v2": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "oracle-<name>",
        "bun",
        "src/index.ts"
      ],
      "cwd": "C:/Users/sitth/OracleWorkspace/engine",
      "description": "Local Oracle Registry (Registry of Form)"
    }
  }
}
```

### 3. Codex: `<project root>/.codex/config.toml`
```toml
[mcp_servers.oracle-v2]
command = "docker"
args = ["exec", "-i", "oracle-<name>", "bun", "src/index.ts"]
cwd = "C:/Users/sitth/OracleWorkspace/engine"
```

---

## Step 3: Add Docker Compose Service

In `C:\Users\sitth\OracleWorkspace\docker-compose.yml`, inspect existing port numbers and pick the next free port (e.g. `47783` or higher).

Add the service block with `restart: unless-stopped`:

```yaml
  oracle-<name>:
    image: oven/bun:latest
    container_name: oracle-<name>
    restart: unless-stopped
    ports:
      - "<next-free-port>:47778"
    depends_on:
      oracle-archon:
        condition: service_started
    volumes:
      - ./engine:/app
      - ./<Your-Repo-Name>:/vault
      - ./.oracle-data/<name>:/root/.arra-oracle-v3
    working_dir: /app
    environment:
      - ORACLE_REPO_ROOT=/vault
      - ORACLE_DATA_DIR=/root/.arra-oracle-v3
      - ORACLE_PORT=47778
      - ORACLE_HTTP_URL=embedded
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - ORACLE_VECTOR_ENABLED=1
    command: bun run server
```

Start the container:
```bash
cd C:\Users\sitth\OracleWorkspace
docker-compose up -d oracle-<name>
```

---

## Step 4: Link `oracle-shared-skills` Submodule & Sync

From the target project root:

1. Add the submodule if not present:
   ```bash
   git submodule add https://github.com/Bossax/oracle-shared-skills.git .oracle-shared-skills
   ```
2. Create junctions for Claude Code in `.claude/skills`:
   ```powershell
   New-Item -ItemType Directory -Force -Path ".claude\skills"
   Get-ChildItem ".oracle-shared-skills\skills" -Directory | ForEach-Object {
       $target = $_.FullName
       $link = Join-Path ".claude\skills" $_.Name
       if (-not (Test-Path $link)) {
           New-Item -ItemType Junction -Path $link -Target $target
       }
   }
   ```
3. Populate `.agents/skills` and provision multi-client subagents:
   ```powershell
   pwsh -File .oracle-shared-skills\tools\sync-skills.ps1 -ProjectRoot (Get-Location).Path
   ```
4. Update `.gitignore` to keep local machine configs and junctioned skills clean:
   ```gitignore
   # Local client configs (machine-specific)
   .mcp.json
   .codex/
   .gemini/
   .agents/
   .claude/settings.local.json
   .claude/skills/style-capture/
   .claude/skills/writing-th/
   .claude/skills/shared-skill-release/
   .claude/skills/oracle-bootstrap/
   ```
6. Register the new consumer in `C:\Users\sitth\OracleWorkspace\oracle-shared-skills\consumers.json`.

---

## Step 5: Verification Smoke Test

1. Verify container is running:
   ```bash
   docker ps --filter "name=oracle-<name>"
   ```
2. Call `oracle_learn` with a test pattern and verify the response contains:
   `"embedding": "ok"`
3. Verify client discovery:
   - Antigravity / Codex: inspect `.agents/skills/` (confirm files exist as real directories, not broken links).
   - Claude Code: verify `.claude/skills/` junctions resolve.
4. Confirm that all three client configurations exist on disk and no em dashes exist in `AGENTS.md`.

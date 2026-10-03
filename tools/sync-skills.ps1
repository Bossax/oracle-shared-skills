<#
.SYNOPSIS
  Provisions shared skills and multi-client subagents from oracle-shared-skills into a consuming project.

.DESCRIPTION
  1. Copies skills into <ProjectRoot>\.agents\skills\ as real physical directories
     (Antigravity's scanner skips NTFS reparse points / junctions on Windows).
  2. Provisions shared subagents from agents\ to client-specific discovery paths:
     - *.md   -> <ProjectRoot>\.claude\agents\ (Claude Code)
     - *.md   -> <ProjectRoot>\.agents\agents\ (Google Antigravity)
     - *.toml -> <ProjectRoot>\.codex\agents\ (OpenAI Codex CLI)
  3. Purges retired legacy subagents from all client directories.

.PARAMETER ProjectRoot
  Absolute path to the consuming project, e.g. C:\Users\sitth\OracleWorkspace\Arun_Creagy

.EXAMPLE
  .\sync-skills.ps1 -ProjectRoot "C:\Users\sitth\OracleWorkspace\Arun_Creagy"
#>
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot
)

$sharedRoot = Split-Path -Parent $PSScriptRoot
$skillsSrc  = Join-Path $sharedRoot "skills"
$agentsSrc  = Join-Path $sharedRoot "agents"

$skillsDst  = Join-Path $ProjectRoot ".agents\skills"
$claudeAgentsDst = Join-Path $ProjectRoot ".claude\agents"
$agyAgentsDst    = Join-Path $ProjectRoot ".agents\agents"
$codexAgentsDst  = Join-Path $ProjectRoot ".codex\agents"

# ---------------------------------------------------------
# 1. Sync Skills (to .agents\skills\)
# ---------------------------------------------------------
Write-Host "=== Syncing Skills to $skillsDst ==="
if (Test-Path $skillsSrc) {
    if (-not (Test-Path $skillsDst)) {
        New-Item -ItemType Directory -Force -Path $skillsDst | Out-Null
    }

    Get-ChildItem $skillsSrc -Directory | ForEach-Object {
        $name = $_.Name
        $dst = Join-Path $skillsDst $name

        if (Test-Path $dst) {
            $item = Get-Item $dst -Force
            if ($item.LinkType) {
                (Get-Item $dst).Delete()
            } else {
                Remove-Item $dst -Recurse -Force
            }
        }

        robocopy $_.FullName $dst /E /XD .venv __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS | Out-Null
        Write-Host "  synced skill: $name -> $dst"
    }
}

# ---------------------------------------------------------
# 2. Provision Subagents to Multi-Client Discovery Paths
# ---------------------------------------------------------
Write-Host "`n=== Provisioning Multi-Client Subagents ==="
if (Test-Path $agentsSrc) {
    # Ensure destination directories exist
    @($claudeAgentsDst, $agyAgentsDst, $codexAgentsDst) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Force -Path $_ | Out-Null
        }
    }

    # Markdown agents (Claude Code & Antigravity)
    Get-ChildItem $agentsSrc -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $claudeAgentsDst $_.Name) -Force
        Copy-Item $_.FullName (Join-Path $agyAgentsDst $_.Name) -Force
        Write-Host "  provisioned md agent: $($_.Name) -> .claude/agents & .agents/agents"
    }

    # TOML agents (OpenAI Codex CLI)
    Get-ChildItem $agentsSrc -Filter "*.toml" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $codexAgentsDst $_.Name) -Force
        Write-Host "  provisioned toml agent: $($_.Name) -> .codex/agents"
    }
}

# ---------------------------------------------------------
# 3. Purge Retired Legacy Subagents
# ---------------------------------------------------------
Write-Host "`n=== Purging Retired Legacy Subagents ==="
$retiredAgents = @(
    "th-argument-mapper.md",
    "th-verbalizer.md",
    "th-editorial-reviewer.md",
    "th-argument-mapper.toml",
    "th-verbalizer.toml",
    "th-editorial-reviewer.toml"
)

foreach ($agentName in $retiredAgents) {
    @($claudeAgentsDst, $agyAgentsDst, $codexAgentsDst) | ForEach-Object {
        $targetFile = Join-Path $_ $agentName
        if (Test-Path $targetFile) {
            Remove-Item $targetFile -Force
            Write-Host "  purged retired agent: $targetFile"
        }
    }
}

Write-Host "`nSync complete for $ProjectRoot."

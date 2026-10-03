<#
.SYNOPSIS
  Bumps every OTHER consumer project (per consumers.json) to a newly released tag,
  optionally re-syncing subagent defs. Hooks are never auto-applied to another
  project - see SKILL.md Step 7.

.PARAMETER Tag
  The tag just released, e.g. v1.1.0

.PARAMETER ExcludeProjectPaths
  Project root path(s) to skip - the project the release was cut from, since it's
  already at this commit.

.PARAMETER SyncAgents
  Pass if this release changed anything in oracle-shared-skills\agents\ - re-runs
  each other project's sync-agents.ps1 after the bump.

.PARAMETER SyncGlobalAgents
  Pass if this release changed anything in oracle-shared-skills\global-agents\ - runs
  sync-global-agents.ps1 to update $HOME\.claude\agents\.

.PARAMETER ConsumersJson
  Path to consumers.json. Defaults to the one at the root of this shared repo.

.EXAMPLE
  .\propagate.ps1 -Tag v1.1.0 -ExcludeProjectPaths "C:\Users\sitth\OracleWorkspace\Arun_Creagy" -SyncAgents -SyncGlobalAgents
#>
param(
    [Parameter(Mandatory = $true)][string]$Tag,
    [string[]]$ExcludeProjectPaths = @(),
    [switch]$SyncAgents,
    [switch]$SyncGlobalAgents,
    [string]$ConsumersJson = (Join-Path $PSScriptRoot "..\..\..\consumers.json")
)

$consumers = (Get-Content $ConsumersJson -Raw | ConvertFrom-Json).consumers

foreach ($c in $consumers) {
    $normalizedExclude = $ExcludeProjectPaths | ForEach-Object { $_.TrimEnd('\') }
    if ($normalizedExclude -contains $c.path.TrimEnd('\')) {
        Write-Host "=== $($c.name): skipped (release source, already at $Tag) ==="
        continue
    }

    Write-Host "=== $($c.name) ==="
    $sub = Join-Path $c.path ".oracle-shared-skills"

    Push-Location $sub
    git fetch --tags
    git checkout $Tag
    Pop-Location

    Push-Location $c.path
    git add .oracle-shared-skills
    git commit -m "bump oracle-shared-skills to $Tag"
    Pop-Location

    # tools\sync-skills.ps1 provisions skills and multi-client agents into consumer project
    $skillsSyncScript = Join-Path $sub "tools\sync-skills.ps1"
    if (-not (Test-Path $skillsSyncScript)) {
        $skillsSyncScript = Join-Path $sub "scripts\sync-skills.ps1" # backward compat
    }
    if (Test-Path $skillsSyncScript) {
        pwsh -File $skillsSyncScript -ProjectRoot $c.path
    }

    Write-Host "$($c.name) bumped to $Tag."
    Write-Host ""
}

Write-Host "If this release changed hooks, apply them manually per project - see SKILL.md Step 7. Not automated here."


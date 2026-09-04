<#
.SYNOPSIS
  Detects drift in the two things that are NOT covered by junctions: subagent
  definitions in .claude\agents\ and hooks in .claude\settings.local.json.

.PARAMETER ProjectRoot
  Root of the project to check, e.g. C:\Users\sitth\OracleWorkspace\Arun_Creagy

.EXAMPLE
  .\detect-drift.ps1 -ProjectRoot "C:\Users\sitth\OracleWorkspace\Arun_Creagy"
#>
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot
)

$sharedRoot    = Join-Path $ProjectRoot ".oracle-shared-skills"
$sharedAgents  = Join-Path $sharedRoot "agents"
$projectAgents = Join-Path $ProjectRoot ".claude\agents"

Write-Host "=== Subagent drift (.claude\agents vs oracle-shared-skills\agents) ==="
$foundAgentDrift = $false
if (Test-Path $projectAgents) {
    Get-ChildItem $projectAgents -Filter "*.md" | ForEach-Object {
        $sharedFile = Join-Path $sharedAgents $_.Name
        if (-not (Test-Path $sharedFile)) {
            Write-Host "  NEW (not in shared repo yet): $($_.Name)"
            $foundAgentDrift = $true
        } else {
            $localHash  = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
            $sharedHash = (Get-FileHash $sharedFile -Algorithm SHA256).Hash
            if ($localHash -ne $sharedHash) {
                Write-Host "  CHANGED (differs from shared repo): $($_.Name)"
                $foundAgentDrift = $true
            }
        }
    }
}
if (-not $foundAgentDrift) { Write-Host "  none" }

Write-Host ""
Write-Host "=== Hook drift (.claude\settings.local.json vs writing-th\setup\settings.local.hooks.json) ==="
$settingsPath   = Join-Path $ProjectRoot ".claude\settings.local.json"
$hooksTemplate  = Join-Path $sharedRoot "skills\writing-th\setup\settings.local.hooks.json"
if ((Test-Path $settingsPath) -and (Test-Path $hooksTemplate)) {
    $localSettings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    $template      = Get-Content $hooksTemplate -Raw | ConvertFrom-Json -AsHashtable
    $localHooks    = if ($localSettings.ContainsKey("hooks")) { $localSettings["hooks"] } else { $null }
    $localJson     = if ($null -ne $localHooks) { $localHooks | ConvertTo-Json -Depth 10 -Compress } else { "" }
    $templateJson  = $template["hooks"] | ConvertTo-Json -Depth 10 -Compress
    if ($localJson -ne $templateJson) {
        Write-Host "  DIFFERENT: $settingsPath's hooks do not match the shared template."
    } else {
        Write-Host "  none — hooks match the shared template"
    }
} else {
    Write-Host "  could not compare (missing settings.local.json or template)"
}

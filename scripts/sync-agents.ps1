<#
.SYNOPSIS
  Copies this repo's shared subagent definitions into a consuming project's
  .claude\agents\ folder, without touching any project-specific agent file
  that already lives there.

.PARAMETER ProjectRoot
  Root of the consuming project, e.g. C:\Users\sitth\OracleWorkspace\Susu_Ocean

.EXAMPLE
  .\sync-agents.ps1 -ProjectRoot "C:\Users\sitth\OracleWorkspace\Susu_Ocean"
#>
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot
)

$src = Join-Path $PSScriptRoot "..\agents"
$dst = Join-Path $ProjectRoot ".claude\agents"
New-Item -ItemType Directory -Force $dst | Out-Null

Get-ChildItem $src -Filter "*.md" | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $dst $_.Name) -Force
    Write-Host "synced $($_.Name) -> $dst"
}

<#
.SYNOPSIS
  Copies this repo's shared global agent definitions (global-agents\*.md)
  into the user's global Claude agents folder ($HOME\.claude\agents).

.PARAMETER UserHome
  Optional override for the user home directory. Defaults to $HOME.

.EXAMPLE
  .\sync-global-agents.ps1
#>
param(
    [string]$UserHome = $HOME
)

$src = Join-Path $PSScriptRoot "..\global-agents"
$dst = Join-Path $UserHome ".claude\agents"

if (-not (Test-Path $src)) {
    Write-Host "No global-agents directory found at $src."
    exit 0
}

if (-not (Test-Path $dst)) {
    New-Item -ItemType Directory -Force $dst | Out-Null
}

Get-ChildItem $src -Filter "*.md" | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $dst $_.Name) -Force
    Write-Host "synced global agent $($_.Name) -> $dst"
}

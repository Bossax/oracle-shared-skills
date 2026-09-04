<#
.SYNOPSIS
  Merges writing-th's required PreToolUse/PostToolUse hooks into a project's
  .claude\settings.local.json, without touching any other key in that file.

.DESCRIPTION
  Backs up settings.local.json before writing. Only replaces the top-level
  "hooks" key with the one from settings.local.hooks.json - permissions,
  skillOverrides, enabledMcpjsonServers, etc. are left untouched. If the project
  already has its own "hooks" key (e.g. for a different tool matcher), review the
  backup diff manually - this script overwrites "hooks" wholesale, it does not
  attempt a deep merge of individual hook entries.

.PARAMETER SettingsPath
  Path to the target project's .claude\settings.local.json.

.EXAMPLE
  .\merge-hooks.ps1 -SettingsPath "C:\Users\sitth\OracleWorkspace\Susu_Ocean\.claude\settings.local.json"
#>
param(
    [Parameter(Mandatory = $true)][string]$SettingsPath
)

$hooksSnippet = Get-Content (Join-Path $PSScriptRoot "settings.local.hooks.json") -Raw | ConvertFrom-Json -AsHashtable

if (Test-Path $SettingsPath) {
    $backup = "$SettingsPath.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Copy-Item $SettingsPath $backup
    Write-Host "Backed up existing settings to $backup"
    $existing = Get-Content $SettingsPath -Raw | ConvertFrom-Json -AsHashtable
} else {
    Write-Host "No existing settings.local.json at $SettingsPath - creating new."
    $existing = @{}
}

if ($existing.ContainsKey("hooks")) {
    Write-Host "WARNING: existing 'hooks' key found and will be replaced wholesale. Review the backup if you had other hooks configured."
}
$existing["hooks"] = $hooksSnippet["hooks"]

$dir = Split-Path $SettingsPath -Parent
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }

$existing | ConvertTo-Json -Depth 10 | Set-Content $SettingsPath
Write-Host "Merged writing-th hooks into $SettingsPath - review the diff before trusting it."

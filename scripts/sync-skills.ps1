<#
.SYNOPSIS
  Copies this repo's skills into a consuming project's .agents\skills\, as real
  directories rather than junctions.

.DESCRIPTION
  .claude\skills\<name> stays a junction into this repo's checkout - Claude Code
  resolves junctions fine, so there's no reason to duplicate content there.

  .agents\skills\<name> is copied instead. Confirmed empirically: Codex resolves
  a junction at .agents\skills\ correctly, but Antigravity's skill scanner does
  not (it appears to skip NTFS reparse points when walking the directory) - even
  though both agents read the exact same path. Since a real directory works for
  every scanner regardless of reparse-point handling, .agents\skills\ trades the
  junction's free-update property for actually working in every consumer agent.

  This means .agents\skills\<name> needs an explicit re-sync after any change to
  a skill's content - same category as sync-agents.ps1 for .claude\agents\*.md.

.PARAMETER ProjectRoot
  Root of the consuming project, e.g. C:\Users\sitth\OracleWorkspace\Susu_Ocean

.EXAMPLE
  .\sync-skills.ps1 -ProjectRoot "C:\Users\sitth\OracleWorkspace\Susu_Ocean"
#>
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot
)

$skillsSrc = Join-Path $PSScriptRoot "..\skills"
$skillsDst = Join-Path $ProjectRoot ".agents\skills"

Get-ChildItem $skillsSrc -Directory | ForEach-Object {
    $name = $_.Name
    $dst = Join-Path $skillsDst $name

    if (Test-Path $dst) {
        $item = Get-Item $dst -Force
        if ($item.LinkType) {
            # was a junction - remove the link itself, not its target's content
            (Get-Item $dst).Delete()
        } else {
            Remove-Item $dst -Recurse -Force
        }
    }

    robocopy $_.FullName $dst /E /XD .venv __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS | Out-Null

    # This is a read-only mirror, not a source of truth - edits here would silently
    # diverge and never reach the shared repo (unlike .claude\skills, still a live
    # junction). Mark read-only so an accidental edit fails loudly instead.
    Get-ChildItem $dst -Recurse -File | ForEach-Object { $_.IsReadOnly = $true }

    Write-Host "synced skill: $name -> $dst (marked read-only)"
}

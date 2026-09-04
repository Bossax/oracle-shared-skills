<#
.SYNOPSIS
  Commits, tags, and pushes a validated change in an oracle-shared-skills checkout.
  Safe to call from a project's detached-HEAD submodule checkout — switches to main
  first if needed, bringing uncommitted changes along.

.PARAMETER SharedRepoPath
  Path to the oracle-shared-skills checkout to release from, e.g.
  C:\Users\sitth\OracleWorkspace\Arun_Creagy\.oracle-shared-skills

.PARAMETER Version
  Tag to create, e.g. v1.1.0 (semver: patch/minor/major per SKILL.md guidance).

.PARAMETER Message
  Commit and tag message.

.EXAMPLE
  .\release.ps1 -SharedRepoPath "C:\Users\sitth\OracleWorkspace\Arun_Creagy\.oracle-shared-skills" -Version v1.1.0 -Message "writing-th: add Stage 3.5 fact-check gate"
#>
param(
    [Parameter(Mandatory = $true)][string]$SharedRepoPath,
    [Parameter(Mandatory = $true)][string]$Version,
    [Parameter(Mandatory = $true)][string]$Message
)

Push-Location $SharedRepoPath
try {
    $branch = git branch --show-current
    if ([string]::IsNullOrWhiteSpace($branch)) {
        Write-Host "Detached HEAD detected — switching to main and bringing changes along..."
        git switch main
        if ($LASTEXITCODE -ne 0) {
            Write-Error "git switch main failed — resolve manually before releasing. Uncommitted changes were NOT touched."
            return
        }
        git pull
    }

    Write-Host "--- status before commit ---"
    git status --short

    git add -A
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Commit failed or nothing to commit — check status above."
        return
    }

    git tag -a $Version -m $Message
    git push origin main --tags

    Write-Host "Released $Version to origin/main."
}
finally {
    Pop-Location
}

<#
.SYNOPSIS
    Provisions or tears down a MAW team visual canvas without hitting the October 7 traps.

.PARAMETER Team
    Name of the team canvas (e.g. climate-policy-sprint).

.PARAMETER Members
    Array of Oracle member names to include (e.g. keth, jiu, arun).

.PARAMETER Teardown
    If set, cleanly shuts down the team session.
#>
param(
    [Parameter(Mandatory = $true)][string]$Team,
    [string[]]$Members = @(),
    [switch]$Teardown
)

function Invoke-WslBash([string]$BashCommand) {
    wsl -d Ubuntu -e bash -c "export PATH=`$HOME/.bun/bin:`$PATH; $BashCommand"
}

if ($Teardown) {
    Write-Host "Tearing down team room '$Team'..."
    Invoke-WslBash "maw team down $Team 2>/dev/null || tmux kill-session -t $Team 2>/dev/null || true"
    Write-Host "Team room '$Team' closed cleanly."
    exit 0
}

Write-Host "Provisioning MAW Team Room: '$Team'..."

# Step 1: Create team if it does not already exist
Write-Host "Step 1: Ensuring team exists..."
Invoke-WslBash "maw team create $Team 2>/dev/null || true"

# Step 2: Invite members
if ($Members.Count -gt 0) {
    Write-Host "Step 2: Inviting members ($($Members -join ', '))..."
    foreach ($m in $Members) {
        Write-Host "  - Inviting '$m' to '$Team'..."
        Invoke-WslBash "maw team oracle-invite $m --team $Team 2>/dev/null || true"
    }
}

# Step 3: Initialize tmux canvas session (Trap avoidance: must run maw new before maw team bring)
Write-Host "Step 3: Initializing tmux canvas (maw new $Team)..."
Invoke-WslBash "maw new $Team 2>/dev/null || true"

# Step 4: Dock and tile member panes
Write-Host "Step 4: Tiling member panes (maw team bring $Team)..."
Invoke-WslBash "maw team bring $Team 2>/dev/null || true"

Write-Host "`nTeam room '$Team' is ready!"
Write-Host "To attach visually in terminal, run: maw a $Team"
Write-Host "Tmux shortcuts inside canvas:"
Write-Host "  - Ctrl+b then arrows : Switch between panes"
Write-Host "  - Ctrl+b then z      : Zoom active pane full-screen / restore"
Write-Host "  - Ctrl+b then d      : Detach safely without killing agents"

<#
.SYNOPSIS
    Scans Oracle fleet health, inspects active agent panes, and diagnoses common MAW traps.

.PARAMETER Target
    Optional specific Oracle to inspect/peek.

.PARAMETER Detailed
    If set, queries verbose session metrics (maw ls -v).
#>
param(
    [string]$Target = "",
    [switch]$Detailed
)

function Invoke-WslBash([string]$BashCommand) {
    wsl -d Ubuntu -e bash -c "export PATH=`$HOME/.bun/bin:`$PATH; $BashCommand"
}

Write-Host "=== 1. Oracle Fleet Inventory ==="
Invoke-WslBash "maw oracle ls 2>/dev/null || true"

Write-Host "`n=== 2. Active Sessions ==="
if ($Detailed) {
    Invoke-WslBash "maw ls -v 2>/dev/null || true"
} else {
    Invoke-WslBash "maw ls 2>/dev/null || true"
}

Write-Host "`n=== 3. Health & Conflict Diagnostic (maw wtf) ==="
Invoke-WslBash "maw wtf 2>/dev/null || true"

if ($Target) {
    Write-Host "`n=== 4. Targeted Inspection for '$Target' ==="
    Write-Host "Peeking into '$Target' pane output..."
    $peek = Invoke-WslBash "maw peek $Target 2>/dev/null || true"
    Write-Host $peek

    if ($peek -match "(bash|sh)\s*[$#]\s*$" -or $peek -match "command not found") {
        Write-Warning "TRAP DETECTED: '$Target' pane has dropped to a raw bash shell!"
        Write-Warning "Remedy: Attach to session ('maw a $Target') or start 'agy' before dispatching text."
    }
}

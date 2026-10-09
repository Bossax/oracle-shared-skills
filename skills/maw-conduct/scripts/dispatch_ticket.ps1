<#
.SYNOPSIS
    Dispatches an Inter-Op ticket to a peer Oracle via maw-js in WSL.

.PARAMETER Target
    Canonical name of the target Oracle (e.g. keth, jiu, lauren, creagy-writing).

.PARAMETER Requester
    Canonical name of the requesting Oracle (e.g. arun, keth, jiu).

.PARAMETER RequesterInboxDir
    Local directory in the requesting Oracle's repo where deliverables arrive (e.g. C:\Users\sitth\OracleWorkspace\Arun_Creagy\ψ\inbox).

.PARAMETER Topic
    High-level topic of inquiry.

.PARAMETER Objective
    Detailed research task or questions.

.PARAMETER Slug
    Unique identifier slug (e.g. 2026-10-09_statutory-audit).

.PARAMETER DryRun
    If true, prints the payload and WSL commands without executing.
#>
param(
    [Parameter(Mandatory = $true)][string]$Target,
    [Parameter(Mandatory = $true)][string]$Requester,
    [Parameter(Mandatory = $true)][string]$RequesterInboxDir,
    [Parameter(Mandatory = $true)][string]$Topic,
    [Parameter(Mandatory = $true)][string]$Objective,
    [string]$Slug = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $Slug) {
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
    $Slug = "${timestamp}_${Target}-inquiry"
}

# Ensure sub-directory for target exists
$targetInboxDir = Join-Path $RequesterInboxDir "from-${Target}"
if (-not (Test-Path $targetInboxDir)) {
    New-Item -ItemType Directory -Path $targetInboxDir -Force | Out-Null
}

$deliverableFileName = "${Slug}.md"
$deliverableWinPath = Join-Path $targetInboxDir $deliverableFileName

# Translate Windows path to WSL path cleanly
$wslDeliverablePath = $deliverableWinPath
if ($deliverableWinPath -match "^([A-Za-z]):(.*)") {
    $drive = $Matches[1].ToLower()
    $rest = $Matches[2] -replace '\\', '/'
    $wslDeliverablePath = "/mnt/${drive}${rest}"
} else {
    $wslDeliverablePath = $deliverableWinPath -replace '\\', '/'
}

# Compose the RFC Ticket
$ticketPayload = @"
# [ORACLE TICKET] $Slug
- From: $Requester
- Requester Inbox: $wslDeliverablePath
- Topic: $Topic
- Objective: $Objective
- Wire Signal: maw hey $Requester 'DONE: $Slug'
"@

Write-Host "Prepared Inter-Op Ticket for target: $Target"
Write-Host "Expected Deliverable: $deliverableWinPath"

if ($DryRun) {
    Write-Host "[DryRun] Ticket Payload:`n$ticketPayload"
    [PSCustomObject]@{
        Status = "DryRun"
        Target = $Target
        DeliverablePath = $deliverableWinPath
    }
    return
}

# WSL Dispatch wrapper
function Invoke-WslBash([string]$BashCommand) {
    wsl -d Ubuntu -e bash -c "export PATH=`$HOME/.bun/bin:`$PATH; $BashCommand"
}

# 1. Check if target is awake
Write-Host "Checking liveness of '$Target' in MAW..."
$lsOutput = Invoke-WslBash "maw ls 2>/dev/null || true"
$isAwake = ($lsOutput -match "\b$Target\b")

if (-not $isAwake) {
    Write-Host "'$Target' is sleeping. Waking up..."
    Invoke-WslBash "maw wake $Target"
    Start-Sleep -Seconds 3
}

# 2. Check for bash-drop trap (verify not idle at raw bash prompt)
$peekOutput = Invoke-WslBash "maw peek $Target 2>/dev/null || true"
if ($peekOutput -match "(bash|sh)\s*[$#]\s*$" -or $peekOutput -match "command not found") {
    Write-Warning "Target '$Target' pane appears to be at a bash prompt! Injecting text directly may fail."
}

# 3. Dispatch ticket via maw hey
Write-Host "Dispatching ticket to '$Target' via maw hey..."
# Escape single quotes in ticket for bash
$escapedPayload = $ticketPayload -replace "'", "'\''"
Invoke-WslBash "maw hey $Target '$escapedPayload'"

Write-Host "Ticket successfully dispatched to '$Target'!"

[PSCustomObject]@{
    Status = "Dispatched"
    Target = $Target
    DeliverablePath = $deliverableWinPath
    Slug = $Slug
}

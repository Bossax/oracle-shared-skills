<#
.SYNOPSIS
    Completes an Inter-Op ticket by depositing the deliverable, archiving to outbox, and firing the wire signal.

.PARAMETER Requester
    Canonical name of the requesting Oracle (e.g. arun).

.PARAMETER Slug
    Ticket identifier slug.

.PARAMETER DeliverableFile
    Local path to the authored markdown brief to be delivered.

.PARAMETER RequesterInboxPath
    Target inbox path specified in the ticket (supports both Windows and WSL paths).

.PARAMETER ResponderRoot
    Root directory of the responding Oracle (for outbox archiving).
#>
param(
    [Parameter(Mandatory = $true)][string]$Requester,
    [Parameter(Mandatory = $true)][string]$Slug,
    [Parameter(Mandatory = $true)][string]$DeliverableFile,
    [Parameter(Mandatory = $true)][string]$RequesterInboxPath,
    [Parameter(Mandatory = $true)][string]$ResponderRoot
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $DeliverableFile)) {
    throw "Deliverable file does not exist: $DeliverableFile"
}

# Translate WSL path to Windows path if needed
$destWinPath = $RequesterInboxPath
if ($destWinPath -match "^/mnt/([a-zA-Z])/(.*)") {
    $drive = $Matches[1].ToUpper()
    $subPath = $Matches[2] -replace '/', '\'
    $destWinPath = "${drive}:\${subPath}"
}

$destDir = Split-Path -Parent $destWinPath
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

# 1. Copy deliverable to requester's inbox
Write-Host "Depositing deliverable to requester inbox: $destWinPath"
Copy-Item -LiteralPath $DeliverableFile -Destination $destWinPath -Force

# 2. Archive to responder's own outbox
$outboxDir = Join-Path $ResponderRoot "ψ\outbox"
if (-not (Test-Path $outboxDir)) {
    New-Item -ItemType Directory -Path $outboxDir -Force | Out-Null
}
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$outboxPath = Join-Path $outboxDir "${timestamp}_${Slug}.md"
Write-Host "Archiving copy to local outbox: $outboxPath"
Copy-Item -LiteralPath $DeliverableFile -Destination $outboxPath -Force

# 3. Fire wire completion signal via maw hey in WSL
Write-Host "Sending wire completion signal to '$Requester'..."
wsl -d Ubuntu -e bash -c "export PATH=`$HOME/.bun/bin:`$PATH; maw hey $Requester 'DONE: $Slug'"

Write-Host "Ticket $Slug completed and wire signal dispatched!"

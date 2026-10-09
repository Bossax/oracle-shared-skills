<#
.SYNOPSIS
    Zero-Token OS Waiter: waits for one or more deliverable files to land on disk.

.DESCRIPTION
    Polls the local filesystem at a specified interval using Start-Sleep (0% CPU, 0 LLM tokens).
    Exits code 0 as soon as all specified target files exist.
    Exits code 1 if the timeout is reached before all files arrive.

.PARAMETER Paths
    One or more file paths to monitor.

.PARAMETER TimeoutSeconds
    Maximum time to wait in seconds (default: 300).

.PARAMETER CheckInterval
    Interval between checks in seconds (default: 2).
#>
param(
    [Parameter(Mandatory = $true)]
    [string[]]$Paths,

    [int]$TimeoutSeconds = 300,
    [int]$CheckInterval = 2
)

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
Write-Host "Waiting for $($Paths.Count) file(s) to arrive on disk (Timeout: ${TimeoutSeconds}s)..."

foreach ($p in $Paths) {
    Write-Host "  - Target: $p"
}

while ($stopwatch.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
    $allPresent = $true
    foreach ($p in $Paths) {
        if (-not (Test-Path -LiteralPath $p)) {
            $allPresent = $false
            break
        }
    }

    if ($allPresent) {
        $stopwatch.Stop()
        Write-Host "All targets arrived in $([math]::Round($stopwatch.Elapsed.TotalSeconds, 1))s!"
        exit 0
    }

    Start-Sleep -Seconds $CheckInterval
}

$stopwatch.Stop()
Write-Error "Timeout reached (${TimeoutSeconds}s). Missing files:"
foreach ($p in $Paths) {
    if (-not (Test-Path -LiteralPath $p)) {
        Write-Error "  - Missing: $p"
    }
}
exit 1

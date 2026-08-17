param(
    [int]$IntervalSeconds = 10,
    [switch]$RunTestsOnUpdate
)

$ErrorActionPreference = "Continue"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host "AI Lab live progress watcher started." -ForegroundColor Cyan
Write-Host "Refresh interval: $IntervalSeconds seconds | Ctrl+C to stop" -ForegroundColor DarkGray
Start-Sleep -Seconds 1

$lastHead = ""

while ($true) {
    $fetchMessage = ""
    $pullMessage = ""

    try {
        git fetch origin main --quiet 2>$null
        $localHead = (git rev-parse HEAD 2>$null).Trim()
        $remoteHead = (git rev-parse origin/main 2>$null).Trim()

        if ($localHead -and $remoteHead -and $localHead -ne $remoteHead) {
            $dirty = git status --porcelain 2>$null
            if ([string]::IsNullOrWhiteSpace(($dirty -join ""))) {
                git pull --ff-only --quiet
                if ($LASTEXITCODE -eq 0) {
                    $pullMessage = "NEW UPDATE PULLED"
                } else {
                    $pullMessage = "PULL FAILED - check git status"
                }
            } else {
                $pullMessage = "REMOTE UPDATE AVAILABLE - local changes prevent auto-pull"
            }
        }
    } catch {
        $fetchMessage = "GitHub check failed: $($_.Exception.Message)"
    }

    $currentHead = (git rev-parse HEAD 2>$null).Trim()
    $headChanged = $currentHead -and $currentHead -ne $lastHead

    if ($RunTestsOnUpdate -and $headChanged -and $lastHead) {
        & "$repoRoot\status.ps1" -RunTests
    } else {
        & "$repoRoot\status.ps1"
    }

    Write-Host "LIVE WATCH" -ForegroundColor Cyan
    Write-Host ("Checked       : {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) -ForegroundColor White
    Write-Host ("Next refresh  : ~{0}s" -f $IntervalSeconds) -ForegroundColor DarkGray
    if ($pullMessage) { Write-Host $pullMessage -ForegroundColor Yellow }
    if ($fetchMessage) { Write-Host $fetchMessage -ForegroundColor Red }
    Write-Host "Ctrl+C to stop." -ForegroundColor DarkGray

    $lastHead = $currentHead
    Start-Sleep -Seconds $IntervalSeconds
}

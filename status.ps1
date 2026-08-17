param(
    [switch]$RunTests
)

$ErrorActionPreference = "SilentlyContinue"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$milestones = @(
    @{ Id = "M0"; Name = "Understanding Foundation"; Weight = 16; Done = 16; State = "DONE" },
    @{ Id = "M1"; Name = "Personal Understanding"; Weight = 17; Done = 0; State = "CURRENT" },
    @{ Id = "M2"; Name = "Persistent Personal Context"; Weight = 17; Done = 0; State = "TODO" },
    @{ Id = "M3"; Name = "One Real Vertical Loop: Coding"; Weight = 17; Done = 0; State = "TODO" },
    @{ Id = "M4"; Name = "Product Shell"; Weight = 16; Done = 0; State = "TODO" },
    @{ Id = "M5"; Name = "Capability Expansion"; Weight = 17; Done = 0; State = "TODO" }
)

$total = ($milestones | Measure-Object -Property Done -Sum).Sum
$barWidth = 40
$filled = [Math]::Floor(($total / 100) * $barWidth)
$empty = $barWidth - $filled
$bar = ("#" * $filled) + ("-" * $empty)

Clear-Host
Write-Host ""
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "                  AI LAB OS - V1.0 STATUS" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host ("TOTAL PROGRESS : [{0}] {1}%" -f $bar, $total) -ForegroundColor Green
Write-Host ""

foreach ($m in $milestones) {
    $pct = if ($m.Weight -eq 0) { 0 } else { [Math]::Round(($m.Done / $m.Weight) * 100) }
    $miniWidth = 10
    $miniFilled = [Math]::Floor(($pct / 100) * $miniWidth)
    $miniBar = ("#" * $miniFilled) + ("-" * ($miniWidth - $miniFilled))
    $color = switch ($m.State) {
        "DONE" { "Green" }
        "CURRENT" { "Yellow" }
        default { "DarkGray" }
    }
    Write-Host ("{0,-3} {1,-32} [{2}] {3,3}%  {4}" -f $m.Id, $m.Name, $miniBar, $pct, $m.State) -ForegroundColor $color
}

Write-Host ""
Write-Host "--------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "CURRENT TARGET" -ForegroundColor Cyan
Write-Host "M1 - Natural language + context -> validated IntentContract" -ForegroundColor White
Write-Host ""
Write-Host "NEXT USER-VISIBLE MILESTONE" -ForegroundColor Cyan
Write-Host '"修復這個 repo 的失敗測試"' -ForegroundColor White
Write-Host "Understand -> Plan -> Execute -> Verify -> Report" -ForegroundColor White
Write-Host "--------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

$branch = git branch --show-current 2>$null
$dirty = git status --porcelain 2>$null
$commit = git log -1 --pretty=format:"%h %s" 2>$null

Write-Host "GIT" -ForegroundColor Cyan
if ($branch) { Write-Host ("Branch : {0}" -f $branch) }
if ($commit) { Write-Host ("Commit : {0}" -f $commit) }
if ([string]::IsNullOrWhiteSpace(($dirty -join ""))) {
    Write-Host "Tree   : CLEAN" -ForegroundColor Green
} else {
    Write-Host "Tree   : CHANGED" -ForegroundColor Yellow
    $dirty | ForEach-Object { Write-Host ("         {0}" -f $_) -ForegroundColor Yellow }
}

Write-Host ""
if ($RunTests) {
    Write-Host "TESTS" -ForegroundColor Cyan
    python -m pytest -q
    if ($LASTEXITCODE -eq 0) {
        Write-Host "TEST RESULT : PASS" -ForegroundColor Green
    } else {
        Write-Host "TEST RESULT : FAIL" -ForegroundColor Red
    }
} else {
    Write-Host "Tests not run. Use: .\status.ps1 -RunTests" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Progress rule: percentage only increases after milestone acceptance evidence." -ForegroundColor DarkGray
Write-Host "Roadmap: docs\ROADMAP.md" -ForegroundColor DarkGray
Write-Host ""

param(
    [switch]$RunTests
)

$ErrorActionPreference = "SilentlyContinue"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

# Make src-layout imports work even before an editable install.
$srcPath = Join-Path $repoRoot "src"
if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
    $env:PYTHONPATH = $srcPath
} elseif (-not (($env:PYTHONPATH -split ';') -contains $srcPath)) {
    $env:PYTHONPATH = "$srcPath;$env:PYTHONPATH"
}

$evalPath = Join-Path $repoRoot "evals\understanding_cases.jsonl"
$evalCount = 0
if (Test-Path $evalPath) {
    $evalCount = @(Get-Content $evalPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
}
$evalTarget = 50
$evalPct = if ($evalTarget -gt 0) {
    [Math]::Min(100, [Math]::Round(($evalCount / $evalTarget) * 100))
} else { 0 }

$currentHead = (git rev-parse HEAD 2>$null).Trim()
$testEvidencePath = Join-Path $env:TEMP "ai-lab-new-last-passing-head.txt"
$testedHead = ""
if (Test-Path $testEvidencePath) {
    $testedHead = (Get-Content $testEvidencePath -Raw).Trim()
}

if ($RunTests) {
    Clear-Host
    Write-Host "Running AI Lab tests..." -ForegroundColor Cyan
    python -m pytest -q
    if ($LASTEXITCODE -eq 0) {
        Set-Content -Path $testEvidencePath -Value $currentHead -Encoding ascii
        $testedHead = $currentHead
        Write-Host "TEST RESULT : PASS" -ForegroundColor Green
    } else {
        Write-Host "TEST RESULT : FAIL" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 700
}

$hasContextCompiler = Test-Path (Join-Path $repoRoot "src\ai_lab\understanding\context.py")
$hasEntrypoint = Test-Path (Join-Path $repoRoot "src\ai_lab\understanding\entrypoint.py")
$hasPolicy = (Test-Path (Join-Path $repoRoot "src\ai_lab\understanding\service.py")) -and
             (Test-Path (Join-Path $repoRoot "src\ai_lab\understanding\policy.py"))
$hasConstraintRegression = Test-Path (Join-Path $repoRoot "tests\test_personal_context_contract.py")
$latestTestsPass = (-not [string]::IsNullOrWhiteSpace($currentHead)) -and ($testedHead -eq $currentHead)
$hasCloudAcceptance = Test-Path (Join-Path $repoRoot "evals\cloud_acceptance_results.jsonl")

# M1 is computed from concrete evidence, never from a hard-coded Done number.
$m1Pct = 0.0
if ($hasContextCompiler) { $m1Pct += 15 }
if ($hasEntrypoint) { $m1Pct += 15 }
if ($hasPolicy) { $m1Pct += 15 }
if ($hasConstraintRegression) { $m1Pct += 10 }
$m1Pct += 30 * [Math]::Min(1.0, ($evalCount / [double]$evalTarget))
if ($latestTestsPass) { $m1Pct += 10 }
if ($hasCloudAcceptance) { $m1Pct += 5 }
$m1Pct = [Math]::Min(100, [Math]::Round($m1Pct))

$milestones = @(
    @{ Id = "M0"; Name = "Understanding Foundation"; Weight = 16; Pct = 100; State = "DONE" },
    @{ Id = "M1"; Name = "Personal Understanding"; Weight = 17; Pct = $m1Pct; State = "CURRENT" },
    @{ Id = "M2"; Name = "Persistent Personal Context"; Weight = 17; Pct = 0; State = "TODO" },
    @{ Id = "M3"; Name = "One Real Vertical Loop: Coding"; Weight = 17; Pct = 0; State = "TODO" },
    @{ Id = "M4"; Name = "Product Shell"; Weight = 16; Pct = 0; State = "TODO" },
    @{ Id = "M5"; Name = "Capability Expansion"; Weight = 17; Pct = 0; State = "TODO" }
)

$totalRaw = 0.0
foreach ($m in $milestones) {
    $totalRaw += $m.Weight * ($m.Pct / 100.0)
}
$total = [Math]::Round($totalRaw)

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
    $pct = [int]$m.Pct
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
Write-Host "M1 EVIDENCE" -ForegroundColor Cyan
Write-Host ("Context compiler          : {0}" -f $(if ($hasContextCompiler) { "DONE" } else { "TODO" }))
Write-Host ("Canonical entrypoint      : {0}" -f $(if ($hasEntrypoint) { "DONE" } else { "TODO" }))
Write-Host ("Grounding + policy        : {0}" -f $(if ($hasPolicy) { "DONE" } else { "TODO" }))
Write-Host ("Constraint regression     : {0}" -f $(if ($hasConstraintRegression) { "DONE" } else { "TODO" }))
Write-Host ("Personal-language evals   : {0}/{1} ({2}%)" -f $evalCount, $evalTarget, $evalPct)
Write-Host ("Latest HEAD tests         : {0}" -f $(if ($latestTestsPass) { "PASS" } else { "NOT VERIFIED" })) -ForegroundColor $(if ($latestTestsPass) { "Green" } else { "Yellow" })
Write-Host ("Cloud-model acceptance    : {0}" -f $(if ($hasCloudAcceptance) { "DONE" } else { "TODO" }))

Write-Host ""
Write-Host "--------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "CURRENT TARGET" -ForegroundColor Cyan
Write-Host "M1 - make short natural-language references reliable and regression-tested" -ForegroundColor White
Write-Host ""
Write-Host "NEXT USER-VISIBLE MILESTONE" -ForegroundColor Cyan
Write-Host 'CONTINUE / THIS / PREVIOUS VERSION / ONLY CHANGE THIS preserve context and constraints' -ForegroundColor White
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
if (-not $RunTests) {
    Write-Host "Tests not run this refresh. Latest HEAD evidence shown above." -ForegroundColor DarkGray
    Write-Host "Use: .\status.ps1 -RunTests" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Progress is calculated from repository evidence; milestone DONE still requires acceptance evidence." -ForegroundColor DarkGray
Write-Host "Roadmap: docs\ROADMAP.md" -ForegroundColor DarkGray
Write-Host ""

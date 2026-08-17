param(
    [string]$RepoUrl = "https://github.com/guanyanning789-lgtm/AI-Lab-New.git",
    [string]$Destination = "C:\AI-Lab\AI-Lab-New"
)

$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not available in PATH."
}

if (Test-Path $Destination) {
    if (-not (Test-Path (Join-Path $Destination ".git"))) {
        throw "Destination exists but is not a Git repository: $Destination"
    }
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    git clone $RepoUrl $Destination
    if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
}

Push-Location $Destination
try {
    $dirty = git status --porcelain
    if ($dirty) {
        throw "Destination repository is not clean. No files were changed."
    }

    $existing = Get-ChildItem -Force | Where-Object { $_.Name -ne ".git" }
    if ($existing) {
        throw "Destination repository is not empty. Foundation publishing is intentionally blocked."
    }

    Get-ChildItem -Force $SourceRoot |
        Where-Object { $_.Name -notin @(".git", ".pytest_cache", "__pycache__") } |
        Copy-Item -Destination $Destination -Recurse -Force

    Get-ChildItem -Path $Destination -Recurse -Directory -Force |
        Where-Object { $_.Name -in @("__pycache__", ".pytest_cache") } |
        Remove-Item -Recurse -Force

    git checkout -B main
    if ($LASTEXITCODE -ne 0) { throw "could not create main branch" }

    git add README.md AGENTS.md pyproject.toml .gitignore docs evals scripts src tests .github
    if ($LASTEXITCODE -ne 0) { throw "git add failed" }

    git commit -m "Establish AI Lab OS understanding foundation"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed; verify your Git identity" }

    git push -u origin main
    if ($LASTEXITCODE -ne 0) { throw "git push failed; verify GitHub authentication" }

    Write-Host "AI Lab OS foundation published successfully." -ForegroundColor Green
} finally {
    Pop-Location
}

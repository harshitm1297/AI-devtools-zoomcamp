$ErrorActionPreference = "Stop"
$env:UV_CACHE_DIR = Join-Path $PWD ".uv-cache"
$env:PYTHONDONTWRITEBYTECODE = "1"

function Assert-LastExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

uv sync --frozen
Assert-LastExitCode "Dependency synchronization"
uv run --frozen pytest -q --basetemp=.pytest-tmp-verify
Assert-LastExitCode "Backend tests"
uv run --frozen python scripts/evaluate.py
Assert-LastExitCode "Deterministic evaluation"
uv run --frozen python agent-hooks/privacy_guard.py
Assert-LastExitCode "Privacy guard"
npm test
Assert-LastExitCode "Frontend tests"
npm run check
Assert-LastExitCode "Frontend syntax checks"

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose config --quiet
    Assert-LastExitCode "Docker Compose validation"
    docker compose build
    Assert-LastExitCode "Container build"
} else {
    Write-Warning "Docker is not installed; container verification was skipped."
}

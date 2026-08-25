$ErrorActionPreference = "Stop"

$preflight = Join-Path $PSScriptRoot "..\infra\check_rag_prerequisites.ps1"
& $preflight
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    Write-Host "Mini Agent 04 virtual environment was not found: $python"
    Write-Host "Create it and install requirements before running E2E tests."
    exit 1
}

$env:RUN_RAG_E2E = "1"
Push-Location (Join-Path $PSScriptRoot "backend")
try {
    & $python -m pytest -q -p no:cacheprovider tests\test_rag_e2e.py
    exit $LASTEXITCODE
} finally {
    Pop-Location
}

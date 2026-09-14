$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

function Invoke-Step {
    param([string]$Title, [scriptblock]$Action)
    Write-Host "`n=== $Title ===" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Title failed with exit code $LASTEXITCODE"
    }
}

Push-Location (Join-Path $root "tradebusiness-backend")
try {
    $python = Join-Path (Get-Location) "venv\Scripts\python.exe"
    Invoke-Step "Backend tests" { & $python -m pytest tests -q --disable-warnings --no-cov }
    Invoke-Step "Backend Black" { & $python -m black --check app scripts tests }
    Invoke-Step "Backend isort" { & $python -m isort --check-only app scripts tests }
    Invoke-Step "Production Compose" { & $python -c "import yaml; yaml.safe_load(open('docker-compose.prod.yml', encoding='utf-8')); print('production compose ok')" }
} finally {
    Pop-Location
}

foreach ($frontend in @("tradebusiness-admin", "tradebusiness-client")) {
    Push-Location (Join-Path $root $frontend)
    try {
        Write-Host "`n=== $frontend type-check ===" -ForegroundColor Cyan
        npm run type-check
        if ($LASTEXITCODE -ne 0) { throw "$frontend type-check failed with exit code $LASTEXITCODE" }
        Write-Host "`n=== $frontend build ===" -ForegroundColor Cyan
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "$frontend build failed with exit code $LASTEXITCODE" }
    } finally {
        Pop-Location
    }
}

Write-Host "`nRelease checks passed." -ForegroundColor Green

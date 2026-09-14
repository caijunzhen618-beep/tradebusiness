# Clean Project Cache - PowerShell Script
# Run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Then: .\cleanup.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Clean Project Cache Files" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Cleaning Python cache..." -ForegroundColor Yellow
$paths = @(
    "tradebusiness-backend\app\__pycache__",
    "tradebusiness-backend\app\**\__pycache__"
)
foreach ($path in $paths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "Python cache cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "[2/5] Cleaning frontend cache..." -ForegroundColor Yellow
$paths = @(
    "tradebusiness-admin\node_modules\.vite",
    "tradebusiness-client\node_modules\.vite"
)
foreach ($path in $paths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "Frontend cache cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Cleaning log files..." -ForegroundColor Yellow
$logPath = "tradebusiness-backend\logs"
if (Test-Path $logPath) {
    Get-ChildItem -Path $logPath -Filter "*.log" | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "Log files cleaned" -ForegroundColor Green
} else {
    Write-Host "No log files found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[4/5] Cleaning temporary files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Include "*.pyc","*.bak","*.tmp","*~" | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Temporary files cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Cleaning Python cache directories..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Python cache directories cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: node_modules folders are preserved" -ForegroundColor Gray
Write-Host "For full cleanup, manually delete:" -ForegroundColor Gray
Write-Host "  - tradebusiness-admin\node_modules" -ForegroundColor White
Write-Host "  - tradebusiness-client\node_modules" -ForegroundColor White
Write-Host "  - tradebusiness-backend\venv" -ForegroundColor White
Write-Host ""

# Optional: Pause to see output
# Read-Host -Prompt "Press Enter to exit"

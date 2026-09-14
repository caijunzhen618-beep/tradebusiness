@echo off
REM Start Admin Frontend Only

echo.
echo ========================================
echo Starting Admin Panel
echo ========================================
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%tradebusiness-admin"

REM Check dependencies
if not exist "node_modules" (
    echo ERROR: Dependencies not installed
    echo Run: npm install
    pause
    exit /b 1
)

REM Start service
echo Starting admin frontend...
echo URL: http://localhost:3000
echo.
npm run dev

pause

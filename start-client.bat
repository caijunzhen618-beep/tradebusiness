@echo off
REM Start Client Frontend Only

echo.
echo ========================================
echo Starting Client Panel
echo ========================================
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%tradebusiness-client"

REM Check dependencies
if not exist "node_modules" (
    echo ERROR: Dependencies not installed
    echo Run: npm install
    pause
    exit /b 1
)

REM Start service
echo Starting client frontend...
echo URL: http://localhost:3001
echo.
npm run dev

pause

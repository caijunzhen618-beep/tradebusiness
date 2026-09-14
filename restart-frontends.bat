@echo off
REM Restart frontend dev servers with new environment variables

echo ============================================================
echo Restarting Frontend Development Servers
echo ============================================================
echo.

echo Step 1: Stopping current frontend processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr LISTENING') do (
    echo   Stopping Admin frontend (PID %%a)
    taskkill /F /PID %%a 2>nul
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr LISTENING') do (
    echo   Stopping Client frontend (PID %%a)
    taskkill /F /PID %%a 2>nul
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting Admin frontend (port 3000)...
start "TradeBusiness Admin Frontend" cmd /k "cd /d %~dp0tradebusiness-admin && npm run dev"

echo.
echo Waiting 3 seconds for Admin frontend to start...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Starting Client frontend (port 3001)...
start "TradeBusiness Client Frontend" cmd /k "cd /d %~dp0tradebusiness-client && npm run dev"

echo.
echo ============================================================
echo Frontend servers started in new windows!
echo ============================================================
echo.
echo Admin:  http://localhost:3000
echo Client: http://localhost:3001
echo.
echo IMPORTANT:
echo 1. Wait for frontends to fully start (about 10 seconds)
echo 2. Clear browser cache (Ctrl+Shift+R)
echo 3. Then visit the URLs above
echo.
pause

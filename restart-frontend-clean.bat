@echo off
REM Complete frontend restart with cache clearing

echo ============================================================
echo Complete Frontend Restart with Cache Clear
echo ============================================================
echo.

echo Step 1: Stopping frontend processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Clearing Vite cache...
if exist "tradebusiness-admin\node_modules\.vite" (
    rd /s /q "tradebusiness-admin\node_modules\.vite"
    echo Admin Vite cache cleared
)
if exist "tradebusiness-client\node_modules\.vite" (
    rd /s /q "tradebusiness-client\node_modules\.vite"
    echo Client Vite cache cleared
)

echo.
echo Step 3: Starting Admin frontend (port 3000)...
start "TradeBusiness Admin" cmd /k "cd /d %~dp0tradebusiness-admin && npm run dev"

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo.
echo Step 4: Starting Client frontend (port 3001)...
start "TradeBusiness Client" cmd /k "cd /d %~dp0tradebusiness-client && npm run dev"

echo.
echo ============================================================
echo Frontends restarted with cleared cache!
echo ============================================================
echo.
echo IMPORTANT:
echo 1. Wait for frontends to start (about 10 seconds)
echo 2. Close ALL browser windows completely
echo 3. Reopen browser
echo 4. Visit: http://localhost:3000
echo.
echo To check environment, visit: http://localhost:3000/index-check.html
echo.
pause

@echo off
REM Environment Check Script
REM System Health Check for TradeBusiness

echo ========================================
echo System Environment Check
echo ========================================
echo.

set "ROOT=%~dp0"

echo [1] Checking project directories...
if exist "%ROOT%tradebusiness-backend" (
    echo     [OK] tradebusiness-backend exists
) else (
    echo     [ERROR] tradebusiness-backend not found
)

if exist "%ROOT%tradebusiness-admin" (
    echo     [OK] tradebusiness-admin exists
) else (
    echo     [ERROR] tradebusiness-admin not found
)

if exist "%ROOT%tradebusiness-client" (
    echo     [OK] tradebusiness-client exists
) else (
    echo     [ERROR] tradebusiness-client not found
)

echo.
echo [2] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo     [ERROR] Python not installed
) else (
    python --version
    echo     [OK] Python installed
)

echo.
echo [3] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo     [ERROR] Node.js not installed
) else (
    node --version
    echo     [OK] Node.js installed
)

echo.
echo [4] Checking backend venv...
if exist "%ROOT%tradebusiness-backend\venv\Scripts\activate.bat" (
    echo     [OK] Backend venv exists
) else (
    echo     [ERROR] Backend venv not found
    echo     Run: cd tradebusiness-backend ^&^& python -m venv venv
)

echo.
echo [5] Checking backend config...
if exist "%ROOT%tradebusiness-backend\.env" (
    echo     [OK] .env file exists
) else (
    echo     [WARNING] .env file not found
    echo     Run: create-env.bat
)

echo.
echo [6] Checking frontend dependencies...
if exist "%ROOT%tradebusiness-admin\node_modules" (
    echo     [OK] Admin dependencies installed
) else (
    echo     [WARNING] Admin dependencies not installed
    echo     Run: cd tradebusiness-admin ^&^& npm install
)

if exist "%ROOT%tradebusiness-client\node_modules" (
    echo     [OK] Client dependencies installed
) else (
    echo     [WARNING] Client dependencies not installed
    echo     Run: cd tradebusiness-client ^&^& npm install
)

echo.
echo [7] Checking ports...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo     [OK] Port 8000 is available
) else (
    echo     [WARNING] Port 8000 is in use
)

netstat -ano | findstr ":3000" >nul 2>&1
if errorlevel 1 (
    echo     [OK] Port 3000 is available
) else (
    echo     [WARNING] Port 3000 is in use
)

netstat -ano | findstr ":3001" >nul 2>&1
if errorlevel 1 (
    echo     [OK] Port 3001 is available
) else (
    echo     [WARNING] Port 3001 is in use
)

echo.
echo ========================================
echo Check Complete!
echo ========================================
echo.
echo If all checks passed, run:
echo   start-all.bat      - Start all services with checks
echo.
echo If there are errors, see STARTUP_FIX.md
echo.
pause

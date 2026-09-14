@echo off
setlocal enabledelayedexpansion

REM TradeBusiness Management System - All-in-One Startup Script

echo.
echo ========================================
echo TradeBusiness - Starting All Services
echo ========================================
echo.

REM Check if in correct directory
if not exist "tradebusiness-backend" (
    echo ERROR: Please run this script from project root
    pause
    exit /b 1
)

REM Set project root
set "PROJECT_ROOT=%~dp0"

echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed or not in PATH
    pause
    exit /b 1
)
echo Python OK

echo.
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not installed or not in PATH
    pause
    exit /b 1
)
echo Node.js OK

echo.
echo [3/6] Preparing backend...
cd /d "%PROJECT_ROOT%tradebusiness-backend"

REM Check venv
if not exist "venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv
        pause
        exit /b 1
    )

    echo Activating venv...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate venv
        pause
        exit /b 1
    )

    echo Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo.
        echo Possible solutions:
        echo 1. Check network connection
        echo 2. Try Chinese mirror:
        echo    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
        echo 3. Manual install: pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo venv exists
    call venv\Scripts\activate.bat
)

cd /d "%PROJECT_ROOT%"

echo.
echo [4/6] Preparing frontend...

REM Check admin dependencies
cd /d "%PROJECT_ROOT%tradebusiness-admin"
if not exist "node_modules" (
    echo Installing admin dependencies...
    echo This may take a few minutes...
    call npm install
    if errorlevel 1 (
        echo WARNING: Admin install failed, continuing...
    )
) else (
    echo Admin dependencies OK
)

REM Check client dependencies
cd /d "%PROJECT_ROOT%tradebusiness-client"
if not exist "node_modules" (
    echo Installing client dependencies...
    echo This may take a few minutes...
    call npm install
    if errorlevel 1 (
        echo WARNING: Client install failed, continuing...
    )
) else (
    echo Client dependencies OK
)

cd /d "%PROJECT_ROOT%"

echo.
echo [5/6] Checking database...
cd /d "%PROJECT_ROOT%tradebusiness-backend"

REM Check .env
if not exist ".env" (
    echo.
    echo ========================================
    echo WARNING: .env file not found
    echo ========================================
    echo.
    echo Creating default config...
    copy .env.example .env >nul
    echo.
    echo IMPORTANT: Edit tradebusiness-backend\.env
    echo Modify:
    echo   1. DATABASE_URL password
    echo   2. SMTP_* email config (optional)
    echo.
    pause
)

REM Check MySQL driver
echo Checking MySQL connection...
venv\Scripts\python.exe -c "import aiomysql; print('MySQL driver OK')" 2>nul
if errorlevel 1 (
    echo WARNING: MySQL driver missing, installing...
    pip install aiomysql pymysql
)

echo Initializing database...
venv\Scripts\python.exe scripts/init_db.py
if errorlevel 1 (
    echo.
    echo Database init failed, but continuing...
    echo Ensure MySQL is running and config is correct
    echo.
)

cd /d "%PROJECT_ROOT%"

echo.
echo [6/6] Starting services...
echo.
echo ========================================
echo All services starting...
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Admin:    http://localhost:3000
echo Client:   http://localhost:3001
echo.
echo Press Ctrl+C or run stop-all.bat to stop
echo.

REM Start backend
echo Starting backend service...
cd /d "%PROJECT_ROOT%tradebusiness-backend"
start "TradeBusiness-Backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Start Celery only when local Redis is available. Otherwise the API keeps its synchronous fallback.
venv\Scripts\python.exe -c "import redis; redis.Redis(host='localhost', port=6379, db=2, socket_connect_timeout=1).ping()" >nul 2>&1
if not errorlevel 1 (
    echo Starting Celery worker and beat...
    start "TradeBusiness-Celery-Worker" cmd /k "call venv\Scripts\activate.bat && celery -A app.tasks.automation_tasks:celery_app worker --loglevel=info --pool=solo"
    start "TradeBusiness-Celery-Beat" cmd /k "call venv\Scripts\activate.bat && celery -A app.tasks.automation_tasks:celery_app beat --loglevel=info"
) else (
    echo Redis unavailable, skipping Celery worker and beat. Synchronous fallback remains enabled.
)

REM Wait 3 seconds
timeout /t 3 /nobreak >nul

REM Start admin
echo Starting admin frontend...
cd /d "%PROJECT_ROOT%tradebusiness-admin"
start "TradeBusiness-Admin" cmd /k "npm run dev"

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Start client
echo Starting client frontend...
cd /d "%PROJECT_ROOT%tradebusiness-client"
start "TradeBusiness-Client" cmd /k "npm run dev"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Service URLs:
echo   Backend API:   http://localhost:8000
echo   API Docs:      http://localhost:8000/docs
echo   Admin Panel:   http://localhost:3000
echo   Client Panel:  http://localhost:3001
echo   Async Tasks:   Redis available = Celery worker/beat started automatically
echo.
echo Default accounts:
echo   Admin:
echo     Username: admin
echo     Password: Admin123
echo.
echo   Sales:
echo     Username: sales01
echo     Password: Sales123
echo.
echo Tips:
echo   - Each service runs in separate window
echo   - Close window to stop that service
echo   - Or run stop-all.bat to stop all
echo.
echo For issues, see:
echo   1. STARTUP_VERIFICATION.md - Fix report
echo   2. STARTUP_FIX.md - Troubleshooting
echo   3. QUICKSTART.md - Quick start guide
echo.

pause

@echo off
REM Start Backend Service Only

echo.
echo ========================================
echo Starting Backend Service
echo ========================================
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%tradebusiness-backend"

REM Check venv
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: venv not found
    echo Run: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check .env
if not exist ".env" (
    echo ERROR: .env file not found
    echo Run: create-env.bat
    pause
    exit /b 1
)

REM Start service
echo Starting FastAPI server...
echo URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

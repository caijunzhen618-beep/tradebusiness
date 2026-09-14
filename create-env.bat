@echo off
setlocal enabledelayedexpansion

REM Create .env configuration file

echo.
echo ========================================
echo Create .env Configuration File
echo ========================================
echo.

REM Set project path
set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%tradebusiness-backend"

REM Check backend directory
if not exist "%BACKEND_DIR%" (
    echo ERROR: tradebusiness-backend directory not found
    echo Please run from project root
    pause
    exit /b 1
)

cd /d "%BACKEND_DIR%"

REM Check .env.example
if not exist ".env.example" (
    echo ERROR: .env.example file not found
    pause
    exit /b 1
)

REM Ask if overwrite exists
if exist ".env" (
    echo WARNING: .env file already exists
    set /p OVERWRITE="Overwrite existing config? (Y/N): "
    if /i not "!OVERWRITE!"=="Y" (
        echo Operation cancelled
        pause
        exit /b 0
    )
    echo Backing up old config...
    copy .env .env.backup >nul
    echo Backed up to .env.backup
)

echo Creating .env from template...
copy .env.example .env >nul

if errorlevel 1 (
    echo ERROR: Copy failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo .env file created successfully!
echo ========================================
echo.
echo Location: %BACKEND_DIR%\.env
echo.
echo IMPORTANT: Edit .env and modify:
echo.
echo 1. Database password
echo    Find: DATABASE_URL=...YOUR_PASSWORD...
echo    Change to: DATABASE_URL=...your_password...
echo.
echo 2. (Optional) Email config
echo    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
echo.
echo 3. (Production) Security keys
echo    SECRET_KEY, JWT_SECRET_KEY
echo.
echo After config, run:
echo   start-backend.bat   - Start backend
echo   start-all.bat       - Start all services
echo.

REM Ask to edit now
set /p EDIT="Open editor to modify config now? (Y/N): "
if /i "!EDIT!"=="Y" (
    notepad .env
)

echo.
echo Press any key to close...
pause >nul

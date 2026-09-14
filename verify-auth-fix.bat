@echo off
REM Authorization Fix Verification Script
REM Run this to test if the authorization fixes are working

echo ============================================================
echo Authorization Fix Verification
echo ============================================================
echo.

cd /d "%~dp0"

echo Checking if Python is available...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ to run this verification script
    pause
    exit /b 1
)

echo.
echo Running verification tests...
echo.

python "%~dp0scripts\verify_auth_fix.py"

echo.
pause

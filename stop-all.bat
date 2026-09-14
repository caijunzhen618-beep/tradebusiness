@echo off
REM Stop All Services

echo.
echo ========================================
echo Stopping All Services
echo ========================================
echo.

echo Stopping all services...

REM Only stop processes listening on this project's service ports.
for %%p in (8000 3000 3001) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%p" ^| findstr "LISTENING"') do (
        echo Stopping PID %%a on port %%p...
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo All services stopped!
echo.
pause

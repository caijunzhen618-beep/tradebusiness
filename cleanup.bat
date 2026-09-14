@echo off
REM Clean project cache and temporary files

echo.
echo ========================================
echo   Clean Project Cache Files
echo ========================================
echo.

echo [1/5] Cleaning Python cache...
if exist "tradebusiness-backend\app\__pycache__" rmdir /s /q "tradebusiness-backend\app\__pycache__" 2>nul
if exist "tradebusiness-backend\app\**\__pycache__" rmdir /s /q "tradebusiness-backend\app\**\__pycache__" 2>nul
echo Python cache cleaned

echo.
echo [2/5] Cleaning frontend cache...
if exist "tradebusiness-admin\node_modules\.vite" rmdir /s /q "tradebusiness-admin\node_modules\.vite" 2>nul
if exist "tradebusiness-client\node_modules\.vite" rmdir /s /q "tradebusiness-client\node_modules\.vite" 2>nul
echo Frontend cache cleaned

echo.
echo [3/5] Cleaning log files...
if exist "tradebusiness-backend\logs" (
    del /q "tradebusiness-backend\logs\*.log" 2>nul
    echo Log files cleaned
) else (
    echo No log files found
)

echo.
echo [4/5] Cleaning temporary files...
del /s /q "*.pyc" 2>nul
del /s /q "*.bak" 2>nul
del /s /q "*.tmp" 2>nul
del /s /q "*~" 2>nul
echo Temporary files cleaned

echo.
echo [5/5] Cleaning Python cache directories...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo Python cache directories cleaned

echo.
echo ========================================
echo   Cleanup Complete!
echo ========================================
echo.
echo Note: node_modules folders are preserved
echo For full cleanup, manually delete:
echo   - tradebusiness-admin\node_modules
echo   - tradebusiness-client\node_modules
echo   - tradebusiness-backend\venv
echo.
pause

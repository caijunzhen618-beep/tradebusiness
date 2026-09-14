@echo off
REM 重启后端服务

echo ========================================
echo 重启后端服务
echo ========================================
echo.

REM 停止所有Python进程
echo 正在停止后端服务...
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

REM 检查是否停止成功
tasklist | find /I "python.exe" >nul
if not errorlevel 1 (
    echo 警告: Python进程仍在运行，强制停止...
    taskkill /F /IM python.exe /T >nul
)

echo 后端服务已停止

echo.
echo 正在启动后端服务...
cd /d "%~dp0tradebusiness-backend"
start "TradeBusiness-Backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo 后端服务重启完成！
echo ========================================
echo.
echo 后端服务将在新窗口中启动
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

timeout /t 3 /nobreak >nul
echo 提示：请等待3-5秒让服务完全启动
echo.

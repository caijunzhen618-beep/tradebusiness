@echo off
REM 货运代理业务管理系统 - Windows 快速启动脚本

chcp 65001 >nul
echo ================================================
echo   货运代理业务管理系统 - 开发环境启动
echo ================================================
echo.

:MENU
echo 请选择操作：
echo   1) 首次安装 - 安装所有依赖
echo   2) 启动所有服务（新窗口）
echo   3) 启动后端
echo   4) 启动管理端
echo   5) 启动客户端
echo   6) 退出
echo.

set /p choice="请输入选项 [1-6]: "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto START_ALL
if "%choice%"=="3" goto START_BACKEND
if "%choice%"=="4" goto START_ADMIN
if "%choice%"=="5" goto START_CLIENT
if "%choice%"=="6" goto EXIT

echo 无效选项
goto MENU

:INSTALL
echo.
echo ================================================
echo   安装后端依赖
echo ================================================
cd tradebusiness-backend

if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if not exist ".env" (
    echo 复制环境变量文件...
    copy .env.example .env
    echo ⚠️  请编辑 tradebusiness-backend\.env 配置数据库连接
)

cd ..

echo.
echo ================================================
echo   安装管理端依赖
echo ================================================
cd tradebusiness-admin

if not exist "node_modules" (
    echo 安装 npm 依赖...
    call npm install
) else (
    echo ✅ 管理端依赖已安装
)

cd ..

echo.
echo ================================================
echo   安装客户端依赖
echo ================================================
cd tradebusiness-client

if not exist "node_modules" (
    echo 安装 npm 依赖...
    call npm install
) else (
    echo ✅ 客户端依赖已安装
)

cd ..

echo.
echo ✅ 依赖安装完成！
echo 请重新运行此脚本启动服务
pause
goto MENU

:START_ALL
echo.
echo 启动所有服务...

start "TradeBusiness Backend" cmd /k "cd tradebusiness-backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

start "TradeBusiness Admin" cmd /k "cd tradebusiness-admin && npm run dev"
timeout /t 3 /nobreak >nul

start "TradeBusiness Client" cmd /k "cd tradebusiness-client && npm run dev"

echo.
echo ================================================
echo   所有服务已启动
echo ================================================
echo 后端 API: http://localhost:8000/docs
echo 管理端:   http://localhost:3000
echo 客户端:   http://localhost:3001
echo.
echo 默认账号：
echo   管理员: admin / Admin123
echo   业务员: sales01 / Sales123
echo ================================================
pause
goto MENU

:START_BACKEND
echo.
echo 启动后端服务...
cd tradebusiness-backend
start "TradeBusiness Backend" cmd /k "venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✅ 后端服务已启动
echo    API 文档: http://localhost:8000/docs
cd ..
pause
goto MENU

:START_ADMIN
echo.
echo 启动管理端...
cd tradebusiness-admin
start "TradeBusiness Admin" cmd /k "npm run dev"
echo ✅ 管理端已启动
echo    访问地址: http://localhost:3000
cd ..
pause
goto MENU

:START_CLIENT
echo.
echo 启动客户端...
cd tradebusiness-client
start "TradeBusiness Client" cmd /k "npm run dev"
echo ✅ 客户端已启动
echo    访问地址: http://localhost:3001
cd ..
pause
goto MENU

:EXIT
echo 退出
exit /b 0

@echo off
chcp 65001 >nul
title 后端服务

cd /d "%~dp0"

echo ========================================
echo   启动后端服务
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo [2/3] 检查虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo [创建] 虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo [3/3] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
echo [安装] 依赖检查中...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   启动FastAPI服务器
echo ========================================
echo.
echo 监听地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按Ctrl+C停止服务
echo.

python run.py

echo.
echo 后端服务已停止
pause
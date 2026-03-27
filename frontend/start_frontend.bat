@echo off
chcp 65001 >nul
title 前端服务

cd /d "%~dp0"

echo ========================================
echo   启动前端服务
echo ========================================
echo.

echo [1/2] 检查Node.js环境...
node --version
if errorlevel 1 (
    echo [错误] Node.js未安装或未添加到PATH
    pause
    exit /b 1
)

echo [2/2] 安装依赖并启动...
if not exist "node_modules" (
    echo [安装] 依赖安装中...
    call npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   启动Vite开发服务器
echo ========================================
echo.
echo 访问地址: http://localhost:3000
echo 代理地址: http://localhost:8000
echo.
echo 按Ctrl+C停止服务
echo.

npm run dev

echo.
echo 前端服务已停止
pause
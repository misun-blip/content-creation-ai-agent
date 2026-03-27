@echo off
chcp 65001 >nul
title 内容创作AI-Agent 启动器

cd /d "%~dp0"

echo ========================================
echo   内容创作AI-Agent 启动器
echo ========================================
echo.

echo [1/2] 启动后端服务...
start "后端服务" /d "%~dp0backend" cmd /k "start_backend.bat"
echo [等待] 后端启动中（15秒）...
timeout /t 15 /nobreak >nul

echo [2/2] 启动前端服务...
start "前端服务" /d "%~dp0frontend" cmd /k "start_frontend.bat"
echo [等待] 前端启动中（10秒）...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 服务地址：
echo   后端 API: http://localhost:8000
echo   API 文档: http://localhost:8000/docs
echo   前端页面: http://localhost:3000
echo.
echo 默认账号：
echo   用户名: admin
echo   密码: admin123
echo.
echo 测试步骤：
echo   1. 访问 http://localhost:8000/docs 确认后端正常
echo   2. 访问 http://localhost:3000 使用 admin/admin123 登录
echo   3. 如果登录失败，检查浏览器控制台Network标签
echo.
echo 按任意键退出...
pause >nul

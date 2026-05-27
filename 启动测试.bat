@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title 测试可视化工具启动器

cd /d "%~dp0"

echo ========================================
echo   测试可视化工具启动器
echo ========================================
echo.

REM ========== 1. 检查Python环境 ==========
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH环境变量
    echo 请先安装Python 3.9+并添加到PATH
    pause
    exit /b 1
)
python --version
echo [✓] Python环境正常
echo.

REM ========== 2. 检查并创建虚拟环境 ==========
echo [2/5] 检查虚拟环境...
cd /d "%~dp0backend"
if not exist "venv\Scripts\activate.bat" (
    echo [创建] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [✓] 虚拟环境创建成功
) else (
    echo [✓] 虚拟环境已存在
)
echo.

REM ========== 3. 激活虚拟环境并安装依赖 ==========
echo [3/5] 激活虚拟环境并检查依赖...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

echo [检查] 安装/更新后端依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    echo 请检查网络环境或稍后重试
    pause
    exit /b 1
)

echo [检查] 检查pytest和pytest-json-report...
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装pytest...
    pip install pytest==9.0.2
    if errorlevel 1 (
        echo [警告] pytest安装失败，但将继续尝试
    )
)

pip show pytest-json-report >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装pytest-json-report...
    pip install pytest-json-report
    if errorlevel 1 (
        echo [警告] pytest-json-report安装失败
        echo [提示] 测试执行API可能无法正常工作，但可视化界面仍可打开
    ) else (
        echo [✓] pytest-json-report安装成功
    )
) else (
    echo [✓] pytest-json-report已安装
)
echo.

REM ========== 4. 启动并等待后端服务 ==========
echo [4/5] 检查并启动后端服务...
cd /d "%~dp0"

set "HEALTH_URL=http://127.0.0.1:8000/health"

echo [提示] 正在确保基础依赖 (MySQL/Redis) 已启动...
docker-compose up -d mysql redis
if errorlevel 1 (
    echo [警告] 尝试启动 Docker 服务失败，如果本机已安装 MySQL/Redis 则可继续。
)

REM 先检测是否已有后端在跑
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri '%HEALTH_URL%' -TimeoutSec 2 -UseBasicParsing -Proxy $null -ErrorAction Stop; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo [✓] 检测到后端服务已在运行（http://localhost:8000）
    goto backend_ready
)

REM 如果端口已被占用但 /health 不通，说明占用者不是本项目后端（或后端启动异常）
powershell -NoProfile -Command "try { $c = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue; if ($c.TcpTestSucceeded) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo [错误] 检测到 8000 端口已被占用，但 %HEALTH_URL% 健康检查未通过。
    echo        这通常表示：8000 端口被其他程序占用，或后端启动异常未注册 /health。
    echo        请先关闭占用 8000 的进程后重试，或打开 http://localhost:8000/docs 确认当前服务是谁。
    pause
    exit /b 1
)

echo [提示] 检测到本机 8000 端口无健康后端服务，准备自动启动后端...
set "BACKEND_DIR=%~dp0backend"
set "VENV_PY=%BACKEND_DIR%\venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [错误] 未找到虚拟环境 Python: %VENV_PY%
    echo        请检查 backend\venv 是否创建成功
    pause
    exit /b 1
)

echo [启动] 使用虚拟环境启动后端: uvicorn app.main:app --host 0.0.0.0 --port 8000
start "内容创作AI-Agent 后端" "%VENV_PY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

REM 等待后端就绪（最多约 30 秒）
set "MAX_RETRY=30"
set "RETRY_COUNT=0"

:wait_backend
set /a RETRY_COUNT+=1
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri '%HEALTH_URL%' -TimeoutSec 2 -UseBasicParsing -Proxy $null -ErrorAction Stop; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo [✓] 后端服务已就绪（http://localhost:8000）
    goto backend_ready
)
if %RETRY_COUNT% GEQ %MAX_RETRY% (
    echo [警告] 尝试多次后端健康检查仍未通过，请手工确认 backend 是否成功启动。
    goto backend_ready
)
timeout /t 1 >nul
goto wait_backend

:backend_ready
echo.
echo.

REM ========== 5. 打开测试可视化网页 ==========
echo [5/5] 打开测试可视化网页...
cd /d "%~dp0"
if not exist "test-dashboard.html" (
    echo [错误] 找不到test-dashboard.html文件
    echo [提示] 请确保test-dashboard.html位于项目根目录
    pause
    exit /b 1
)

REM 获取HTML文件的完整路径
set "HTML_FILE=%~dp0test-dashboard.html"

REM 使用默认浏览器打开
start "" "%HTML_FILE%"

echo [✓] 测试可视化网页已打开
echo.

REM ========== 显示使用说明 ==========
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 使用说明：
echo   1. 测试可视化网页已在浏览器中打开
echo   2. 如果后端服务未运行，请先启动后端服务
echo   3. 在网页中选择要测试的模块
echo   4. 点击"开始测试"按钮执行测试
echo   5. 测试完成后可查看可视化图表和导出报告
echo.
echo 后端服务地址: http://localhost:8000
echo API文档地址: http://localhost:8000/docs
echo 测试API地址: http://localhost:8000/api/v1/test/run
echo.
echo 注意事项：
echo   - 确保后端服务已启动（运行backend\start_backend.bat）
echo   - 确保已安装pytest和pytest-json-report
echo   - 测试执行可能需要一些时间，请耐心等待
echo.
echo 按任意键退出...
pause >nul


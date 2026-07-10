@echo off
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist "env\.env.dev" (
    if exist "env\.env.dev.example" (
        echo [INFO] 未找到 env\.env.dev，正在从示例复制...
        copy "env\.env.dev.example" "env\.env.dev" >nul
        echo [INFO] 请编辑 env\.env.dev 后重新运行
    ) else (
        echo [ERROR] 未找到 env\.env.dev，请先配置环境文件
        pause
        exit /b 1
    )
)

:menu
cls
echo ========================================
echo   FastAPI Web Admin - uv 开发脚本
echo ========================================
echo.
echo  0. 安装/同步依赖 (uv sync)
echo  1. 启动开发服务 (uv run main.py run --env=dev)
echo  2. 生成迁移脚本 (uv run main.py revision --env=dev)
echo  3. 应用迁移 (uv run main.py upgrade --env=dev)
echo  4. 重置数据库 (uv run main.py reset --env=dev)
echo  5. 导出生产依赖 (uv export --no-dev -o requirements.txt)
echo  9. 退出
echo.
set /p option="请选择操作: "

if "%option%"=="0" goto sync_deps
if "%option%"=="1" goto start_dev
if "%option%"=="2" goto revision
if "%option%"=="3" goto upgrade
if "%option%"=="4" goto reset_db
if "%option%"=="5" goto export_req
if "%option%"=="9" exit /b 0
goto menu

:sync_deps
echo.
echo [INFO] 同步依赖...
uv sync
pause
goto menu

:start_dev
echo.
echo [INFO] 启动开发服务...
uv run main.py run --env=dev
pause
goto menu

:revision
echo.
echo [INFO] 生成迁移脚本...
uv run main.py revision --env=dev
pause
goto menu

:upgrade
echo.
echo [INFO] 应用迁移...
uv run main.py upgrade --env=dev
pause
goto menu

:reset_db
echo.
echo [WARN] 将删表重建并导入种子数据！
uv run main.py reset --env=dev
pause
goto menu

:export_req
echo.
echo [INFO] 导出生产 requirements.txt...
uv export --no-dev -o requirements.txt
pause
goto menu

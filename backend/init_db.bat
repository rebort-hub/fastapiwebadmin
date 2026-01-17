@echo off
REM 数据库初始化脚本 (Windows)

echo === 开始数据库迁移 ===

REM 1. 生成迁移文件
echo 1. 生成迁移文件...
alembic revision --autogenerate -m "initial migration"

if %errorlevel% neq 0 (
    echo ❌ 生成迁移文件失败
    exit /b 1
)

echo ✅ 迁移文件生成成功

REM 2. 执行迁移
echo 2. 执行数据库迁移...
alembic upgrade head

if %errorlevel% neq 0 (
    echo ❌ 数据库迁移失败
    exit /b 1
)

echo ✅ 数据库迁移成功
echo === 数据库初始化完成 ===
pause

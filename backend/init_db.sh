#!/bin/bash

# 数据库初始化脚本

echo "=== 开始数据库迁移 ==="

# 1. 生成迁移文件
echo "1. 生成迁移文件..."
alembic revision --autogenerate -m "initial migration"

if [ $? -ne 0 ]; then
    echo "❌ 生成迁移文件失败"
    exit 1
fi

echo "✅ 迁移文件生成成功"

# 2. 执行迁移
echo "2. 执行数据库迁移..."
alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败"
    exit 1
fi

echo "✅ 数据库迁移成功"
echo "=== 数据库初始化完成 ==="

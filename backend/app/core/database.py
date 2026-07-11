# -*- coding: utf-8 -*-
"""数据库初始化工具"""

from sqlalchemy import text

from app.config.setting import settings
from app.core.logger import log
from app.db.sqlalchemy import engine
from app.models.base import Base, DeclarativeRoot
from app.utils.import_util import ImportUtil


async def create_tables() -> None:
    """按模型创建缺失的数据表（不删表）。"""
    if not settings.SQL_DB_ENABLE:
        log.warning("数据库未启用，跳过建表")
        return

    found_models = ImportUtil.find_models(DeclarativeRoot)
    log.info(f"已加载 {len(found_models)} 个模型定义")

    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeRoot.metadata.create_all)
    log.info("数据库表结构检查/创建完成")


async def drop_tables() -> None:
    """删除所有模型对应的表（慎用）。"""
    if not settings.SQL_DB_ENABLE:
        return

    ImportUtil.find_models(DeclarativeRoot)
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeRoot.metadata.drop_all)
    log.warning("已删除所有业务表")


async def table_is_empty(table_name: str) -> bool:
    """判断表是否为空；表不存在时视为空。"""
    async with engine.connect() as conn:
        try:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
            count = result.scalar() or 0
            return count == 0
        except Exception:
            return True

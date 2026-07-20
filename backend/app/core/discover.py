# -*- coding: utf-8 -*-
"""
插件动态路由发现与注册

目录规范：
- 插件放在 ``app/plugin`` 下，顶级目录以 ``fea_`` 开头（如 ``fea_project``）
- 控制器文件名为 ``controller.py``
- 在 controller.py 模块顶层定义 APIRouter 实例（如 ``ProjectRouter = APIRouter(...)``）
- 路由前缀：``fea_xxx`` → 容器前缀 ``/xxx``
"""

import importlib
from pathlib import Path
from fastapi import APIRouter
from app.config.setting import settings
from app.core.logger import logger

PLUGIN_PREFIX = settings.PLUGIN_PREFIX
PREFIX_LEN = len(PLUGIN_PREFIX)


def get_dynamic_router() -> APIRouter:
    """扫描 plugin 目录并注册所有插件路由。"""
    logger.info("开始插件路由发现与注册")
    root_router = APIRouter()
    seen_router_ids: set[int] = set()

    try:
        base_package = importlib.import_module("app.plugin")
        base_dir = Path(next(iter(base_package.__path__)))
        pattern = f"{PLUGIN_PREFIX}*/**/controller.py"
        controller_files = sorted(base_dir.glob(pattern))
        container_routers: dict[str, APIRouter] = {}

        for file in controller_files:
            rel_path = file.relative_to(base_dir)
            path_parts = rel_path.parts
            top_module = path_parts[0]

            if not top_module.startswith(PLUGIN_PREFIX):
                continue
            suffix = top_module[PREFIX_LEN:]
            if not suffix:
                logger.error(f"跳过无效插件目录: {top_module}")
                continue
            prefix = f"/{suffix}"

            if prefix not in container_routers:
                container_routers[prefix] = APIRouter(prefix=prefix)
            container_router = container_routers[prefix]
            module_path = f"app.plugin.{'.'.join(path_parts[:-1])}.controller"

            try:
                module = importlib.import_module(module_path)
                registered = 0
                for attr_name in dir(module):
                    attr_value = getattr(module, attr_name, None)
                    if isinstance(attr_value, APIRouter):
                        router_id = id(attr_value)
                        if router_id not in seen_router_ids:
                            seen_router_ids.add(router_id)
                            container_router.include_router(attr_value)
                            registered += 1
                if registered == 0:
                    logger.warning(f"模块 {module_path} 未找到顶层 APIRouter")
            except Exception as exc:
                logger.exception(f"加载插件模块失败: {module_path} - {exc}")

        for prefix, container_router in sorted(container_routers.items()):
            root_router.include_router(container_router)
            logger.info(f"注册插件容器: {prefix} (路由数: {len(container_router.routes)})")

        logger.info(f"插件路由发现完成: {len(container_routers)} 个容器")
    except Exception as exc:
        logger.exception(f"插件路由发现失败: {exc}")

    return root_router


__all__ = ["get_dynamic_router"]

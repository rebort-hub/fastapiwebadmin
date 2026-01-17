# -*- coding: utf-8 -*-
# @author: rebort
from fastapi import APIRouter

from app.apis.system import user, menu, roles, lookup, id_center, file, health

app_router = APIRouter()

# system
app_router.include_router(user.router, prefix="/user", tags=["用户管理"])
app_router.include_router(menu.router, prefix="/menu", tags=["菜单管理"])
app_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
app_router.include_router(lookup.router, prefix="/lookup", tags=["数据字典"])
app_router.include_router(id_center.router, prefix="/idCenter", tags=["ID中心"])
app_router.include_router(file.router, prefix="/file", tags=["文件管理"])
app_router.include_router(health.router, prefix="/health", tags=["健康检查"])

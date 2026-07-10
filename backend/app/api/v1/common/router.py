# -*- coding: utf-8 -*-
"""公共路由聚合"""

from fastapi import APIRouter

from .file.controller import FileRouter
from .health.controller import HealthRouter

common_router = APIRouter()

common_router.include_router(HealthRouter)
common_router.include_router(FileRouter)

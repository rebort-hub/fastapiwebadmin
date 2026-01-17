# -*- coding: utf-8 -*-
# @author: rebort
"""健康检查和系统信息接口"""
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter
from sqlalchemy import text

from app.db import redis_pool
from app.db.sqlalchemy import async_session
from app.schemas.common import ResponseModel, HealthCheckResponse, SystemInfoResponse
from app.utils.response import HttpResponse
from config import config

router = APIRouter()


@router.get(
    "/health",
    summary="健康检查",
    description="检查系统健康状态，包括数据库和Redis连接",
    response_model=ResponseModel[HealthCheckResponse],
    responses={
        200: {
            "description": "健康检查成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": "OK",
                        "success": True,
                        "data": {
                            "status": "healthy",
                            "timestamp": "2024-01-16T10:00:00",
                            "version": "2.0",
                            "checks": {
                                "database": {"status": "up"},
                                "redis": {"status": "up"}
                            }
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    健康检查接口
    
    检查项：
    - 数据库连接状态
    - Redis连接状态
    - 系统整体状态
    
    返回：
    - status: healthy(健康) / unhealthy(不健康)
    - timestamp: 检查时间
    - version: 系统版本
    - checks: 各组件检查详情
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": str(config.SERVER_VERSION),
        "checks": {}
    }
    
    # 检查数据库
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "up"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {"status": "down", "error": str(e)}
    
    # 检查Redis
    try:
        await redis_pool.redis.ping()
        health_status["checks"]["redis"] = {"status": "up"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = {"status": "down", "error": str(e)}
    
    return await HttpResponse.success(data=health_status)


@router.get(
    "/readiness",
    summary="就绪检查",
    description="检查系统是否就绪，用于容器编排系统（如Kubernetes）",
    response_model=ResponseModel[Dict[str, Any]],
    responses={
        200: {
            "description": "就绪检查成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": "OK",
                        "success": True,
                        "data": {
                            "ready": True,
                            "timestamp": "2024-01-16T10:00:00"
                        }
                    }
                }
            }
        }
    }
)
async def readiness_check():
    """
    就绪检查接口
    
    用于 Kubernetes 等容器编排系统判断服务是否准备好接收流量
    
    返回：
    - ready: 是否就绪
    - timestamp: 检查时间
    """
    return await HttpResponse.success(data={
        "ready": True,
        "timestamp": datetime.now().isoformat()
    })


@router.get(
    "/info",
    summary="系统信息",
    description="获取系统基本信息，包括版本、配置等",
    response_model=ResponseModel[SystemInfoResponse],
    responses={
        200: {
            "description": "获取系统信息成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": "OK",
                        "success": True,
                        "data": {
                            "name": "fastapiwebadmin",
                            "version": "2.0",
                            "description": "企业级管理系统",
                            "base_url": "http://127.0.0.1:8100",
                            "api_prefix": "/api",
                            "timestamp": "2024-01-16T10:00:00"
                        }
                    }
                }
            }
        }
    }
)
async def system_info():
    """
    系统信息接口
    
    返回系统的基本信息：
    - name: 系统名称
    - version: 系统版本
    - description: 系统描述
    - base_url: 基础URL
    - api_prefix: API前缀
    - timestamp: 当前时间
    """
    info = {
        "name": "fastapiwebadmin",
        "version": str(config.SERVER_VERSION),
        "description": config.SERVER_DESC.strip(),
        "base_url": str(config.BASE_URL),
        "api_prefix": config.API_PREFIX,
        "timestamp": datetime.now().isoformat()
    }
    return await HttpResponse.success(data=info)

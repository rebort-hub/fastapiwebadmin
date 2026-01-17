# -*- coding: utf-8 -*-
# @author: rebort
"""通用响应模型"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(default=0, description="状态码，0表示成功")
    msg: str = Field(default="OK", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    success: bool = Field(default=True, description="是否成功")
    trace_id: Optional[str] = Field(default=None, description="追踪ID")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "msg": "OK",
                "data": {},
                "success": True,
                "trace_id": "abc123"
            }
        }


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="健康状态: healthy/unhealthy")
    timestamp: str = Field(description="检查时间")
    version: str = Field(description="系统版本")
    checks: dict = Field(description="各组件检查结果")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-16T10:00:00",
                "version": "2.0",
                "checks": {
                    "database": {"status": "up"},
                    "redis": {"status": "up"}
                }
            }
        }


class SystemInfoResponse(BaseModel):
    """系统信息响应"""
    name: str = Field(description="系统名称")
    version: str = Field(description="系统版本")
    description: str = Field(description="系统描述")
    base_url: str = Field(description="基础URL")
    api_prefix: str = Field(description="API前缀")
    timestamp: str = Field(description="当前时间")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "fast-element-admin",
                "version": "2.0",
                "description": "企业级管理系统",
                "base_url": "http://127.0.0.1:8100",
                "api_prefix": "/api",
                "timestamp": "2024-01-16T10:00:00"
            }
        }

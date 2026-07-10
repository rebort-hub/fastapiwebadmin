# -*- coding: utf-8 -*-
"""统一 API 响应模型"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""

    code: int = Field(default=0, description="状态码，0表示成功")
    msg: str = Field(default="OK", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    success: bool = Field(default=True, description="是否成功")
    trace_id: Optional[str] = Field(default=None, description="追踪ID")


class HealthCheckResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(description="健康状态: healthy/unhealthy")
    timestamp: str = Field(description="检查时间")
    version: str = Field(description="系统版本")
    checks: dict = Field(description="各组件检查结果")


class SystemInfoResponse(BaseModel):
    """系统信息响应"""

    name: str = Field(description="系统名称")
    version: str = Field(description="系统版本")
    description: str = Field(description="系统描述")
    base_url: str = Field(description="基础URL")
    api_prefix: str = Field(description="API前缀")
    timestamp: str = Field(description="当前时间")

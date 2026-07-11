# -*- coding: utf-8 -*-
import typing

from pydantic import BaseModel, Field

from app.common.schema import BaseSchema


class OperationLogQuery(BaseSchema):
    username: typing.Optional[str] = Field(None, description="用户名")
    request_path: typing.Optional[str] = Field(None, description="请求路径")
    request_method: typing.Optional[str] = Field(None, description="请求方式")
    request_ip: typing.Optional[str] = Field(None, description="请求IP")


class OperationLogIn(BaseModel):
    user_id: typing.Optional[int] = None
    username: typing.Optional[str] = None
    request_path: str
    request_method: str
    request_payload: typing.Optional[str] = None
    request_ip: typing.Optional[str] = None
    location: typing.Optional[str] = None
    browser: typing.Optional[str] = None
    os_name: typing.Optional[str] = None
    response_code: typing.Optional[int] = None
    response_body: typing.Optional[str] = None
    process_time: typing.Optional[str] = None
    description: typing.Optional[str] = None
    status: typing.Optional[int] = 1

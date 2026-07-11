# -*- coding: utf-8 -*-
import typing

from pydantic import BaseModel, Field

from app.common.schema import BaseSchema


class LoginRecordIn(BaseModel):
    token: typing.Optional[str] = Field(None, description="token")
    code: typing.Optional[str] = Field(None, description="账号")
    user_id: typing.Optional[int] = Field(None, description="用户id")
    user_name: typing.Optional[str] = Field(None, description="用户名称")
    logout_type: typing.Optional[str] = Field(None, description="登出类型")
    login_type: typing.Optional[str] = Field(None, description="登录类型")
    login_time: typing.Optional[str] = Field(None, description="登录时间")
    logout_time: typing.Optional[str] = Field(None, description="登出时间")
    login_ip: typing.Optional[str] = Field(None, description="登录ip")
    ret_msg: typing.Optional[str] = Field(None, description="返回信息")
    ret_code: typing.Optional[str] = Field(None, description="返回code")
    address: typing.Optional[str] = Field(None, description="地址")
    source_type: typing.Optional[str] = Field(None, description="来源")


class LoginRecordQuery(BaseSchema):
    token: typing.Optional[str] = Field(None, description="token")
    code: typing.Optional[str] = Field(None, description="账号")
    user_id: typing.Optional[int] = Field(None, description="用户id")
    user_name: typing.Optional[str] = Field(None, description="用户名称")
    logout_type: typing.Optional[str] = Field(None, description="登出类型")
    login_type: typing.Optional[str] = Field(None, description="登录类型")
    login_time: typing.Optional[str] = Field(None, description="登录时间")
    logout_time: typing.Optional[str] = Field(None, description="登出时间")
    login_ip: typing.Optional[str] = Field(None, description="登录ip")
    ret_msg: typing.Optional[str] = Field(None, description="返回信息")
    ret_code: typing.Optional[str] = Field(None, description="返回code")
    address: typing.Optional[str] = Field(None, description="地址")
    source_type: typing.Optional[str] = Field(None, description="来源")

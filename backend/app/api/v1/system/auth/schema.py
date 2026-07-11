# -*- coding: utf-8 -*-
from pydantic import BaseModel, EmailStr, Field


class CaptchaOut(BaseModel):
    enable: bool = Field(True, description="是否启用登录验证码")
    img_base: str = Field("", description="验证码图片 data-uri")
    key: str = Field("", description="验证码 key")
    register_enabled: bool = Field(False, description="是否开放自助注册")


class EmailCodeIn(BaseModel):
    username: str = Field(..., min_length=1, max_length=64, description="用户名")
    title: str = Field(..., min_length=1, max_length=32, description="邮件标题")
    mail: EmailStr = Field(..., description="邮箱地址")


class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    email: EmailStr = Field(..., description="邮箱")
    code: str | None = Field(None, max_length=16, description="邮箱验证码")
    phone: str | None = Field(None, max_length=20, description="手机号")
    nickname: str | None = Field(None, max_length=255, description="昵称")
    dept_id: int | None = Field(None, description="部门 ID")


class ForgetPasswordIn(BaseModel):
    username: str = Field(..., min_length=1, max_length=64, description="用户名或邮箱")
    email: EmailStr = Field(..., description="注册邮箱")
    code: str = Field(..., min_length=4, max_length=16, description="邮箱验证码")
    new_password: str = Field(..., min_length=6, max_length=64, description="新密码")

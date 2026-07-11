# -*- coding: utf-8 -*-
# @author: rebort
import typing

from pydantic import BaseModel, Field
from app.common.schema import BaseSchema
from app.utils.des import decrypt_rsa_password


class UserIn(BaseModel):
    id: typing.Optional[int] = Field(None, title="id", description='id')
    username: typing.Optional[str] = Field(..., title="用户名不能为空！", description='用户名')
    nickname: typing.Optional[str] = Field(..., title="用户昵称不能为空！", description='用户昵称')
    email: typing.Optional[str] = Field(None, description='邮箱')
    user_type: typing.Optional[int] = Field(None, description='用户类型')
    status: typing.Optional[int] = Field(None, description='是否禁用')
    remarks: typing.Optional[str] = Field(None, description='用户描述')
    avatar: typing.Optional[str] = Field(None, description='头像')
    tags: typing.List = Field(None, description='标签')
    roles: typing.List = Field(None, description='角色ID列表，写入 user_roles 关联表')
    password: typing.Optional[str] = Field(description='标签', default=decrypt_rsa_password("123456"))
    dept_id: typing.Optional[int] = Field(None, description='所属部门ID')


class UserUpdate(BaseModel):
    pass


class UserDel(BaseModel):
    id: int = Field(..., title="id", description='id')


class UserQuery(BaseSchema):
    username: typing.Optional[str] = Field(None, description='用户名')
    nickname: typing.Optional[str] = Field(None, description='昵称')
    user_ids: typing.List[int] = Field(None, description='用户id')
    skip_data_scope: typing.Optional[bool] = Field(False, description='跳过数据权限过滤')


class UserLogin(BaseModel):
    username: typing.Optional[str] = Field(..., description='用户名')
    password: typing.Optional[str] = Field(..., description='密码')
    captcha: typing.Optional[str] = Field(None, description='验证码')
    captcha_key: typing.Optional[str] = Field(None, description='验证码 key')


class UserResetPwd(BaseModel):
    id: int = Field(..., description='用户id')
    old_pwd: typing.Optional[str] = Field(..., description='旧密码')
    new_pwd: typing.Optional[str] = Field(..., description='新密码')
    re_new_pwd: typing.Optional[str] = Field(..., description='二次输入新密码')


class UserUpdateAvatar(BaseModel):
    id: int = Field(..., description='用户id')
    avatar: str = Field(..., description='头像URL')

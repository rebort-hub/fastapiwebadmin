# -*- coding: utf-8 -*-
import typing

from pydantic import BaseModel, Field, field_validator

from app.common.schema import BaseSchema


DATA_SCOPE_LABELS = {
    1: "仅本人数据权限",
    2: "本部门数据权限",
    3: "本部门及以下数据权限",
    4: "全部数据权限",
    5: "自定义数据权限",
}


class RoleIn(BaseModel):
    id: typing.Optional[int] = Field(None, description="角色id")
    name: str = Field(..., description="角色名称")
    role_type: int = Field(default=10, description="角色类型")
    description: typing.Optional[str] = Field(None, description="描述")
    status: typing.Optional[int] = Field(default=10, description="状态 10 启用 20 禁用")
    dept_id: typing.Optional[int] = Field(None, description="所属部门ID")
    data_scope: typing.Optional[int] = Field(None, description="数据权限范围")


class RoleQuery(BaseSchema):
    id: typing.Optional[int] = Field(None, description="角色id")
    name: typing.Optional[str] = Field(None, description="角色名称")
    role_type: typing.Optional[str] = Field(10, description="角色类型")


class RoleDel(BaseModel):
    id: int = Field(..., description="角色id")


class RoleDetailQuery(BaseModel):
    id: int = Field(..., description="角色id")


class RolePermissionIn(BaseModel):
    role_id: int = Field(..., description="角色ID")
    menu_ids: typing.List[int] = Field(default_factory=list, description="菜单ID列表")
    data_scope: int = Field(..., description="数据权限范围 1-5")
    dept_ids: typing.List[int] = Field(default_factory=list, description="自定义数据权限部门ID")

    @field_validator("data_scope")
    @classmethod
    def validate_data_scope(cls, value: int) -> int:
        if value not in DATA_SCOPE_LABELS:
            raise ValueError(f"数据权限范围必须为: {','.join(map(str, DATA_SCOPE_LABELS.keys()))}")
        return value


class RoleUserQuery(BaseModel):
    role_id: int = Field(..., description="角色ID")


class RoleUserSetIn(BaseModel):
    role_id: int = Field(..., description="角色ID")
    user_ids: typing.List[int] = Field(default_factory=list, description="关联用户ID列表")

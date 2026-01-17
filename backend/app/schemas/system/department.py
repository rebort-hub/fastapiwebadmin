# -*- coding: utf-8 -*-
# @author: rebort
import typing
from pydantic import BaseModel, Field


class DepartmentIn(BaseModel):
    id: typing.Optional[int] = Field(None, title="id", description='id')
    name: typing.Optional[str] = Field(..., title="部门名称", description='部门名称')
    parent_id: typing.Optional[int] = Field(0, description='父部门ID')
    sort: typing.Optional[int] = Field(0, description='排序')
    status: typing.Optional[int] = Field(1, description='状态 1启用 0禁用')
    description: typing.Optional[str] = Field(None, description='部门描述')


class DepartmentDel(BaseModel):
    id: int = Field(..., title="id", description='id')

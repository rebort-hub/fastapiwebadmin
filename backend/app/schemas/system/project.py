# -*- coding: utf-8 -*-
# @author: rebort
import typing
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema


class ProjectIn(BaseModel):
    id: typing.Optional[int] = Field(None, title="id", description='id')
    name: typing.Optional[str] = Field(..., title="项目名称", description='项目名称')
    description: typing.Optional[str] = Field(None, description='项目描述')


class ProjectQuery(BaseSchema):
    name: typing.Optional[str] = Field(None, description='项目名称')


class ProjectDel(BaseModel):
    id: int = Field(..., title="id", description='id')

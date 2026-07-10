# -*- coding: utf-8 -*-
# @author: rebort
import uuid
import typing

from pydantic import BaseModel, Field


class FileIn(BaseModel):
    id: str = Field(default=str(uuid.uuid4()).replace("-", ""), description="文件id")
    name: str = Field(None, description="存储的文件名")
    file_path: str = Field(None, description="文件路径")
    extend_name: str = Field(None, description="文件后缀名")
    original_name: str = Field(None, description="文件原名称")
    content_type: str = Field(None, description="文件类型")
    file_size: str = Field(None, description="文件大小")


class FileQuery(BaseModel):
    """文件查询参数"""
    page: int = Field(1, description="页码")
    pageSize: int = Field(20, description="每页数量")
    name: typing.Optional[str] = Field(None, description="文件名搜索")


class FileDown(BaseModel):
    path: str = Field(..., description="文件路径")


class FileId(BaseModel):
    id: typing.Union[int, str] = Field(..., description="文件id")

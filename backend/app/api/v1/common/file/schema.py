# -*- coding: utf-8 -*-
import uuid
import typing

from pydantic import BaseModel, Field


class FileIn(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))
    name: str | None = None
    file_path: str | None = None
    extend_name: str | None = None
    original_name: str | None = None
    content_type: str | None = None
    file_size: str | None = None
    storage_type: str | None = "local"
    file_url: str | None = None
    file_hash: str | None = None
    uploader_id: int | None = None
    uploader_name: str | None = None


class FileQuery(BaseModel):
    page: int = Field(1, description="页码")
    pageSize: int = Field(20, description="每页数量")
    name: typing.Optional[str] = Field(None, description="文件名搜索")
    storage_type: typing.Optional[str] = Field(None, description="存储类型")


class FileId(BaseModel):
    id: typing.Union[int, str] = Field(..., description="文件id")


class FileIdList(BaseModel):
    ids: list[str] = Field(..., description="文件id列表")

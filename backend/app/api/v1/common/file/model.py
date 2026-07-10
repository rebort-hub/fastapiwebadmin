# -*- coding: utf-8 -*-
from sqlalchemy import Column, String

from app.models.base import Base


class FileInfo(Base):
    """文件信息"""

    __tablename__ = "file_info"

    id = Column(String(60), nullable=False, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True, comment="存储的文件名")
    file_path = Column(String(255), nullable=True, comment="文件路径")
    extend_name = Column(String(255), nullable=True, comment="扩展名称", index=True)
    original_name = Column(String(255), nullable=True, comment="原名称")
    content_type = Column(String(255), nullable=True, comment="文件类型")
    file_size = Column(String(255), nullable=True, comment="文件大小")

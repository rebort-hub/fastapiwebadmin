# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, select

from app.api.v1.common.file.schema import FileQuery
from app.models.base import Base


class FileInfo(Base):
    """文件信息"""

    __tablename__ = "file_info"

    id = Column(String(60), nullable=False, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True, comment="存储的文件名")
    file_path = Column(String(255), nullable=True, comment="文件路径/存储key")
    extend_name = Column(String(255), nullable=True, comment="扩展名称", index=True)
    original_name = Column(String(255), nullable=True, comment="原名称")
    content_type = Column(String(255), nullable=True, comment="文件类型")
    file_size = Column(String(255), nullable=True, comment="文件大小")
    storage_type = Column(String(32), nullable=True, default="local", comment="存储类型")
    file_url = Column(String(1000), nullable=True, comment="访问URL")
    file_hash = Column(String(64), nullable=True, comment="文件MD5")
    uploader_id = Column(Integer, nullable=True, comment="上传者ID")
    uploader_name = Column(String(64), nullable=True, comment="上传者")

    @classmethod
    async def get_list(cls, params: FileQuery):
        q = [cls.enabled_flag == 1]
        if params.name:
            q.append(cls.original_name.like(f"%{params.name}%"))
        if params.storage_type:
            q.append(cls.storage_type == params.storage_type)
        stmt = select(*cls.get_table_columns()).where(*q).order_by(cls.creation_date.desc())
        return await cls.pagination(stmt)

    @classmethod
    async def statistics(cls) -> dict:
        from sqlalchemy import func

        from app.db.sqlalchemy import async_session

        async with async_session() as session:
            total = await session.scalar(
                select(func.count()).select_from(cls).where(cls.enabled_flag == 1)
            )
            size_rows = await session.execute(
                select(cls.file_size).where(cls.enabled_flag == 1)
            )
        total_size = 0
        for row in size_rows.scalars().all():
            try:
                total_size += int(float(row or 0))
            except (TypeError, ValueError):
                pass
        return {"total_count": total or 0, "total_size_kb": round(total_size, 2)}

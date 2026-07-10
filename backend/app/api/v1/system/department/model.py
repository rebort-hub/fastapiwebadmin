# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import aliased
from app.models.base import Base


class Department(Base):
    """部门表"""

    __tablename__ = "department"

    name = Column(String(100), nullable=False, comment="部门名称", index=True)
    parent_id = Column(Integer, nullable=True, comment="父部门ID", default=0)
    sort = Column(Integer, nullable=True, comment="排序", default=0)
    status = Column(Integer, nullable=True, comment="状态 1启用 0禁用", default=1)
    description = Column(String(500), nullable=True, comment="部门描述")

    @classmethod
    async def get_list(cls):
        from app.api.v1.system.user.model import User

        q = [cls.enabled_flag == 1]
        u = aliased(User)
        stmt = (
            select(
                *cls.get_table_columns(),
                u.nickname.label("created_by_name"),
                User.nickname.label("updated_by_name"),
            )
            .where(*q)
            .outerjoin(u, u.id == cls.created_by)
            .outerjoin(User, User.id == cls.updated_by)
            .order_by(cls.sort, cls.id)
        )
        result = await cls.get_result(stmt)
        return result if result else []

    @classmethod
    async def get_by_name(cls, name: str, exclude_id: int = None):
        q = [cls.name == name, cls.enabled_flag == 1]
        if exclude_id:
            q.append(cls.id != exclude_id)
        stmt = select(*cls.get_table_columns()).where(*q)
        return await cls.get_result(stmt, first=True)

    @classmethod
    async def get_children(cls, parent_id: int):
        stmt = select(*cls.get_table_columns()).where(cls.parent_id == parent_id, cls.enabled_flag == 1)
        return await cls.get_result(stmt)

# -*- coding: utf-8 -*-
import typing

from sqlalchemy import Column, Integer, String, Text, select
from sqlalchemy.orm import aliased
from app.api.v1.system.roles.schema import RoleQuery
from app.models.base import Base


class Roles(Base):
    """角色表"""

    __tablename__ = "roles"

    name = Column(String(64), nullable=True, comment="菜单名称", index=True)
    role_type = Column(Integer, nullable=False, comment="权限类型，10菜单权限，20用户组权限", index=True, default=10)
    menus = Column(Text, nullable=True, comment="菜单列表")
    description = Column(Integer, nullable=True, comment="描述")
    status = Column(Integer, nullable=True, comment="状态 10 启用 20 禁用", default=10)
    dept_id = Column(Integer, nullable=True, comment="部门ID")

    @classmethod
    async def get_list(cls, params: RoleQuery):
        from app.api.v1.system.department.model import Department
        from app.api.v1.system.user.model import User

        q = [cls.enabled_flag == 1]
        if params.id:
            q.append(cls.id == params.id)
        if params.name:
            q.append(cls.name.like(f"%{params.name}%"))
        if params.role_type:
            q.append(cls.role_type == params.role_type)
        else:
            q.append(cls.role_type == 10)

        u = aliased(User)
        d = aliased(Department)
        stmt = (
            select(
                *cls.get_table_columns(),
                u.nickname.label("created_by_name"),
                User.nickname.label("updated_by_name"),
                d.name.label("dept_name"),
            )
            .where(*q)
            .outerjoin(u, u.id == cls.created_by)
            .outerjoin(User, User.id == cls.updated_by)
            .outerjoin(d, d.id == cls.dept_id)
            .order_by(cls.id.desc())
        )
        return await cls.pagination(stmt)

    @classmethod
    async def get_roles_by_ids(cls, ids: typing.List, role_type=None):
        q = [cls.enabled_flag == 1, cls.id.in_(ids)]
        if role_type:
            q.append(cls.role_type == role_type)
        else:
            q.append(cls.role_type == 10)
        stmt = select(cls.get_table_columns()).where(*q)
        return await cls.get_result(stmt)

    @classmethod
    async def get_roles_by_name(cls, name, role_type=None):
        q = [cls.name == name, cls.enabled_flag == 1]
        if role_type:
            q.append(cls.role_type == role_type)
        else:
            q.append(cls.role_type == 10)
        stmt = select(cls.get_table_columns()).where(*q)
        return await cls.get_result(stmt, True)

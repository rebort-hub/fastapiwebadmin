# -*- coding: utf-8 -*-
import typing
from sqlalchemy import Column, Integer, JSON, String, Text, select
from sqlalchemy.orm import aliased
from app.api.v1.system.user.schema import UserQuery
from app.models.base import Base


class User(Base):
    """用户表"""

    __tablename__ = "user"

    username = Column(String(64), nullable=False, comment="用户名", index=True)
    password = Column(Text, nullable=False, comment="密码")
    email = Column(String(64), nullable=True, comment="邮箱")
    roles = Column(JSON, nullable=False, comment="用户类型")
    status = Column(Integer, nullable=False, comment="用户状态 1 启用，0 禁用", default=1)
    nickname = Column(String(255), nullable=False, comment="用户昵称")
    user_type = Column(Integer, nullable=False, comment="用户类型 10 管理人员, 20 测试人员", default=20)
    remarks = Column(String(255), nullable=False, comment="用户描述")
    avatar = Column(Text, nullable=False, comment="头像")
    tags = Column(JSON, nullable=False, comment="标签")
    dept_id = Column(Integer, nullable=True, comment="部门ID")

    @classmethod
    async def get_list(cls, params: UserQuery):
        from app.api.v1.system.department.model import Department

        q = [cls.enabled_flag == 1]
        if params.username:
            q.append(cls.username.like("%{}%".format(params.username)))
        if params.nickname:
            q.append(cls.nickname.like("%{}%".format(params.nickname)))
        if params.user_ids and isinstance(params.user_ids, list):
            q.append(cls.id.in_(params.user_ids))

        u = aliased(User)
        d = aliased(Department)
        stmt = (
            select(*cls.get_table_columns(), u.nickname.label("created_by_name"), d.name.label("dept_name"))
            .where(*q)
            .outerjoin(u, u.id == cls.created_by)
            .outerjoin(d, d.id == cls.dept_id)
            .order_by(cls.id.desc())
        )
        return await cls.pagination(stmt)

    @classmethod
    async def get_user_by_roles(cls, roles_id: int) -> typing.Any:
        stmt = select(cls.id).where(cls.roles.like(f"%{roles_id}%"), cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_user_by_name(cls, username: str):
        stmt = select(*cls.get_table_columns()).where(cls.username == username, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_user_by_email(cls, email: str):
        if not email:
            return None
        stmt = select(*cls.get_table_columns()).where(cls.email == email, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_user_by_nickname(cls, nickname: str):
        stmt = select(*cls.get_table_columns()).where(cls.nickname == nickname, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

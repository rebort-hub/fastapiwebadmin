# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import aliased

from app.api.v1.system.lookup.schema import LookupQuery, LookupValueQuery
from app.models.base import Base


class Lookup(Base):
    __tablename__ = "lookup"

    code = Column(String(64), nullable=False, index=True, comment="编码")
    description = Column(String(256), comment="描述")

    @classmethod
    async def get_list(cls, params: LookupQuery):
        from app.api.v1.system.user.model import User

        q = [cls.enabled_flag == 1]
        if params.code:
            q.append(cls.code.like(f"%{params.code}%"))
        u = aliased(User)
        stmt = (
            select(
                cls.get_table_columns(),
                u.nickname.label("created_by_name"),
                User.nickname.label("updated_by_name"),
            )
            .where(*q)
            .join(u, u.id == cls.created_by)
            .join(User, User.id == cls.updated_by)
            .order_by(cls.id.desc())
        )
        return await cls.pagination(stmt)

    @classmethod
    async def get_lookup_by_code(cls, code: str):
        stmt = select(cls).where(cls.code == code, cls.enabled_flag == 1)
        return await cls.get_result(stmt)


class LookupValue(Base):
    __tablename__ = "lookup_value"

    id = Column(Integer, primary_key=True, comment="主键")
    lookup_id = Column(Integer, nullable=False, index=True, comment="所属类型")
    lookup_code = Column(String(32), nullable=False, index=True, comment="编码")
    lookup_value = Column(String(256), comment="值")
    ext = Column(String(256), comment="拓展1")
    display_sequence = Column(Integer, comment="显示顺序")

    @classmethod
    async def get_lookup_value(cls, params: LookupValueQuery = LookupValueQuery()):
        from app.api.v1.system.user.model import User

        q = [cls.enabled_flag == 1]
        if params.code:
            q.append(Lookup.code == params.code)
        if params.lookup_id:
            q.append(cls.lookup_id == params.lookup_id)
        u = aliased(User)
        stmt = (
            select(
                cls.get_table_columns(),
                Lookup.code.label("code"),
                u.nickname.label("created_by_name"),
                User.nickname.label("updated_by_name"),
            )
            .where(*q)
            .join(Lookup, cls.lookup_id == Lookup.id)
            .join(User, cls.created_by == User.id)
            .join(u, cls.updated_by == u.id)
            .order_by(cls.display_sequence)
        )
        return await cls.get_result(stmt)

    @classmethod
    async def get_lookup_value_by_lookup_id(cls, lookup_id, lookup_code=None):
        q = [cls.lookup_id == lookup_id, cls.enabled_flag == 1]
        if lookup_code:
            q.append(cls.lookup_code == lookup_code)
        stmt = select(cls.get_table_columns()).where(*q).order_by(cls.id.desc())
        return await cls.get_result(stmt, True)

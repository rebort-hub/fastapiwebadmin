# -*- coding: utf-8 -*-
import json
import typing

from sqlalchemy import BigInteger, Column, Integer, JSON, String, Text, delete, insert, select
from sqlalchemy.orm import aliased

from app.api.v1.system.user.schema import UserQuery
from app.models.base import AssociationBase, Base


class User(Base):
    """用户表"""

    __tablename__ = "user"

    username = Column(String(64), nullable=False, comment="用户名", index=True)
    password = Column(Text, nullable=False, comment="密码")
    email = Column(String(64), nullable=True, comment="邮箱")
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

        from app.core.data_scope import DataScopeFilter

        if not getattr(params, "skip_data_scope", False):
            scope = await DataScopeFilter.for_request()
            scope_clause = scope.user_clause(cls)
            if scope_clause is not None:
                q.append(scope_clause)

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
    async def get_all_enabled(cls, limit: int = 500) -> typing.List[typing.Dict[str, typing.Any]]:
        stmt = (
            select(cls.id, cls.username, cls.nickname, cls.dept_id)
            .where(cls.enabled_flag == 1)
            .order_by(cls.id.desc())
            .limit(limit)
        )
        return await cls.get_result(stmt) or []

    @classmethod
    async def get_user_by_roles(cls, roles_id: int) -> typing.Any:
        if await UserRole.has_users_for_role(roles_id):
            user_ids = await UserRole.get_user_ids_by_role(roles_id)
            return {"id": user_ids[0]} if user_ids else None
        return None

    @classmethod
    async def get_user_ids_by_role(cls, role_id: int) -> list[int]:
        return await UserRole.get_user_ids_by_role(role_id)

    @classmethod
    async def get_users_by_role(cls, role_id: int) -> list[dict]:
        user_ids = await cls.get_user_ids_by_role(role_id)
        if not user_ids:
            return []
        stmt = (
            select(cls.id, cls.username, cls.nickname, cls.dept_id)
            .where(cls.id.in_(user_ids), cls.enabled_flag == 1)
            .order_by(cls.id.desc())
        )
        return await cls.get_result(stmt) or []

    @classmethod
    async def append_role(cls, user_id: int, role_id: int) -> None:
        await UserRole.append_role(user_id, role_id)

    @classmethod
    async def remove_role(cls, user_id: int, role_id: int) -> None:
        await UserRole.remove_role(user_id, role_id)

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


class UserRole(AssociationBase):
    """用户-角色关联表 user_roles"""

    __tablename__ = "user_roles"

    user_id = Column(BigInteger, primary_key=True, comment="用户ID")
    role_id = Column(Integer, primary_key=True, comment="角色ID", index=True)

    @classmethod
    async def get_role_ids_by_user(cls, user_id: int) -> typing.List[int]:
        if not user_id:
            return []
        stmt = select(cls.role_id).where(cls.user_id == user_id).order_by(cls.role_id)
        rows = await cls.get_result(stmt)
        return [row["role_id"] for row in rows] if rows else []

    @classmethod
    async def get_role_ids_map(cls, user_ids: typing.Iterable[int]) -> typing.Dict[int, typing.List[int]]:
        ids = [int(uid) for uid in user_ids if uid]
        if not ids:
            return {}
        stmt = select(cls.user_id, cls.role_id).where(cls.user_id.in_(ids)).order_by(cls.role_id)
        rows = await cls.get_result(stmt) or []
        mapping: dict[int, list[int]] = {uid: [] for uid in ids}
        for row in rows:
            mapping.setdefault(row["user_id"], []).append(row["role_id"])
        return mapping

    @classmethod
    async def get_user_ids_by_role(cls, role_id: int) -> typing.List[int]:
        stmt = select(cls.user_id).where(cls.role_id == role_id)
        rows = await cls.get_result(stmt)
        return [row["user_id"] for row in rows] if rows else []

    @classmethod
    async def has_users_for_role(cls, role_id: int) -> bool:
        stmt = select(cls.user_id).where(cls.role_id == role_id).limit(1)
        return bool(await cls.get_result(stmt, first=True))

    @classmethod
    async def set_user_roles(cls, user_id: int, role_ids: typing.Iterable[int]) -> None:
        await cls.execute(delete(cls).where(cls.user_id == user_id))
        unique_ids = sorted({int(rid) for rid in role_ids if rid})
        if unique_ids:
            await cls.execute(
                insert(cls),
                [{"user_id": user_id, "role_id": role_id} for role_id in unique_ids],
            )

    @classmethod
    async def set_role_users(cls, role_id: int, user_ids: typing.Iterable[int]) -> None:
        await cls.execute(delete(cls).where(cls.role_id == role_id))
        unique_ids = sorted({int(uid) for uid in user_ids if uid})
        if unique_ids:
            await cls.execute(
                insert(cls),
                [{"user_id": user_id, "role_id": role_id} for user_id in unique_ids],
            )

    @classmethod
    async def append_role(cls, user_id: int, role_id: int) -> None:
        role_ids = await cls.get_role_ids_by_user(user_id)
        if role_id not in role_ids:
            await cls.execute(insert(cls).values(user_id=user_id, role_id=role_id))

    @classmethod
    async def remove_role(cls, user_id: int, role_id: int) -> None:
        await cls.execute(delete(cls).where(cls.user_id == user_id, cls.role_id == role_id))

    @classmethod
    async def delete_by_user(cls, user_id: int) -> None:
        await cls.execute(delete(cls).where(cls.user_id == user_id))

    @classmethod
    async def delete_by_role(cls, role_id: int) -> None:
        await cls.execute(delete(cls).where(cls.role_id == role_id))

    @classmethod
    def migrate_from_legacy_json(cls, cursor, rows: typing.Iterable[tuple]) -> int:
        count = 0
        for user_id, roles_raw in rows:
            if not roles_raw:
                continue
            if isinstance(roles_raw, str):
                try:
                    role_ids = json.loads(roles_raw)
                except json.JSONDecodeError:
                    continue
            elif isinstance(roles_raw, (list, tuple)):
                role_ids = list(roles_raw)
            else:
                continue
            for role_id in role_ids:
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                        (user_id, int(role_id)),
                    )
                    count += 1
                except Exception:
                    pass
        return count

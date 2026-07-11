# -*- coding: utf-8 -*-
import typing

from sqlalchemy import Column, Integer, String, delete, insert, select
from sqlalchemy.orm import aliased

from app.api.v1.system.roles.schema import RoleQuery
from app.models.base import AssociationBase, Base


class Roles(Base):
    """角色表"""

    __tablename__ = "roles"

    name = Column(String(64), nullable=True, comment="角色名称", index=True)
    role_type = Column(Integer, nullable=False, comment="权限类型，10菜单权限，20用户组权限", index=True, default=10)
    description = Column(String(255), nullable=True, comment="描述")
    status = Column(Integer, nullable=True, comment="状态 10 启用 20 禁用", default=10)
    dept_id = Column(Integer, nullable=True, comment="部门ID")
    data_scope = Column(
        Integer,
        nullable=False,
        comment="数据权限范围(1:仅本人 2:本部门 3:本部门及以下 4:全部 5:自定义)",
        default=4,
    )

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

        from app.core.data_scope import DataScopeFilter

        scope = await DataScopeFilter.for_request()
        scope_clause = scope.role_clause(cls)
        if scope_clause is not None:
            q.append(scope_clause)

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


class RoleMenu(AssociationBase):
    """角色-菜单关联表 role_menus"""

    __tablename__ = "role_menus"

    role_id = Column(Integer, primary_key=True, comment="角色ID")
    menu_id = Column(Integer, primary_key=True, comment="菜单ID", index=True)

    @classmethod
    async def get_menu_ids_by_role(cls, role_id: int) -> typing.List[int]:
        stmt = select(cls.menu_id).where(cls.role_id == role_id).order_by(cls.menu_id)
        rows = await cls.get_result(stmt)
        return [row["menu_id"] for row in rows] if rows else []

    @classmethod
    async def get_menu_ids_by_roles(cls, role_ids: typing.Iterable[int]) -> typing.List[int]:
        ids = sorted({int(rid) for rid in role_ids if rid})
        if not ids:
            return []
        stmt = select(cls.menu_id).where(cls.role_id.in_(ids)).distinct().order_by(cls.menu_id)
        rows = await cls.get_result(stmt)
        return [row["menu_id"] for row in rows] if rows else []

    @classmethod
    async def get_menu_ids_map(cls, role_ids: typing.Iterable[int]) -> typing.Dict[int, typing.List[int]]:
        ids = sorted({int(rid) for rid in role_ids if rid})
        if not ids:
            return {}
        stmt = select(cls.role_id, cls.menu_id).where(cls.role_id.in_(ids)).order_by(cls.menu_id)
        rows = await cls.get_result(stmt) or []
        mapping: dict[int, list[int]] = {rid: [] for rid in ids}
        for row in rows:
            mapping.setdefault(row["role_id"], []).append(row["menu_id"])
        return mapping

    @classmethod
    async def set_role_menus(cls, role_id: int, menu_ids: typing.Iterable[int]) -> None:
        await cls.execute(delete(cls).where(cls.role_id == role_id))
        unique_ids = sorted({int(mid) for mid in menu_ids if mid})
        if unique_ids:
            await cls.execute(
                insert(cls),
                [{"role_id": role_id, "menu_id": menu_id} for menu_id in unique_ids],
            )

    @classmethod
    async def delete_by_role(cls, role_id: int) -> None:
        await cls.execute(delete(cls).where(cls.role_id == role_id))

    @classmethod
    def migrate_from_legacy_csv(cls, cursor, rows: typing.Iterable[tuple]) -> int:
        count = 0
        for role_id, menus_raw in rows:
            if not menus_raw:
                continue
            menu_ids = [int(mid) for mid in str(menus_raw).split(",") if str(mid).strip().isdigit()]
            for menu_id in menu_ids:
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO role_menus (role_id, menu_id) VALUES (%s, %s)",
                        (role_id, menu_id),
                    )
                    count += 1
                except Exception:
                    pass
        return count


class RoleDept(AssociationBase):
    """角色-部门关联表 role_depts（自定义数据权限）"""

    __tablename__ = "role_depts"

    role_id = Column(Integer, primary_key=True, comment="角色ID")
    dept_id = Column(Integer, primary_key=True, comment="部门ID")

    @classmethod
    async def get_dept_ids_by_role(cls, role_id: int) -> typing.List[int]:
        stmt = select(cls.dept_id).where(cls.role_id == role_id)
        rows = await cls.get_result(stmt)
        return [row["dept_id"] for row in rows] if rows else []

    @classmethod
    async def set_role_depts(cls, role_id: int, dept_ids: typing.Iterable[int]) -> None:
        await cls.execute(delete(cls).where(cls.role_id == role_id))
        unique_ids = sorted({int(dept_id) for dept_id in dept_ids if dept_id})
        if unique_ids:
            await cls.execute(
                insert(cls),
                [{"role_id": role_id, "dept_id": dept_id} for dept_id in unique_ids],
            )

    @classmethod
    async def get_role_dept_relations(cls, role_ids: typing.List[int]) -> typing.List[dict]:
        if not role_ids:
            return []
        stmt = select(cls.role_id, cls.dept_id).where(cls.role_id.in_(role_ids))
        rows = await cls.get_result(stmt) or []
        return [{"role_id": row["role_id"], "dept_id": row["dept_id"]} for row in rows]

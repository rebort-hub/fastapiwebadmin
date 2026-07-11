import traceback
import typing

from loguru import logger
from sqlalchemy import select

from app.api.v1.system.department.model import Department
from app.api.v1.system.roles.model import RoleDept, RoleMenu, Roles
from app.api.v1.system.roles.schema import (
    DATA_SCOPE_LABELS,
    RoleDel,
    RoleDetailQuery,
    RoleIn,
    RolePermissionIn,
    RoleQuery,
    RoleUserQuery,
    RoleUserSetIn,
)
from app.api.v1.system.user.model import User, UserRole


class RolesService:
    """角色类"""

    @staticmethod
    async def _attach_role_relations(rows: typing.List[dict]) -> None:
        if not rows:
            return
        role_ids = [row["id"] for row in rows]

        dept_relations = await RoleDept.get_role_dept_relations(role_ids)
        dept_ids = {item["dept_id"] for item in dept_relations}
        dept_map: dict[int, str] = {}
        if dept_ids:
            dept_stmt = select(Department.id, Department.name).where(
                Department.id.in_(dept_ids), Department.enabled_flag == 1
            )
            dept_rows = await Department.get_result(dept_stmt) or []
            dept_map = {row["id"]: row["name"] for row in dept_rows}

        role_depts: dict[int, list[dict]] = {role_id: [] for role_id in role_ids}
        for item in dept_relations:
            dept_id = item["dept_id"]
            role_depts.setdefault(item["role_id"], []).append(
                {"id": dept_id, "name": dept_map.get(dept_id, str(dept_id))}
            )

        menu_map = await RoleMenu.get_menu_ids_map(role_ids)

        for row in rows:
            row["menus"] = menu_map.get(row["id"], [])
            row.setdefault("data_scope", 4)
            row["data_scope_label"] = DATA_SCOPE_LABELS.get(row.get("data_scope") or 4, "")
            row["depts"] = role_depts.get(row["id"], [])

    @staticmethod
    async def list(params: RoleQuery) -> typing.Dict[str, typing.Any]:
        data = await Roles.get_list(params)
        await RolesService._attach_role_relations(data.get("rows", []))
        return data

    @staticmethod
    async def detail(params: RoleDetailQuery) -> typing.Dict[str, typing.Any]:
        role = await Roles.get(params.id, to_dict=True)
        if not role:
            raise ValueError("角色不存在")
        role["menus"] = await RoleMenu.get_menu_ids_by_role(params.id)
        role.setdefault("data_scope", 4)
        dept_ids = await RoleDept.get_dept_ids_by_role(params.id)
        depts = []
        if dept_ids:
            dept_stmt = select(Department.id, Department.name).where(
                Department.id.in_(dept_ids), Department.enabled_flag == 1
            )
            depts = await Department.get_result(dept_stmt) or []
        role["dept_ids"] = dept_ids
        role["depts"] = depts
        role["user_ids"] = await UserRole.get_user_ids_by_role(params.id)
        return role

    @staticmethod
    async def save_or_update(params: RoleIn) -> int:
        payload = params.model_dump(exclude_none=True)

        if params.id:
            role_info = await Roles.get(params.id)
            if role_info.name != params.name:
                if await Roles.get_roles_by_name(params.name):
                    raise ValueError("角色名已存在!")
        else:
            if await Roles.get_roles_by_name(params.name):
                raise ValueError("角色名已存在!")
            payload.setdefault("data_scope", 4)
        result = await Roles.create_or_update(payload)
        return result

    @staticmethod
    async def set_permission(params: RolePermissionIn) -> None:
        if params.role_id == 1:
            raise ValueError("系统默认角色，不可修改权限")
        role = await Roles.get(params.role_id)
        if not role:
            raise ValueError("角色不存在")

        menu_ids = sorted(set(params.menu_ids))
        await Roles.create_or_update(
            {
                "id": params.role_id,
                "data_scope": params.data_scope,
            }
        )
        await RoleMenu.set_role_menus(params.role_id, menu_ids)
        dept_ids = params.dept_ids if params.data_scope == 5 else []
        await RoleDept.set_role_depts(params.role_id, dept_ids)

    @staticmethod
    async def get_role_users(params: RoleUserQuery) -> typing.List[typing.Dict[str, typing.Any]]:
        return await User.get_users_by_role(params.role_id)

    @staticmethod
    async def get_candidate_users() -> typing.List[typing.Dict[str, typing.Any]]:
        return await User.get_all_enabled()

    @staticmethod
    async def set_role_users(params: RoleUserSetIn) -> None:
        if params.role_id == 1:
            raise ValueError("系统默认角色，不可修改关联用户")
        role = await Roles.get(params.role_id)
        if not role:
            raise ValueError("角色不存在")
        await UserRole.set_role_users(params.role_id, params.user_ids)

    @staticmethod
    async def deleted(params: RoleDel) -> int:
        try:
            if await UserRole.has_users_for_role(params.id):
                raise ValueError("有用户关联了当前角色，不允许删除!")
            await RoleMenu.delete_by_role(params.id)
            await RoleDept.set_role_depts(params.id, [])
            return await Roles.delete(params.id)
        except Exception:
            logger.error(traceback.format_exc())
            raise

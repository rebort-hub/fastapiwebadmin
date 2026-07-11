# -*- coding: utf-8 -*-
"""RBAC 权限解析：按钮权限码、角色菜单关联。"""

import typing

from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import Roles
from app.api.v1.system.roles.model import RoleMenu
from app.api.v1.system.user.model import User, UserRole

SUPER_ADMIN_USER_TYPE = 10

PERMISSION_ALIASES: dict[str, list[str]] = {
    "user:resetpwd": ["user:resetPwd"],
}


class PermissionService:
    """根据用户角色与菜单配置解析权限码。"""

    @staticmethod
    def is_super_admin(user_type: typing.Optional[int]) -> bool:
        return user_type == SUPER_ADMIN_USER_TYPE

    @staticmethod
    async def get_user_role_ids(user: typing.Union[User, typing.Dict[str, typing.Any]]) -> typing.List[int]:
        if isinstance(user, User):
            user_id = user.id
        else:
            user_id = user.get("id")
        if not user_id:
            return []
        return await UserRole.get_role_ids_by_user(user_id)

    @staticmethod
    def expand_permission_codes(codes: typing.Iterable[str]) -> list[str]:
        expanded: set[str] = set()
        for code in codes:
            if not code:
                continue
            expanded.add(code)
            for alias in PERMISSION_ALIASES.get(code, []):
                expanded.add(alias)
        return sorted(expanded)

    @staticmethod
    def has_any_permission(
        user_permissions: typing.Iterable[str],
        required_permissions: typing.Iterable[str],
    ) -> bool:
        user_set = set(user_permissions)
        for required in required_permissions:
            if required in user_set:
                return True
            canonical = PermissionService.resolve_canonical_code(required)
            if canonical in user_set:
                return True
        return False

    @staticmethod
    def resolve_canonical_code(permission: str) -> str:
        for canonical, aliases in PERMISSION_ALIASES.items():
            if permission == canonical or permission in aliases:
                return canonical
        return permission

    @staticmethod
    async def get_permission_codes(user: User) -> list[str]:
        if PermissionService.is_super_admin(user.user_type):
            buttons = await Menu.get_all_buttons() or []
            codes = {btn.get("roles") for btn in buttons if btn.get("roles")}
            return PermissionService.expand_permission_codes(codes)

        role_ids = await PermissionService.get_user_role_ids(user)
        if not role_ids:
            return []

        menu_ids = await RoleMenu.get_menu_ids_by_roles(role_ids)
        if not menu_ids:
            return []

        buttons = await Menu.get_buttons_by_ids(menu_ids) or []
        codes = {btn.get("roles") for btn in buttons if btn.get("roles")}
        return PermissionService.expand_permission_codes(codes)

    @staticmethod
    async def get_permission_codes_by_user_id(user_id: int) -> list[str]:
        user = await User.get(user_id)
        if not user:
            return []
        return await PermissionService.get_permission_codes(user)

    @staticmethod
    async def get_menu_ids_for_user(user: User) -> list[int]:
        if PermissionService.is_super_admin(user.user_type):
            all_menu = await Menu.get_menu_all()
            return [item["id"] for item in all_menu]
        role_ids = await PermissionService.get_user_role_ids(user)
        if not role_ids:
            return []
        return await RoleMenu.get_menu_ids_by_roles(role_ids)

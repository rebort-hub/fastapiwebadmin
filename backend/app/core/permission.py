# -*- coding: utf-8 -*-
"""RBAC 权限解析：按钮权限码、角色菜单关联。"""

import typing

from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import Roles
from app.api.v1.system.user.model import User

SUPER_ADMIN_USER_TYPE = 10

# 数据库权限码与前端历史命名兼容
PERMISSION_ALIASES: dict[str, list[str]] = {
    "user:resetpwd": ["user:resetPwd"],
}


class PermissionService:
    """根据用户角色与菜单配置解析权限码。"""

    @staticmethod
    def is_super_admin(user_type: typing.Optional[int]) -> bool:
        return user_type == SUPER_ADMIN_USER_TYPE

    @staticmethod
    def expand_permission_codes(codes: typing.Iterable[str]) -> list[str]:
        """展开权限别名，保证前后端标识一致。"""
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
        """用户权限满足任一要求即通过。"""
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
        """将别名映射回数据库中的权限码。"""
        for canonical, aliases in PERMISSION_ALIASES.items():
            if permission == canonical or permission in aliases:
                return canonical
        return permission

    @staticmethod
    async def get_permission_codes(user: User) -> list[str]:
        """获取用户拥有的按钮权限码列表。"""
        if PermissionService.is_super_admin(user.user_type):
            buttons = await Menu.get_all_buttons() or []
            codes = {btn.get("roles") for btn in buttons if btn.get("roles")}
            return PermissionService.expand_permission_codes(codes)

        if not user.roles:
            return []

        roles = await Roles.get_roles_by_ids(user.roles if user.roles else [])
        menu_ids: list[int] = []
        for role in roles:
            menus = role.get("menus")
            if menus:
                menu_ids.extend(int(menu_id) for menu_id in str(menus).split(",") if menu_id)

        if not menu_ids:
            return []

        buttons = await Menu.get_buttons_by_ids(list(set(menu_ids))) or []
        codes = {btn.get("roles") for btn in buttons if btn.get("roles")}
        return PermissionService.expand_permission_codes(codes)

    @staticmethod
    async def get_permission_codes_by_user_id(user_id: int) -> list[str]:
        user = await User.get(user_id)
        if not user:
            return []
        return await PermissionService.get_permission_codes(user)

# -*- coding: utf-8 -*-
"""FastAPI 依赖：登录态与接口权限校验。"""

import typing

from app.api.v1.system.user.model import User
from app.core.data_scope import set_data_scope_enabled
from app.core.permission import PermissionService
from app.exceptions.exceptions import AccessTokenFail, PermissionNotEnough
from app.utils.current_user import current_user


class AuthPermission:
    """接口权限依赖，满足任一权限码即可访问。"""

    def __init__(
        self,
        permissions: list[str] | None = None,
        check_data_scope: bool = True,
    ) -> None:
        self.permissions = permissions or []
        self.check_data_scope = check_data_scope

    async def __call__(self) -> dict[str, typing.Any]:
        set_data_scope_enabled(self.check_data_scope)
        token_user = await current_user()
        user_id = token_user.get("id")
        if not user_id:
            raise AccessTokenFail()

        user = await User.get(user_id)
        if not user:
            raise AccessTokenFail()

        if PermissionService.is_super_admin(user.user_type):
            return token_user

        if not self.permissions:
            return token_user

        user_permissions = await PermissionService.get_permission_codes(user)
        if not PermissionService.has_any_permission(user_permissions, self.permissions):
            raise PermissionNotEnough()
        return token_user


class RequireSuperAdmin:
    """仅超级管理员可访问。"""

    async def __call__(self) -> dict[str, typing.Any]:
        token_user = await current_user()
        user = await User.get(token_user.get("id"))
        if not user or not PermissionService.is_super_admin(user.user_type):
            raise PermissionNotEnough()
        return token_user

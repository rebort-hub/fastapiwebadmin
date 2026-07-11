# -*- coding: utf-8 -*-
"""数据权限范围过滤。"""

from __future__ import annotations

import typing
from contextvars import ContextVar
from dataclasses import dataclass, field

from sqlalchemy import or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.v1.system.department.model import Department
from app.api.v1.system.roles.model import Roles
from app.api.v1.system.roles.model import RoleDept
from app.api.v1.system.user.model import UserRole
from app.api.v1.system.user.model import User
from app.core.permission import PermissionService
from app.exceptions.exceptions import AccessTokenFail
from app.utils.current_user import current_user
from app.utils.dept_tree import collect_dept_descendants

DATA_SCOPE_SELF = 1
DATA_SCOPE_DEPT = 2
DATA_SCOPE_DEPT_AND_CHILD = 3
DATA_SCOPE_ALL = 4
DATA_SCOPE_CUSTOM = 5

_check_data_scope: ContextVar[bool] = ContextVar("check_data_scope", default=True)


def set_data_scope_enabled(enabled: bool) -> None:
    _check_data_scope.set(enabled)


def is_data_scope_enabled() -> bool:
    return _check_data_scope.get()


@dataclass
class DataScopeFilter:
    """当前请求用户的数据可见范围。"""

    unrestricted: bool = False
    current_user_id: typing.Optional[int] = None
    user_dept_id: typing.Optional[int] = None
    user_role_ids: typing.List[int] = field(default_factory=list)
    data_scopes: typing.Set[int] = field(default_factory=set)
    accessible_dept_ids: typing.Set[int] = field(default_factory=set)

    @classmethod
    async def for_request(cls) -> "DataScopeFilter":
        if not is_data_scope_enabled():
            return cls(unrestricted=True)

        try:
            token_user = await current_user()
        except AccessTokenFail:
            return cls(unrestricted=True)

        user_id = token_user.get("id")
        if not user_id:
            return cls(unrestricted=True)

        user = await User.get(user_id, to_dict=True)
        if not user:
            return cls(unrestricted=True)

        if PermissionService.is_super_admin(user.get("user_type")):
            return cls(unrestricted=True)

        role_ids = await UserRole.get_role_ids_by_user(user_id)
        if not role_ids:
            return cls(
                current_user_id=user_id,
                user_dept_id=user.get("dept_id"),
                data_scopes={DATA_SCOPE_SELF},
            )

        roles = await Roles.get_roles_by_ids(role_ids)
        data_scopes: set[int] = set()
        custom_dept_ids: set[int] = set()
        for role in roles:
            scope = role.get("data_scope") or DATA_SCOPE_SELF
            data_scopes.add(scope)
            if scope == DATA_SCOPE_CUSTOM:
                custom_dept_ids.update(await RoleDept.get_dept_ids_by_role(role["id"]))

        if DATA_SCOPE_ALL in data_scopes:
            return cls(unrestricted=True)

        accessible_dept_ids = await cls._resolve_accessible_dept_ids(
            data_scopes=data_scopes,
            custom_dept_ids=custom_dept_ids,
            user_dept_id=user.get("dept_id"),
        )

        return cls(
            current_user_id=user_id,
            user_dept_id=user.get("dept_id"),
            user_role_ids=role_ids,
            data_scopes=data_scopes,
            accessible_dept_ids=accessible_dept_ids,
        )

    @staticmethod
    async def _resolve_accessible_dept_ids(
        data_scopes: set[int],
        custom_dept_ids: set[int],
        user_dept_id: typing.Optional[int],
    ) -> set[int]:
        accessible: set[int] = set()
        if DATA_SCOPE_CUSTOM in data_scopes:
            accessible.update(custom_dept_ids)

        if DATA_SCOPE_DEPT in data_scopes and user_dept_id is not None:
            accessible.add(user_dept_id)

        if DATA_SCOPE_DEPT_AND_CHILD in data_scopes and user_dept_id is not None:
            all_depts = await Department.get_list() or []
            accessible.update(collect_dept_descendants(all_depts, user_dept_id))

        return accessible

    def user_clause(self, user_model=User) -> typing.Optional[ColumnElement]:
        """用户列表/关联查询过滤。"""
        if self.unrestricted:
            return None

        clauses: list[ColumnElement] = []
        if self.accessible_dept_ids:
            clauses.append(user_model.dept_id.in_(list(self.accessible_dept_ids)))

        if DATA_SCOPE_SELF in self.data_scopes and not self.accessible_dept_ids:
            clauses.append(self._self_user_clause(user_model))

        if not clauses:
            return self._self_user_clause(user_model)

        if len(clauses) == 1:
            return clauses[0]
        return or_(*clauses)

    def role_clause(self, role_model=Roles) -> typing.Optional[ColumnElement]:
        """角色列表：非超管仅可见本人绑定的角色。"""
        if self.unrestricted:
            return None
        if not self.user_role_ids:
            return role_model.id == -1
        return role_model.id.in_(self.user_role_ids)

    def dept_visible_ids(self) -> typing.Optional[set[int]]:
        """部门树过滤；None 表示不限制。"""
        if self.unrestricted:
            return None
        if self.accessible_dept_ids:
            return set(self.accessible_dept_ids)
        if DATA_SCOPE_SELF in self.data_scopes:
            if self.user_dept_id is not None:
                return {self.user_dept_id}
            return set()
        return set()

    def log_user_clause(self, user_id_column) -> typing.Optional[ColumnElement]:
        """操作日志、登录日志等按操作用户过滤。"""
        if self.unrestricted:
            return None

        if self.accessible_dept_ids:
            user_subq = select(User.id).where(
                User.enabled_flag == 1,
                User.dept_id.in_(list(self.accessible_dept_ids)),
            )
            return or_(user_id_column == self.current_user_id, user_id_column.in_(user_subq))

        return user_id_column == self.current_user_id

    def created_by_clause(self, model) -> typing.Optional[ColumnElement]:
        """通用业务表按创建人过滤。"""
        if self.unrestricted:
            return None
        if not hasattr(model, "created_by"):
            return None

        created_by = getattr(model, "created_by")
        if self.accessible_dept_ids:
            user_subq = select(User.id).where(
                User.enabled_flag == 1,
                User.dept_id.in_(list(self.accessible_dept_ids)),
            )
            return or_(created_by == self.current_user_id, created_by.in_(user_subq))

        if DATA_SCOPE_SELF in self.data_scopes or not self.data_scopes:
            return created_by == self.current_user_id

        return created_by == self.current_user_id

    def _self_user_clause(self, user_model) -> ColumnElement:
        return or_(
            user_model.id == self.current_user_id,
            user_model.created_by == self.current_user_id,
        )

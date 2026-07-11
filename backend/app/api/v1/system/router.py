# -*- coding: utf-8 -*-
"""系统核心路由聚合"""

from fastapi import APIRouter

from .auth.controller import AuthRouter
from .department.controller import DepartmentRouter
from .id_center.controller import IdCenterRouter
from .login_record.controller import LoginRecordRouter
from .operation_log.controller import OperationLogRouter
from .lookup.controller import LookupRouter
from .menu.controller import MenuRouter
from .roles.controller import RolesRouter
from .user.controller import UserRouter

system_router = APIRouter()

system_router.include_router(AuthRouter)
system_router.include_router(UserRouter)
system_router.include_router(MenuRouter)
system_router.include_router(RolesRouter)
system_router.include_router(LookupRouter)
system_router.include_router(IdCenterRouter)
system_router.include_router(DepartmentRouter)
system_router.include_router(LoginRecordRouter)
system_router.include_router(OperationLogRouter)

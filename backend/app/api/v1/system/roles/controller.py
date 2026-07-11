from fastapi import Depends

from app.core.dependencies import AuthPermission
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse
from app.api.v1.system.roles.schema import (
    RoleDel,
    RoleDetailQuery,
    RoleIn,
    RolePermissionIn,
    RoleQuery,
    RoleUserQuery,
    RoleUserSetIn,
)
from app.api.v1.system.roles.service import RolesService

RolesRouter = APIRouter(prefix="/roles", tags=["角色管理"])


@RolesRouter.post("/list", description="获取角色列表")
async def all_roles(params: RoleQuery, _auth=Depends(AuthPermission(["role:query"]))):
    data = await RolesService.list(params)
    return await HttpResponse.success(data)


@RolesRouter.post("/detail", description="获取角色详情（含权限）")
async def role_detail(
    params: RoleDetailQuery,
    _auth=Depends(AuthPermission(["role:query"], check_data_scope=False)),
):
    data = await RolesService.detail(params)
    return await HttpResponse.success(data)


@RolesRouter.post("/saveOrUpdate", description="新增或更新角色")
async def save_or_update(params: RoleIn, _auth=Depends(AuthPermission(["role:add", "role:edit"]))):
    data = await RolesService.save_or_update(params)
    return await HttpResponse.success(data)


@RolesRouter.post("/permission/setting", description="角色授权（菜单+数据权限）")
async def set_permission(
    params: RolePermissionIn,
    _auth=Depends(AuthPermission(["role:permission"], check_data_scope=False)),
):
    await RolesService.set_permission(params)
    return await HttpResponse.success()


@RolesRouter.post("/users", description="获取角色关联用户")
async def get_role_users(
    params: RoleUserQuery,
    _auth=Depends(AuthPermission(["role:query"], check_data_scope=False)),
):
    data = await RolesService.get_role_users(params)
    return await HttpResponse.success(data)


@RolesRouter.post("/candidateUsers", description="权限分配候选用户")
async def candidate_users(
    _auth=Depends(AuthPermission(["role:permission"], check_data_scope=False)),
):
    data = await RolesService.get_candidate_users()
    return await HttpResponse.success(data)


@RolesRouter.post("/setUsers", description="设置角色关联用户")
async def set_role_users(
    params: RoleUserSetIn,
    _auth=Depends(AuthPermission(["role:permission"], check_data_scope=False)),
):
    await RolesService.set_role_users(params)
    return await HttpResponse.success()


@RolesRouter.post("/deleted", description="删除角色")
async def deleted(params: RoleDel, _auth=Depends(AuthPermission(["role:delete"]))):
    data = await RolesService.deleted(params)
    return await HttpResponse.success(data)

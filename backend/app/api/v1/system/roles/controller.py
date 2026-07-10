from fastapi import Depends

from app.core.dependencies import AuthPermission
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse
from app.api.v1.system.roles.schema import RoleQuery, RoleIn, RoleDel
from app.api.v1.system.roles.service import RolesService

RolesRouter = APIRouter(prefix="/roles", tags=["角色管理"])


@RolesRouter.post('/list', description="获取角色列表")
async def all_roles(params: RoleQuery, _auth=Depends(AuthPermission(["role:query"]))):
    data = await RolesService.list(params)
    return await HttpResponse.success(data)


@RolesRouter.post('/saveOrUpdate', description="新增或更新角色")
async def save_or_update(params: RoleIn, _auth=Depends(AuthPermission(["role:add", "role:edit"]))):
    data = await RolesService.save_or_update(params)
    return await HttpResponse.success(data)


@RolesRouter.post('/deleted', description="删除角色")
async def deleted(params: RoleDel, _auth=Depends(AuthPermission(["role:delete"]))):
    data = await RolesService.deleted(params)
    return await HttpResponse.success(data)

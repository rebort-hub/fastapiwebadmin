# -*- coding: utf-8 -*-
# @author: rebort
from fastapi import Depends

from app.core.dependencies import AuthPermission
from app.corelibs.custom_router import APIRouter
from app.api.v1.system.department.schema import DepartmentIn, DepartmentDel
from app.api.v1.system.department.service import DepartmentService
from app.utils.response import HttpResponse

DepartmentRouter = APIRouter(prefix="/department", tags=["部门管理"])


@DepartmentRouter.post("/list", description="部门列表")
async def department_list():
    data = await DepartmentService.list()
    return await HttpResponse.success(data)


@DepartmentRouter.post('/saveOrUpdate', description="保存或更新部门")
async def save_or_update(
    params: DepartmentIn,
    _auth=Depends(AuthPermission(["dept:add", "dept:edit"])),
):
    await DepartmentService.save_or_update(params)
    return await HttpResponse.success()


@DepartmentRouter.post('/deleted', description="删除部门")
async def deleted(params: DepartmentDel, _auth=Depends(AuthPermission(["dept:delete"]))):
    await DepartmentService.deleted(params)
    return await HttpResponse.success()

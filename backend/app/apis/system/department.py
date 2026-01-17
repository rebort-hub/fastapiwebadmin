# -*- coding: utf-8 -*-
# @author: rebort
from app.corelibs.custom_router import APIRouter
from app.schemas.system.department import DepartmentIn, DepartmentDel
from app.services.system.department import DepartmentService
from app.utils.response import HttpResponse

router = APIRouter()


@router.post("/list", description="部门列表")
async def department_list():
    data = await DepartmentService.list()
    return await HttpResponse.success(data)


@router.post('/saveOrUpdate', description="保存或更新部门")
async def save_or_update(params: DepartmentIn):
    await DepartmentService.save_or_update(params)
    return await HttpResponse.success()


@router.post('/deleted', description="删除部门")
async def deleted(params: DepartmentDel):
    await DepartmentService.deleted(params)
    return await HttpResponse.success()

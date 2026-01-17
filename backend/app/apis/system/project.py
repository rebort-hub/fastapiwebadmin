# -*- coding: utf-8 -*-
# @author: rebort
from app.corelibs.custom_router import APIRouter
from app.schemas.system.project import ProjectQuery, ProjectIn, ProjectDel
from app.services.system.project import ProjectService
from app.utils.response import HttpResponse

router = APIRouter()


@router.post("/list", description="项目列表")
async def project_list(params: ProjectQuery):
    data = await ProjectService.list(params)
    return await HttpResponse.success(data)


@router.post('/saveOrUpdate', description="保存或更新项目")
async def save_or_update(params: ProjectIn):
    await ProjectService.save_or_update(params)
    return await HttpResponse.success()


@router.post('/deleted', description="删除项目")
async def deleted(params: ProjectDel):
    await ProjectService.deleted(params)
    return await HttpResponse.success()

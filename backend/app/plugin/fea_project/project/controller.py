# -*- coding: utf-8 -*-
# @author: rebort
from fastapi import Depends

from app.core.dependencies import AuthPermission
from app.corelibs.custom_router import APIRouter
from app.plugin.fea_project.project.schema import ProjectQuery, ProjectIn, ProjectDel
from app.plugin.fea_project.project.service import ProjectService
from app.utils.response import HttpResponse

ProjectRouter = APIRouter(tags=["项目管理"])


@ProjectRouter.post("/list", description="项目列表")
async def project_list(params: ProjectQuery, _auth=Depends(AuthPermission(["project:query"]))):
    data = await ProjectService.list(params)
    return await HttpResponse.success(data)


@ProjectRouter.post('/saveOrUpdate', description="保存或更新项目")
async def save_or_update(
    params: ProjectIn,
    _auth=Depends(AuthPermission(["project:add", "project:edit"])),
):
    await ProjectService.save_or_update(params)
    return await HttpResponse.success()


@ProjectRouter.post('/deleted', description="删除项目")
async def deleted(params: ProjectDel, _auth=Depends(AuthPermission(["project:delete"]))):
    await ProjectService.deleted(params)
    return await HttpResponse.success()

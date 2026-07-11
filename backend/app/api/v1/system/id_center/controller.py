# -*- coding: utf-8 -*-
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse

from .service import IdCenterService

IdCenterRouter = APIRouter(prefix="/idCenter", tags=["ID中心"])


@IdCenterRouter.get("/getId", description="获取全局唯一 ID")
async def get_id():
    data = await IdCenterService.get_id()
    return await HttpResponse.success(data.model_dump())

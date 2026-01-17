# -*- coding: utf-8 -*-
# @author: rebort
from app.corelibs.custom_router import APIRouter
from app.schemas.system.user import UserLoginRecordQuery
from app.services.system.login_record import LoginRecordService
from app.utils.response import HttpResponse

router = APIRouter()


@router.post("/list", description="登录记录列表")
async def login_record_list(params: UserLoginRecordQuery):
    data = await LoginRecordService.list(params)
    return await HttpResponse.success(data)

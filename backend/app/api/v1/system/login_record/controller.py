# -*- coding: utf-8 -*-
# @author: rebort
from fastapi import Depends

from app.core.dependencies import AuthPermission
from app.corelibs.custom_router import APIRouter
from app.api.v1.system.user.schema import UserLoginRecordQuery
from app.api.v1.system.login_record.service import LoginRecordService
from app.utils.response import HttpResponse

LoginRecordRouter = APIRouter(prefix="/loginRecord", tags=["登录记录"])


@LoginRecordRouter.post("/list", description="登录记录列表")
async def login_record_list(
    params: UserLoginRecordQuery,
    _auth=Depends(AuthPermission(["loginRecord:query"])),
):
    data = await LoginRecordService.list(params)
    return await HttpResponse.success(data)

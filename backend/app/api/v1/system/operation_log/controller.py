# -*- coding: utf-8 -*-
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse

from .schema import OperationLogQuery
from .service import OperationLogService

OperationLogRouter = APIRouter(prefix="/operationLog", tags=["操作日志"])


@OperationLogRouter.post("/list", description="操作日志列表")
async def operation_log_list(params: OperationLogQuery):
    data = await OperationLogService.list(params)
    return await HttpResponse.success(data)

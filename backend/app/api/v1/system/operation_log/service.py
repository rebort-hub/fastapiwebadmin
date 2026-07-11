# -*- coding: utf-8 -*-
import asyncio
import json
import time
import typing

from loguru import logger

from app.api.v1.system.operation_log.model import OperationLog
from app.api.v1.system.operation_log.schema import OperationLogIn, OperationLogQuery


class OperationLogService:
    @staticmethod
    async def create_log(data: OperationLogIn) -> None:
        try:
            payload = data.model_dump()
            if payload.get("response_body") and len(payload["response_body"]) > 4000:
                payload["response_body"] = payload["response_body"][:4000]
            if payload.get("request_payload") and len(payload["request_payload"]) > 4000:
                payload["request_payload"] = payload["request_payload"][:4000]
            await OperationLog.create(payload)
        except Exception as exc:
            logger.error(f"写入操作日志失败: {exc}")

    @staticmethod
    def create_log_async(data: OperationLogIn) -> None:
        asyncio.create_task(OperationLogService.create_log(data))

    @staticmethod
    async def list(params: OperationLogQuery) -> typing.Dict[str, typing.Any]:
        return await OperationLog.get_list(params)

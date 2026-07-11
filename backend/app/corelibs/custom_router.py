# -*- coding: utf-8 -*-
import json
import time
from typing import Callable

import fastapi
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.routing import APIRoute
from loguru import logger

from app.config.setting import settings
from app.corelibs.consts import TEST_USER_INFO
from app.db import redis_pool
from app.utils.context import AccessToken, FastApiRequest


class ContextIncludedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                body_form = await request.form()
            except Exception:
                body_form = None

            body = None
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body = await request.json()
                    except Exception:
                        try:
                            body = body_bytes.decode("utf-8")
                        except Exception:
                            body = body_bytes.decode("gb2312", errors="ignore")
            except Exception:
                pass

            request.scope.setdefault("request_form", body_form)
            request.scope.setdefault("request_body", body)
            FastApiRequest.set(request)

            start_time = time.time()
            response: Response = await original_route_handler(request)
            await _record_operation_log(request, response, self, start_time)
            return response

        return custom_route_handler


async def _record_operation_log(request: Request, response: Response, route: APIRoute, start_time: float) -> None:
    if not settings.OPERATION_LOG_RECORD:
        return
    path = request.url.path
    if request.method not in settings.OPERATION_RECORD_METHOD:
        return
    if any(path.startswith(p) for p in settings.OPERATION_LOG_IGNORE_PATHS):
        return
    referer = request.headers.get("referer") or ""
    if referer.endswith("docs") or referer.endswith("redoc"):
        return

    try:
        from app.api.v1.system.operation_log.schema import OperationLogIn
        from app.api.v1.system.operation_log.service import OperationLogService
        from app.utils.request_meta import resolve_client_ip, resolve_login_location, resolve_user_agent

        login_ip = resolve_client_ip(request)
        browser, os_name = resolve_user_agent(request)
        location = resolve_login_location(login_ip)

        user_id = None
        username = None
        token = AccessToken.get() or request.headers.get("token")
        if token:
            user_info = await redis_pool.redis.get(TEST_USER_INFO.format(token))
            if user_info:
                user_id = user_info.get("id")
                username = user_info.get("username")

        payload = request.scope.get("request_body")
        if isinstance(payload, (dict, list)):
            request_payload = json.dumps(payload, ensure_ascii=False)[:2000]
        elif payload:
            request_payload = str(payload)[:2000]
        else:
            request_payload = ""

        response_body = ""
        if hasattr(response, "body") and response.body:
            try:
                response_body = response.body.decode("utf-8", errors="ignore")[:2000]
            except Exception:
                response_body = ""

        OperationLogService.create_log_async(
            OperationLogIn(
                user_id=user_id,
                username=username,
                request_path=path,
                request_method=request.method,
                request_payload=request_payload,
                request_ip=login_ip,
                location=location,
                browser=browser or None,
                os_name=os_name or None,
                response_code=response.status_code,
                response_body=response_body,
                process_time=f"{(time.time() - start_time):.2f}s",
                description=route.summary or route.name,
                status=1 if response.status_code < 400 else 0,
            )
        )
    except Exception as exc:
        logger.error(f"操作日志记录失败: {exc}")


class APIRouter(fastapi.APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route_class = ContextIncludedRoute

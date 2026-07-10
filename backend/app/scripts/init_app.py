# -*- coding: utf-8 -*-
"""应用初始化：生命周期、中间件、路由、异常、静态资源"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app.common.enums import EnvironmentEnum
from app.config.setting import settings
from app.core.discover import get_dynamic_router
from app.corelibs import g
from app.corelibs.consts import CACHE_DAY, TEST_USER_INFO
from app.db import redis_pool
from app.exceptions.exceptions import AccessTokenFail
from app.init.exception import init_exception
from app.init.limiter import init_limiter
from app.scripts.initialize import InitializeData
from app.utils.common import get_str_uuid
from app.utils.context import AccessToken
from app.utils.response import HttpResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：数据库 → Redis → 限流器。"""
    logger.info("应用启动中...")

    try:
        if settings.SQL_DB_ENABLE:
            await InitializeData().init_db()
            logger.info("数据库初始化完成")
    except Exception as exc:
        logger.exception(f"数据库初始化失败: {exc}")
        if settings.ENVIRONMENT == EnvironmentEnum.DEV:
            logger.warning("开发环境将继续启动，请检查数据库配置")
        else:
            raise

    if settings.REDIS_ENABLE:
        redis_uri = settings.REDIS_URI or settings.computed_redis_uri
        redis_pool.init_by_uri(redis_uri)
        logger.info("Redis 连接初始化完成")

    await init_limiter(app)
    logger.info("应用启动完成")

    yield

    if redis_pool.redis:
        await redis_pool.redis.close()
    logger.info("应用已关闭")


async def _login_verification(request: Request) -> None:
    token = request.headers.get("token")
    router = request.scope.get("path", "")
    if (
        router.startswith(settings.API_PREFIX)
        and not router.startswith(f"{settings.API_PREFIX}/file")
        and router not in settings.WHITE_ROUTER
    ):
        if not token:
            raise AccessTokenFail()
        user_info = await redis_pool.redis.get(TEST_USER_INFO.format(token))
        if not user_info:
            raise AccessTokenFail()
        await redis_pool.redis.set(TEST_USER_INFO.format(token), user_info, CACHE_DAY)


def register_middlewares(app: FastAPI) -> None:
    if settings.CORS_ORIGIN_ENABLE:
        origins = settings.CORS_ORIGINS or settings.ALLOW_ORIGINS
        allow_credentials = settings.ALLOW_CREDENTIALS
        # 浏览器不允许 credentials + Allow-Origin: *
        if allow_credentials and ("*" in origins or origins == ["*"]):
            origins = [
                "http://127.0.0.1:3000",
                "http://localhost:3000",
                "http://127.0.0.1:8100",
                "http://localhost:8100",
            ]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(o) for o in origins],
            allow_credentials=allow_credentials,
            allow_methods=settings.ALLOW_METHODS,
            allow_headers=settings.ALLOW_HEADERS,
        )

    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        g.trace_id = get_str_uuid()
        start_time = time.time()
        token = request.headers.get("token")
        AccessToken.set(token)
        remote_addr = request.headers.get("X-Real-IP", request.client.host if request.client else "")
        logger.info(f"访问记录:IP:{remote_addr}-method:{request.method}-url:{request.url}")
        try:
            await _login_verification(request)
        except AccessTokenFail as err:
            return await HttpResponse.success(code=err.code, msg=err.msg)
        response = await call_next(request)
        response.headers["X-request-id"] = g.trace_id
        logger.info(f"请求耗时: {time.time() - start_time:.3f}s")
        return response


def register_routers(app: FastAPI) -> None:
    from app.api.v1.common.router import common_router
    from app.api.v1.system.router import system_router

    app.include_router(common_router, prefix=settings.API_PREFIX)
    app.include_router(system_router, prefix=settings.API_PREFIX)
    app.include_router(get_dynamic_router(), prefix=settings.API_PREFIX)


def register_files(app: FastAPI) -> None:
    if settings.STATIC_ENABLE:
        app.mount(
            f"/{settings.STATIC_DIR}",
            StaticFiles(directory=settings.STATIC_DIR),
            name=settings.STATIC_DIR,
        )


def reset_api_docs(app: FastAPI) -> None:
    from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

    @app.get(settings.DOCS_URL, include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(openapi_url="/openapi.json", title=settings.TITLE)

    @app.get(settings.REDOC_URL, include_in_schema=False)
    async def custom_redoc_html():
        return get_redoc_html(openapi_url="/openapi.json", title=settings.TITLE)


def register_app(app: FastAPI) -> None:
    """统一注册异常、中间件、路由、静态资源、文档。"""
    init_exception(app)
    register_middlewares(app)
    register_routers(app)
    register_files(app)
    reset_api_docs(app)

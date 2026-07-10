# -*- coding: utf-8 -*-
"""系统配置"""

import os
import typing
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote_plus

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.enums import EnvironmentEnum
from app.config.path_conf import BASE_DIR, ENV_DIR, FILES_DIR, LOG_DIR, STATIC_DIR

project_desc = """
    🎉 fastapiwebadmin 接口文档汇总 🎉
    ✨ 账号: admin ✨
    ✨ 密码: 123456 ✨
    ✨ 权限(scopes): admin ✨
"""


def _env_file() -> Path:
    env_name = os.getenv("ENVIRONMENT", EnvironmentEnum.DEV.value)
    return ENV_DIR / f".env.{env_name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """优先读取项目 env 文件，避免被系统同名环境变量污染。"""
        return init_settings, dotenv_settings, env_settings, file_secret_settings

    # ================================================= #
    # ******************* 项目环境 ****************** #
    # ================================================= #
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.DEV

    # ================================================= #
    # ******************* 服务器配置 ****************** #
    # ================================================= #
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8100
    BASE_URL: AnyHttpUrl = "http://127.0.0.1:8100"

    # ================================================= #
    # ******************* API 文档配置 **************** #
    # ================================================= #
    DEBUG: bool = True
    TITLE: str = "FastApiwebAdmin API"
    SERVER_DESC: str = project_desc
    SERVER_VERSION: typing.Union[int, str] = "2.0"
    VERSION: str = "2.0"
    DESCRIPTION: str = project_desc
    SUMMARY: str = "接口汇总"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    API_PREFIX: str = "/api"
    ROOT_PATH: str = ""
    GLOBAL_ENCODING: str = "utf8"

    # ================================================= #
    # ******************** 跨域配置 ******************** #
    # ================================================= #
    CORS_ORIGIN_ENABLE: bool = True
    CORS_ORIGINS: list[str] = ["*"]
    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE"]
    ALLOW_HEADERS: list[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True

    # ================================================= #
    # ******************* 登录认证配置 ****************** #
    # ================================================= #
    SECRET_KEY: str = "kPBDjVk0o3Y1wLxdODxBpjwEjo7-Euegg4kdnzFIRjc"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    WHITE_ROUTER: list[str] = [
        "/api/user/login",
        "/api/health/health",
        "/api/health/readiness",
        "/api/health/info",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    # ================================================= #
    # ******************** 数据库配置 ******************* #
    # ================================================= #
    SQL_DB_ENABLE: bool = True
    AUTO_CREATE_TABLES: bool = True
    AUTO_SEED_DATA: bool = True
    SEED_SQL_FILE: str = str(BASE_DIR / "db_script" / "db_init.sql")
    DATABASE_TYPE: Literal["mysql", "postgres", "sqlite"] = "mysql"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "123456"
    DATABASE_NAME: str = "fastapiwebadmin"
    DATABASE_ECHO: bool = False

    # 兼容旧版 .env 直连 URI（设置后优先于分项配置）
    MYSQL_DATABASE_URI: str | None = None
    MYSQL_DATABASE_URI_SYNC: str | None = None

    # ================================================= #
    # ******************** Redis 配置 ******************* #
    # ================================================= #
    REDIS_ENABLE: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = ""
    REDIS_PASSWORD: str = ""
    REDIS_DB_NAME: int = 4
    REDIS_URI: str | None = None

    # ================================================= #
    # ******************** 日志配置 ******************** #
    # ================================================= #
    LOGGER_DIR: str = "logs"
    LOGGER_NAME: str = "fastapiwebadmin.log"
    LOGGER_LEVEL: str = "INFO"
    LOGGER_ROTATION: str = "10 MB"
    LOGGER_RETENTION: str = "7 days"

    # ================================================= #
    # ******************** 静态文件 ******************** #
    # ================================================= #
    STATIC_ENABLE: bool = True
    STATIC_DIR: str = "static"
    STATIC_URL: str = "/static"
    STATIC_ROOT: Path = STATIC_DIR

    # ================================================= #
    # ******************** Celery 配置 **************** #
    # ================================================= #
    CELERY_BROKER_URL: str = "redis://localhost:6379/5"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/5"
    CELERY_BEAT_DB_URL: str | None = None
    accept_content: list[str] = ["json"]
    result_serializer: str = "json"
    timezone: str = "Asia/Shanghai"
    enable_utc: bool = False
    worker_concurrency: int = 10
    worker_prefetch_multiplier: int = 4
    worker_max_tasks_per_child: int = 100
    broker_pool_limit: int = 10
    result_backend_transport_options: dict[str, Any] = {"visibility_timeout": 3600}
    include: list[str] = [
        "app.plugin.fea_celery.tasks.common",
    ]
    task_run_pool: int = 3
    TEST_FILES_DIR: str = str(FILES_DIR)

    # ================================================= #
    # ******************* 插件配置 ******************* #
    # ================================================= #
    PLUGIN_PREFIX: str = "fea_"

    # ================================================= #
    # ******************* 计算属性 ******************* #
    # ================================================= #
    @property
    def BASEDIR(self) -> str:
        return str(BASE_DIR)

    @property
    def DATABASE_URI(self) -> str:
        if self.MYSQL_DATABASE_URI:
            return self.MYSQL_DATABASE_URI
        return self.ASYNC_DB_URI

    @property
    def DATABASE_URI_SYNC(self) -> str:
        if self.MYSQL_DATABASE_URI_SYNC:
            return self.MYSQL_DATABASE_URI_SYNC
        return self.DB_URI

    @property
    def ASYNC_DB_URI(self) -> str:
        if self.DATABASE_TYPE == "mysql":
            return (
                f"mysql+asyncmy://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
            )
        if self.DATABASE_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )
        return f"sqlite+aiosqlite:///{self.DATABASE_NAME}.db"

    @property
    def DB_URI(self) -> str:
        if self.CELERY_BEAT_DB_URL:
            return self.CELERY_BEAT_DB_URL
        if self.MYSQL_DATABASE_URI_SYNC:
            return self.MYSQL_DATABASE_URI_SYNC
        if self.DATABASE_TYPE == "mysql":
            return (
                f"mysql+pymysql://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
            )
        if self.DATABASE_TYPE == "postgres":
            return (
                f"postgresql+psycopg://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )
        return f"sqlite:///{self.DATABASE_NAME}.db"

    @property
    def broker_url(self) -> str:
        return self.CELERY_BROKER_URL

    @property
    def result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND

    @property
    def beat_db_uri(self) -> str:
        return self.DB_URI

    @property
    def computed_redis_uri(self) -> str:
        if self.REDIS_URI:
            return self.REDIS_URI
        auth = ""
        if self.REDIS_USER or self.REDIS_PASSWORD:
            auth = f"{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_NAME}"

    @property
    def FASTAPI_CONFIG(self) -> dict[str, Any]:
        return {
            "title": self.TITLE,
            "description": self.SERVER_DESC,
            "version": str(self.SERVER_VERSION),
            "debug": self.DEBUG,
            "docs_url": None,
            "redoc_url": None,
            "openapi_url": "/openapi.json",
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# -*- coding: utf-8 -*-
"""应用入口"""

import os
from typing import Annotated

import uvicorn
from fastapi import FastAPI

from app.common.enums import EnvironmentEnum


def create_app() -> FastAPI:
    from app.config.setting import get_settings
    from app.core.logger import setup_logging
    from app.scripts.init_app import lifespan, register_app

    setup_logging()
    get_settings()
    app = FastAPI(**get_settings().FASTAPI_CONFIG, lifespan=lifespan)
    register_app(app)
    return app


def _prepare_env(env: EnvironmentEnum) -> None:
    os.environ["ENVIRONMENT"] = env.value
    from app.config.setting import get_settings

    get_settings.cache_clear()


def _get_cli():
    import typer
    from alembic import command
    from alembic.config import Config

    cli = typer.Typer(name="fastapiwebadmin", help="FastAPI Web Admin 命令行工具")
    alembic_cfg = Config("alembic.ini")

    @cli.command(name="run", help="启动服务，例: uv run main.py run --env=dev")
    def run(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
    ) -> None:
        _prepare_env(env)
        from app.config.setting import get_settings

        settings = get_settings()
        typer.echo(f"启动 {settings.TITLE} ({env.value}) ...")
        uvicorn.run(
            app="main:create_app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            reload=env == EnvironmentEnum.DEV,
            factory=True,
        )

    @cli.command(name="revision", help="生成 Alembic 迁移脚本")
    def revision(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
        message: Annotated[str, typer.Option("-m", "--message", help="迁移描述")] = "迁移脚本",
    ) -> None:
        _prepare_env(env)
        command.revision(alembic_cfg, autogenerate=True, message=message)
        typer.echo("迁移脚本已生成，请检查 app/alembic/versions/ 后执行 upgrade")

    @cli.command(name="upgrade", help="应用 Alembic 迁移")
    def upgrade(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
        revision: Annotated[str, typer.Option("-r", "--revision", help="目标版本")] = "head",
    ) -> None:
        _prepare_env(env)
        command.upgrade(alembic_cfg, revision)
        typer.echo(f"迁移已应用至 {revision}")

    @cli.command(name="downgrade", help="回滚 Alembic 迁移")
    def downgrade(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
        revision: Annotated[str, typer.Option("-r", "--revision", help="目标版本")] = "-1",
    ) -> None:
        _prepare_env(env)
        if not typer.confirm(f"确定回滚至 {revision} 吗？"):
            raise typer.Exit()
        command.downgrade(alembic_cfg, revision)
        typer.echo("迁移已回滚")

    @cli.command(name="current", help="查看当前迁移版本")
    def current(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
    ) -> None:
        _prepare_env(env)
        command.current(alembic_cfg)

    @cli.command(name="history", help="查看迁移历史")
    def history(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
        verbose: Annotated[bool, typer.Option("-v", "--verbose", help="显示详情")] = False,
    ) -> None:
        _prepare_env(env)
        command.history(alembic_cfg, verbose=verbose)

    @cli.command(name="reset", help="删表重建并导入种子数据（仅开发环境）")
    def reset(
        env: Annotated[EnvironmentEnum, typer.Option("--env", help="运行环境")] = EnvironmentEnum.DEV,
    ) -> None:
        import asyncio

        if env != EnvironmentEnum.DEV:
            typer.echo("reset 仅允许在 dev 环境执行", err=True)
            raise typer.Exit(code=1)

        _prepare_env(env)
        from app.core.logger import setup_logging
        from app.scripts.initialize import InitializeData

        setup_logging()
        if not typer.confirm("将删除所有表并重建，是否继续？"):
            raise typer.Exit()
        typer.echo("正在重置数据库（删表 → 建表 → 种子数据）...")
        asyncio.run(InitializeData.reset_db())
        typer.echo("数据库重置完成，默认账号: admin / 123456")

    return cli


app = create_app()


if __name__ == "__main__":
    _get_cli()()

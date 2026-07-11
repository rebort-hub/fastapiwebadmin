from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import MetaData, engine_from_config, pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.setting import get_settings
from app.models.base import Base, DeclarativeRoot
from app.utils.import_util import ImportUtil

config = context.config
app_config = get_settings()
config.set_main_option("sqlalchemy.url", app_config.DATABASE_URI_SYNC)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 重置 metadata，避免重复注册；随后自动扫描全部 model 文件
if DeclarativeRoot.metadata.tables:
    DeclarativeRoot.metadata = MetaData()

found_models = ImportUtil.find_models(DeclarativeRoot)
target_metadata = DeclarativeRoot.metadata
print(f"自动发现 {len(found_models)} 个模型，{len(target_metadata.tables)} 张表")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

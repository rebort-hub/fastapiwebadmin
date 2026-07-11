# -*- coding: utf-8 -*-
"""应用启动时数据库初始化与种子数据导入"""

from pathlib import Path

import pymysql

from app.config.setting import settings
from app.core.database import create_tables, table_is_empty
from app.core.logger import log


class InitializeData:
    """启动时建表并在空库时导入种子数据。"""

    def __init__(self) -> None:
        self.seed_sql_file = Path(settings.SEED_SQL_FILE)

    async def init_db(self) -> None:
        if not settings.SQL_DB_ENABLE:
            log.warning("SQL_DB_ENABLE=False，跳过数据库初始化")
            return

        if settings.AUTO_SEED_DATA and await table_is_empty("user"):
            if self.seed_sql_file.exists():
                log.info(f"检测到空库，执行完整种子 SQL: {self.seed_sql_file.name}")
                success, failed = self._execute_full_sql_file(self.seed_sql_file)
                log.info(f"种子数据导入完成: 成功 {success} 条语句, 失败 {failed} 条")
                if failed == 0:
                    log.info("默认账号: admin / 123456")
                else:
                    log.warning("部分种子 SQL 执行失败，请检查日志")
                # 种子 SQL 可能不含后续新增模块，补建 ORM 中缺失的表
                if settings.AUTO_CREATE_TABLES:
                    await create_tables()
                    await self._patch_schema()
                return

        if settings.AUTO_CREATE_TABLES:
            await create_tables()
            await self._patch_schema()

    async def _patch_schema(self) -> None:
        """为已有库补充新增字段/表（非破坏性）。"""
        if not settings.SQL_DB_ENABLE:
            return
        alters = [
            "ALTER TABLE `file_info` ADD COLUMN `storage_type` varchar(32) NULL DEFAULT 'local' COMMENT '存储类型'",
            "ALTER TABLE `file_info` ADD COLUMN `file_url` varchar(1000) NULL COMMENT '访问URL'",
            "ALTER TABLE `file_info` ADD COLUMN `file_hash` varchar(64) NULL COMMENT '文件MD5'",
            "ALTER TABLE `file_info` ADD COLUMN `uploader_id` int NULL COMMENT '上传者ID'",
            "ALTER TABLE `file_info` ADD COLUMN `uploader_name` varchar(64) NULL COMMENT '上传者'",
            "ALTER TABLE `roles` ADD COLUMN `data_scope` int NOT NULL DEFAULT 4 COMMENT '数据权限范围(1:仅本人 2:本部门 3:本部门及以下 4:全部 5:自定义)'",
        ]
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS `role_depts` (
              `role_id` int NOT NULL COMMENT '角色ID',
              `dept_id` int NOT NULL COMMENT '部门ID',
              PRIMARY KEY (`role_id`, `dept_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色自定义数据权限部门'
            """,
            """
            CREATE TABLE IF NOT EXISTS `user_roles` (
              `user_id` bigint NOT NULL COMMENT '用户ID',
              `role_id` int NOT NULL COMMENT '角色ID',
              PRIMARY KEY (`user_id`, `role_id`),
              KEY `idx_user_roles_role_id` (`role_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表'
            """,
            """
            CREATE TABLE IF NOT EXISTS `role_menus` (
              `role_id` int NOT NULL COMMENT '角色ID',
              `menu_id` int NOT NULL COMMENT '菜单ID',
              PRIMARY KEY (`role_id`, `menu_id`),
              KEY `idx_role_menus_menu_id` (`menu_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单关联表'
            """,
        ]
        try:
            conn = pymysql.connect(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                charset="utf8mb4",
            )
            cursor = conn.cursor()
            for sql in alters:
                try:
                    cursor.execute(sql)
                except Exception:
                    pass
            for sql in create_tables_sql:
                try:
                    cursor.execute(sql)
                except Exception:
                    pass
            self._migrate_rbac_data(cursor)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as exc:
            log.warning(f"schema patch 跳过: {exc}")

    @staticmethod
    def _migrate_rbac_data(cursor) -> None:
        """将历史 JSON/CSV 权限数据迁移到规范关联表。"""
        from app.api.v1.system.roles.model import RoleMenu
        from app.api.v1.system.user.model import UserRole

        try:
            cursor.execute("SELECT COUNT(*) AS cnt FROM user_roles")
            user_role_count = cursor.fetchone()[0]
            if user_role_count == 0 and InitializeData._column_exists(cursor, "user", "roles"):
                cursor.execute(
                    "SELECT id, roles FROM user WHERE enabled_flag = 1 AND roles IS NOT NULL"
                )
                migrated = UserRole.migrate_from_legacy_json(cursor, cursor.fetchall())
                if migrated:
                    log.info(f"RBAC 迁移: user_roles 写入 {migrated} 条")

            cursor.execute("SELECT COUNT(*) AS cnt FROM role_menus")
            role_menu_count = cursor.fetchone()[0]
            if role_menu_count == 0 and InitializeData._column_exists(cursor, "roles", "menus"):
                cursor.execute(
                    "SELECT id, menus FROM roles WHERE enabled_flag = 1 AND menus IS NOT NULL AND menus <> ''"
                )
                migrated = RoleMenu.migrate_from_legacy_csv(cursor, cursor.fetchall())
                if migrated:
                    log.info(f"RBAC 迁移: role_menus 写入 {migrated} 条")

            InitializeData._drop_legacy_rbac_columns(cursor)
        except Exception as exc:
            log.warning(f"RBAC 数据迁移跳过: {exc}")

    @staticmethod
    def _column_exists(cursor, table: str, column: str) -> bool:
        cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", (column,))
        return cursor.fetchone() is not None

    @staticmethod
    def _drop_legacy_rbac_columns(cursor) -> None:
        """关联表有数据后，移除历史冗余字段。"""
        drops = []
        cursor.execute("SELECT COUNT(*) FROM user_roles")
        if cursor.fetchone()[0] > 0 and InitializeData._column_exists(cursor, "user", "roles"):
            drops.append("ALTER TABLE `user` DROP COLUMN `roles`")
        cursor.execute("SELECT COUNT(*) FROM role_menus")
        if cursor.fetchone()[0] > 0 and InitializeData._column_exists(cursor, "roles", "menus"):
            drops.append("ALTER TABLE `roles` DROP COLUMN `menus`")
        for sql in drops:
            try:
                cursor.execute(sql)
                log.info(f"RBAC 清理: {sql}")
            except Exception as exc:
                log.warning(f"RBAC 清理跳过: {exc}")

    def _execute_full_sql_file(self, sql_file: Path) -> tuple[int, int]:
        """执行完整 SQL 文件（含 DDL + INSERT），与 Navicat 导出格式兼容。"""
        with open(sql_file, encoding="utf-8") as f:
            sql_content = f.read()

        statements = self._split_sql_statements(sql_content)
        conn = pymysql.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            charset="utf8mb4",
        )
        cursor = conn.cursor()
        success_count = 0
        fail_count = 0

        try:
            for statement in statements:
                sql = self._normalize_statement(statement)
                if not sql:
                    continue
                try:
                    cursor.execute(sql)
                    success_count += 1
                except Exception as exc:
                    fail_count += 1
                    preview = sql[:80].replace("\n", " ")
                    log.warning(f"SQL 执行失败: {str(exc)[:200]} | {preview}...")
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return success_count, fail_count

    @staticmethod
    def _split_sql_statements(content: str) -> list[str]:
        """按语句分割 SQL，正确处理引号内的分号。"""
        statements: list[str] = []
        current: list[str] = []
        in_single = False
        in_double = False
        in_backtick = False
        i = 0
        length = len(content)

        while i < length:
            char = content[i]

            if char == "\\" and (in_single or in_double):
                current.append(char)
                if i + 1 < length:
                    current.append(content[i + 1])
                    i += 2
                continue

            if char == "'" and not in_double and not in_backtick:
                if in_single and i + 1 < length and content[i + 1] == "'":
                    current.append("''")
                    i += 2
                    continue
                in_single = not in_single
            elif char == '"' and not in_single and not in_backtick:
                in_double = not in_double
            elif char == "`" and not in_single and not in_double:
                in_backtick = not in_backtick
            elif char == ";" and not in_single and not in_double and not in_backtick:
                statement = "".join(current).strip()
                if statement and not InitializeData._is_skippable_statement(statement):
                    statements.append(statement)
                current = []
                i += 1
                continue

            current.append(char)
            i += 1

        statement = "".join(current).strip()
        if statement and not InitializeData._is_skippable_statement(statement):
            statements.append(statement)

        return statements

    @staticmethod
    def _strip_leading_comments(statement: str) -> str:
        """去掉 Navicat 导出中语句前的 -- 行注释，保留实际 SQL。"""
        lines: list[str] = []
        for line in statement.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    @staticmethod
    def _is_skippable_statement(statement: str) -> bool:
        """跳过纯注释或 Navicat 文件头块注释。"""
        cleaned = InitializeData._strip_leading_comments(statement)
        if not cleaned:
            return True
        if cleaned.startswith("/*"):
            return True
        return False

    @staticmethod
    def _normalize_statement(statement: str) -> str:
        """执行前去掉前置行注释。"""
        return InitializeData._strip_leading_comments(statement)

    @staticmethod
    async def reset_db() -> None:
        """删表重建并导入种子（CLI reset 使用）。"""
        from app.core.database import drop_tables

        await drop_tables()
        initializer = InitializeData()
        await initializer.init_db()

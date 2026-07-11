# -*- coding: utf-8 -*-
"""基于 ip2region xdb 的 IP 地理位置解析"""

import atexit
import ipaddress
from pathlib import Path

from loguru import logger

from app.config.path_conf import BASE_DIR

_searcher = None
_c_buffer = None
_init_failed = False

XDB_PATH = BASE_DIR / "assets" / "ip2region_v4.xdb"
SERVER_XDB_PATH = BASE_DIR.parent / "server" / "assets" / "ip2region_v4.xdb"


def _resolve_xdb_path() -> Path | None:
    for candidate in (XDB_PATH, SERVER_XDB_PATH):
        if candidate.is_file():
            return candidate
    return None


def _init_searcher() -> bool:
    global _searcher, _c_buffer, _init_failed
    if _init_failed:
        return False
    if _searcher is not None:
        return True
    db_path = _resolve_xdb_path()
    if not db_path:
        logger.warning(
            "ip2region 数据文件不存在，请将 ip2region_v4.xdb 放入 backend/assets/"
        )
        _init_failed = True
        return False
    try:
        import ip2region.searcher as xdb
        import ip2region.util as util

        util.verify_from_file(str(db_path))
        _c_buffer = util.load_content_from_file(str(db_path))
        _searcher = xdb.new_with_buffer(util.IPv4, _c_buffer)
        atexit.register(_close_searcher)
        return True
    except Exception as exc:
        logger.error(f"ip2region 初始化失败: {exc}")
        _init_failed = True
        return False


def _close_searcher() -> None:
    global _searcher, _c_buffer
    if _searcher is not None:
        _searcher.close()
        _searcher = None
        _c_buffer = None


def get_ip_location(ip: str | None) -> str:
    """返回地理位置字符串，格式：国家|省份|城市|运营商。"""
    if not ip or not isinstance(ip, str):
        return "无效IP"
    ip = ip.strip()
    if not ip:
        return "无效IP"
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return "无效IP"
    if ip_obj.is_private or ip_obj.is_loopback:
        return "内网IP"
    if ip_obj.version != 4:
        return "暂不支持IPv6"
    if not _init_searcher():
        return "未知"
    try:
        region = _searcher.search(ip)
        return _parse_region(region) if region else "未知"
    except Exception:
        return "未知"


def _parse_region(region: str) -> str:
    if not region:
        return "未知"
    parts = [p for p in region.split("|") if p and p != "0"]
    return "|".join(parts) if parts else "未知"

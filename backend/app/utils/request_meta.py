# -*- coding: utf-8 -*-
"""请求元数据：IP、UA、地理位置。"""

from fastapi import Request

from app.config.setting import settings
from app.utils.ip2region_util import get_ip_location


def resolve_client_ip(request: Request | None) -> str:
    if request is None:
        return ""
    forwarded = request.headers.get("X-Forwarded-For") or request.headers.get("X-Real-IP")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or ""
    return ""


def resolve_user_agent(request: Request | None) -> tuple[str, str]:
    if request is None:
        return "", ""
    try:
        from user_agents import parse

        ua = parse(request.headers.get("user-agent", ""))
        return ua.browser.family or "", ua.os.family or ""
    except Exception:
        return "", ""


def resolve_login_location(ip: str | None) -> str:
    if not settings.IP_LOCATION_ENABLED:
        return "内网IP"
    if not ip:
        return "未知"
    return get_ip_location(ip)

# -*- coding: utf-8 -*-
"""认证模块业务逻辑：验证码、账号注册/找回密码、OAuth 登录。"""

from __future__ import annotations

import json
import secrets
from typing import Any, Literal
from urllib.parse import quote, urlencode

import httpx
from fastapi import Request

from app.api.v1.system.user.model import User, UserRole
from app.config.setting import settings
from app.core.logger import log
from app.corelibs.codes import CodeEnum
from app.corelibs.consts import CAPTCHA_CODE
from app.db import redis_pool
from app.utils.captcha_util import CaptchaUtil
from app.utils.mail import EmailService
from app.utils.security import hash_password

from .schema import CaptchaOut, EmailCodeIn, ForgetPasswordIn, RegisterIn

OAuthProvider = Literal["wechat", "qq", "github", "gitee"]

_OAUTH_STATE_PREFIX = "fastapiwebadmin:oauth_state:"
_OAUTH_STATE_TTL_SECONDS = 600


class CaptchaService:
    @staticmethod
    async def get_captcha() -> CaptchaOut:
        register_enabled = settings.REGISTER_ENABLE
        if not settings.CAPTCHA_ENABLE:
            return CaptchaOut(enable=False, img_base="", key="", register_enabled=register_enabled)

        captcha_key, img_base, answer = CaptchaUtil.generate_arithmetic_captcha()
        await redis_pool.redis.set(
            CAPTCHA_CODE.format(captcha_key),
            str(answer),
            ex=settings.CAPTCHA_EXPIRE_SECONDS,
        )
        return CaptchaOut(
            enable=True,
            img_base=img_base,
            key=captcha_key,
            register_enabled=register_enabled,
        )

    @staticmethod
    async def verify_captcha(captcha_key: str | None, captcha: str | None) -> None:
        if not settings.CAPTCHA_ENABLE:
            return
        if not captcha_key or not captcha:
            raise ValueError("验证码不能为空")
        cache_key = CAPTCHA_CODE.format(captcha_key)
        cached = await redis_pool.redis.get(cache_key)
        await redis_pool.redis.delete(cache_key)
        if cached is None:
            raise ValueError("验证码已过期，请刷新后重试")
        if str(cached).strip() != str(captcha).strip():
            raise ValueError("验证码错误")


class AuthAccountService:
    @staticmethod
    async def send_email_code(params: EmailCodeIn) -> None:
        ok = await EmailService.send_email(
            username=params.username,
            title=params.title,
            mail=params.mail,
        )
        if not ok:
            raise ValueError("验证码发送失败，请检查邮箱配置或稍后重试")

    @staticmethod
    async def register(params: RegisterIn) -> None:
        if not settings.REGISTER_ENABLE:
            raise ValueError("注册功能已关闭")

        if settings.REGISTER_EMAIL_CODE_ENABLE:
            result = await EmailService.verify_code(
                username=params.username,
                mail=params.email,
                code=params.code or "",
            )
            if not result["status"]:
                raise ValueError(result["msg"])

        if await User.get_user_by_name(params.username):
            raise ValueError(CodeEnum.USERNAME_OR_EMAIL_IS_REGISTER.msg)

        if await User.get_user_by_email(params.email):
            raise ValueError("该邮箱已被注册")

        nickname = (params.nickname or params.username)[:255]
        if await User.get_user_by_nickname(nickname):
            raise ValueError("用户昵称已存在")

        dept_id = params.dept_id if params.dept_id is not None else settings.REGISTER_DEFAULT_DEPT_ID
        user = await User.create(
            {
                "username": params.username,
                "password": hash_password(params.password),
                "email": params.email,
                "nickname": nickname,
                "user_type": 20,
                "status": 1,
                "remarks": "自助注册",
                "avatar": "",
                "tags": [],
                "dept_id": dept_id,
            }
        )
        user_id = user.id if hasattr(user, "id") else user.get("id")
        await UserRole.set_user_roles(user_id, settings.REGISTER_DEFAULT_ROLE_IDS)

    @staticmethod
    async def forget_password(params: ForgetPasswordIn) -> None:
        result = await EmailService.verify_code(
            username=params.username,
            mail=params.email,
            code=params.code,
        )
        if not result["status"]:
            raise ValueError(result["msg"])

        user_info = await User.get_user_by_email(params.email)
        if not user_info:
            raise ValueError("该邮箱未注册或未绑定账号")

        await User.update(
            {
                "id": user_info["id"],
                "password": hash_password(params.new_password),
            }
        )


class OAuthService:
    @staticmethod
    def callback_url(request: Request, provider: OAuthProvider) -> str:
        root = str(request.base_url).rstrip("/")
        return f"{root}{settings.API_PREFIX}/auth/oauth/{provider}/callback"

    @staticmethod
    def error_redirect(frontend_base: str, message: str) -> str:
        sep = "&" if "?" in frontend_base else "?"
        return f"{frontend_base}{sep}oauth_error={quote(message, safe='')}"

    @staticmethod
    def success_redirect(frontend_base: str, token: str) -> str:
        query = urlencode(
            {
                "access_token": token,
                "refresh_token": token,
                "token_type": "bearer",
            }
        )
        sep = "&" if "?" in frontend_base else "?"
        return f"{frontend_base}{sep}{query}"

    @staticmethod
    async def save_state(*, state: str, provider: OAuthProvider, frontend_redirect: str) -> None:
        await redis_pool.redis.set(
            f"{_OAUTH_STATE_PREFIX}{state}",
            {"provider": provider, "frontend_redirect": frontend_redirect},
            ex=_OAUTH_STATE_TTL_SECONDS,
        )

    @staticmethod
    def build_authorize_url(*, provider: OAuthProvider, callback_url: str, state: str) -> str:
        client_id, _ = OAuthService._require_credentials(provider)
        if provider == "github":
            params = {
                "client_id": client_id,
                "redirect_uri": callback_url,
                "scope": "user:email",
                "state": state,
            }
            return "https://github.com/login/oauth/authorize?" + urlencode(params)
        if provider == "gitee":
            params = {
                "client_id": client_id,
                "redirect_uri": callback_url,
                "response_type": "code",
                "state": state,
            }
            return "https://gitee.com/oauth/authorize?" + urlencode(params)
        if provider == "wechat":
            params = {
                "appid": client_id,
                "redirect_uri": callback_url,
                "response_type": "code",
                "scope": "snsapi_login",
                "state": state,
            }
            return "https://open.weixin.qq.com/connect/qrconnect?" + urlencode(params) + "#wechat_redirect"
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": callback_url,
            "state": state,
            "scope": "get_user_info",
        }
        return "https://graph.qq.com/oauth2.0/authorize?" + urlencode(params)

    @staticmethod
    async def complete_login(
        *,
        request: Request,
        provider: OAuthProvider,
        code: str,
        state: str,
    ) -> tuple[str, str]:
        raw = await redis_pool.redis.get(f"{_OAUTH_STATE_PREFIX}{state}")
        if not raw:
            raise ValueError("登录状态已失效，请重试")
        payload = raw if isinstance(raw, dict) else json.loads(raw)
        if payload.get("provider") != provider:
            raise ValueError("OAuth 状态不匹配")

        frontend = str(payload.get("frontend_redirect") or "").strip()
        if not frontend:
            raise ValueError("缺少前端回调地址")

        callback = OAuthService.callback_url(request, provider)
        client_id, client_secret = OAuthService._require_credentials(provider)

        if provider == "github":
            token_data = await OAuthService._http_json(
                "POST",
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": callback,
                },
            )
            access = token_data.get("access_token")
            if not access:
                raise ValueError(token_data.get("error_description") or "GitHub 换取令牌失败")
            profile = await OAuthService._http_json(
                "GET",
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access}", "Accept": "application/json"},
            )
            unique_id = str(profile.get("login") or profile.get("id"))
            display_name = str(profile.get("name") or unique_id)
        elif provider == "gitee":
            query = urlencode(
                {
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": callback,
                }
            )
            token_data = await OAuthService._http_json("GET", f"https://gitee.com/oauth/token?{query}")
            access = token_data.get("access_token")
            if not access:
                raise ValueError(token_data.get("error_description") or "Gitee 换取令牌失败")
            profile = await OAuthService._http_json("GET", "https://gitee.com/api/v5/user", params={"access_token": access})
            unique_id = str(profile.get("login") or profile.get("id"))
            display_name = str(profile.get("name") or unique_id)
        elif provider == "wechat":
            query = urlencode(
                {
                    "appid": client_id,
                    "secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                }
            )
            token_data = await OAuthService._http_json("GET", f"https://api.weixin.qq.com/sns/oauth2/access_token?{query}")
            access = token_data.get("access_token")
            openid = token_data.get("openid")
            if not access or not openid:
                raise ValueError(token_data.get("errmsg") or "微信换取令牌失败")
            profile_query = urlencode({"access_token": access, "openid": openid, "lang": "zh_CN"})
            profile = await OAuthService._http_json("GET", f"https://api.weixin.qq.com/sns/userinfo?{profile_query}")
            unique_id = str(profile.get("unionid") or openid)
            display_name = str(profile.get("nickname") or "wechat")
        else:
            query = urlencode(
                {
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": callback,
                }
            )
            text = await OAuthService._http_text("GET", f"https://graph.qq.com/oauth2.0/token?{query}")
            parts = dict(part.split("=", 1) for part in text.split("&") if "=" in part)
            access = parts.get("access_token")
            if not access:
                raise ValueError("QQ 换取 access_token 失败")
            me = await OAuthService._http_json(
                "GET",
                "https://graph.qq.com/oauth2.0/me",
                params={"access_token": access, "fmt": "json"},
            )
            openid = me.get("openid")
            if not openid:
                raise ValueError("QQ 获取 openid 失败")
            profile = await OAuthService._http_json(
                "GET",
                "https://graph.qq.com/user/get_user_info",
                params={"access_token": access, "oauth_consumer_key": client_id, "openid": openid},
            )
            unique_id = str(openid)
            display_name = str(profile.get("nickname") or "qq")

        user = await OAuthService._ensure_user(provider, unique_id, display_name)
        if user.status in (1, True, "1"):
            raise ValueError("用户已被禁用")

        from app.api.v1.system.user.service import UserService

        session = await UserService.create_login_session(user)
        await redis_pool.redis.delete(f"{_OAUTH_STATE_PREFIX}{state}")
        return session["token"], frontend

    @staticmethod
    def _require_credentials(provider: OAuthProvider) -> tuple[str, str]:
        mapping = {
            "github": (settings.OAUTH_GITHUB_CLIENT_ID, settings.OAUTH_GITHUB_CLIENT_SECRET),
            "gitee": (settings.OAUTH_GITEE_CLIENT_ID, settings.OAUTH_GITEE_CLIENT_SECRET),
            "wechat": (settings.OAUTH_WECHAT_OPEN_APP_ID, settings.OAUTH_WECHAT_OPEN_APP_SECRET),
            "qq": (settings.OAUTH_QQ_APP_ID, settings.OAUTH_QQ_APP_SECRET),
        }
        client_id, client_secret = mapping[provider]
        if not client_id or not client_secret:
            raise ValueError(f"{provider} OAuth 未配置客户端密钥")
        return client_id, client_secret

    @staticmethod
    async def _http_json(method: str, url: str, **kwargs: Any) -> Any:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def _http_text(method: str, url: str, **kwargs: Any) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.text

    @staticmethod
    def _username_for_oauth(provider: OAuthProvider, unique_id: str) -> str:
        raw = f"oauth_{provider}_{unique_id}"
        raw = "".join(char if char.isalnum() or char in "_-." else "_" for char in raw)[:32]
        if len(raw) < 3:
            raw = (raw + "usr")[:32]
        if not raw[0].isalpha():
            raw = f"o{raw[:31]}"
        return raw

    @staticmethod
    async def _ensure_user(provider: OAuthProvider, unique_id: str, display_name: str) -> User:
        username = OAuthService._username_for_oauth(provider, unique_id)
        existing = await User.get_user_by_name(username)
        if existing:
            user = await User.get(existing["id"])
            if user:
                return user

        password = hash_password(secrets.token_urlsafe(16))
        await User.create_or_update(
            {
                "username": username,
                "nickname": (display_name or username)[:255],
                "password": password,
                "user_type": 20,
                "status": 1,
                "remarks": f"OAuth {provider}",
                "avatar": "",
                "email": f"{username}@oauth.local",
                "tags": [],
            }
        )
        created = await User.get_user_by_name(username)
        if not created:
            raise ValueError("OAuth 自动注册失败")
        await UserRole.set_user_roles(created["id"], settings.OAUTH_DEFAULT_ROLE_IDS)
        user = await User.get(created["id"])
        if not user:
            raise ValueError("OAuth 自动注册失败")
        log.info(f"OAuth 自动注册用户: {username} ({provider})")
        return user

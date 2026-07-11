# -*- coding: utf-8 -*-
import secrets

from fastapi import Query, Request
from fastapi.responses import RedirectResponse

from app.config.setting import settings
from app.corelibs.custom_router import APIRouter
from app.db import redis_pool
from app.utils.response import HttpResponse

from .schema import EmailCodeIn, ForgetPasswordIn, RegisterIn
from .service import AuthAccountService, CaptchaService, OAuthProvider, OAuthService

AuthRouter = APIRouter(prefix="/auth", tags=["认证授权"])

_OAUTH_PROVIDERS = {"wechat", "qq", "github", "gitee"}
_OAUTH_STATE_PREFIX = "fastapiwebadmin:oauth_state:"


@AuthRouter.get("/captcha/get", description="获取登录验证码")
async def get_captcha():
    data = await CaptchaService.get_captcha()
    return await HttpResponse.success(data.model_dump())


@AuthRouter.post("/register", description="用户自助注册")
async def register(params: RegisterIn):
    try:
        await AuthAccountService.register(params)
        return await HttpResponse.success(msg="注册成功")
    except ValueError as exc:
        return await HttpResponse.fail(msg=str(exc))


@AuthRouter.post("/code", description="发送邮箱验证码")
async def send_email_code(params: EmailCodeIn):
    try:
        await AuthAccountService.send_email_code(params)
        return await HttpResponse.success(msg="验证码发送成功")
    except ValueError as exc:
        return await HttpResponse.fail(msg=str(exc))


@AuthRouter.post("/forget-password", description="忘记密码（邮箱验证码重置）")
async def forget_password(params: ForgetPasswordIn):
    try:
        await AuthAccountService.forget_password(params)
        return await HttpResponse.success(msg="密码重置成功，请使用新密码登录")
    except ValueError as exc:
        return await HttpResponse.fail(msg=str(exc))


@AuthRouter.get("/oauth/{provider}/login", description="跳转第三方 OAuth 授权页")
async def oauth_login_redirect(
    request: Request,
    provider: OAuthProvider,
    redirect_uri: str | None = Query(None, description="授权完成后回到的前端登录页 URL"),
):
    fallback = settings.OAUTH_FRONTEND_FALLBACK
    if provider not in _OAUTH_PROVIDERS:
        return RedirectResponse(OAuthService.error_redirect(fallback, "不支持的 OAuth 渠道"), status_code=302)
    if not redirect_uri:
        return RedirectResponse(OAuthService.error_redirect(fallback, "缺少 redirect_uri 参数"), status_code=302)
    try:
        state = secrets.token_urlsafe(32)
        await OAuthService.save_state(state=state, provider=provider, frontend_redirect=redirect_uri)
        authorize_url = OAuthService.build_authorize_url(
            provider=provider,
            callback_url=OAuthService.callback_url(request, provider),
            state=state,
        )
        return RedirectResponse(authorize_url, status_code=302)
    except ValueError as exc:
        return RedirectResponse(OAuthService.error_redirect(redirect_uri, str(exc)), status_code=302)


@AuthRouter.get("/oauth/{provider}/callback", description="第三方 OAuth 回调", include_in_schema=False)
async def oauth_callback(
    request: Request,
    provider: OAuthProvider,
    code: str | None = Query(None),
    state: str | None = Query(None),
):
    fallback = settings.OAUTH_FRONTEND_FALLBACK

    async def resolve_frontend() -> str:
        if not state:
            return fallback
        payload = await redis_pool.redis.get(f"{_OAUTH_STATE_PREFIX}{state}")
        if not payload:
            return fallback
        if isinstance(payload, dict):
            return str(payload.get("frontend_redirect") or fallback)
        return fallback

    if provider not in _OAUTH_PROVIDERS:
        return RedirectResponse(OAuthService.error_redirect(await resolve_frontend(), "不支持的 OAuth 渠道"), status_code=302)
    if not code or not state:
        return RedirectResponse(
            OAuthService.error_redirect(await resolve_frontend(), "授权被取消或参数不完整"),
            status_code=302,
        )
    try:
        token, frontend = await OAuthService.complete_login(
            request=request,
            provider=provider,
            code=code,
            state=state,
        )
        return RedirectResponse(OAuthService.success_redirect(frontend, token), status_code=302)
    except ValueError as exc:
        return RedirectResponse(OAuthService.error_redirect(await resolve_frontend(), str(exc)), status_code=302)

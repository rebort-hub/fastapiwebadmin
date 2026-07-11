# -*- coding: utf-8 -*-
"""验证码服务。"""

from app.config.setting import settings
from app.corelibs.consts import CAPTCHA_CODE
from app.db import redis_pool
from app.utils.captcha_util import CaptchaUtil

from .schema import CaptchaOut


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

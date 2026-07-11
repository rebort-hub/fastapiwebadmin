# -*- coding: utf-8 -*-
"""邮件发送与邮箱验证码。"""

import random
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from app.config.setting import settings
from app.corelibs.consts import EMAIL_CODE
from app.db import redis_pool

_MAIL_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


def _envelope_from_address(from_addr: str | None, smtp_username: str) -> str:
    raw = (from_addr or "").strip()
    if raw and "@" in raw:
        return raw
    return smtp_username


class EmailService:
    @staticmethod
    def _email_config() -> dict:
        return {
            "host": settings.EMAIL_HOST,
            "port": settings.EMAIL_PORT,
            "username": settings.EMAIL_USERNAME,
            "password": settings.EMAIL_PASSWORD,
            "from_addr": settings.EMAIL_FROM_ADDR or settings.EMAIL_USERNAME,
            "from_name": settings.EMAIL_FROM_NAME or settings.TITLE,
            "use_ssl": settings.EMAIL_USE_SSL,
        }

    @classmethod
    def generate_verification_code(cls, length: int = 4) -> str:
        return "".join(str(random.randint(0, 9)) for _ in range(length))

    @classmethod
    async def send_email(cls, *, username: str, title: str, mail: str) -> bool:
        email_cfg = cls._email_config()
        if not (email_cfg.get("username") and str(email_cfg.get("password", "")).strip()):
            logger.error(
                "邮件未发送：未配置 SMTP。请在 env 中填写 EMAIL_HOST、EMAIL_PORT、"
                "EMAIL_USERNAME、EMAIL_PASSWORD 等。"
            )
            return False

        if not _MAIL_TEMPLATES_DIR.is_dir():
            logger.error(f"邮件模板目录不存在: {_MAIL_TEMPLATES_DIR}")
            return False

        code = cls.generate_verification_code(4)
        code_str = "".join(
            f'<span style="display:inline-block;margin:2px 4px;padding:6px 10px;'
            f'font-size:22px;font-weight:bold;color:#FE4F70;background:#ededed;border-radius:6px;">{i}</span>'
            for i in code
        )
        env = Environment(loader=FileSystemLoader(str(_MAIL_TEMPLATES_DIR)))
        template = env.get_template("mail_zh.html")
        system_name = settings.TITLE
        content = template.render(TITLE=title, CODE=code_str, PROJECTNAME=system_name)
        subject = f"{system_name}-{title}"
        send_name = email_cfg["from_name"]
        from_email = _envelope_from_address(email_cfg.get("from_addr"), email_cfg["username"])

        message = EmailMessage()
        message["From"] = formataddr((send_name, from_email), charset="utf-8")
        message["To"] = mail
        message["Subject"] = subject
        plain = (
            f"验证码: {code}\n\n"
            f"操作: {title}\n"
            f"项目: {system_name}\n\n"
            f"此为系统邮件，请勿回复。"
        )
        message.set_content(plain, charset="utf-8")
        message.add_alternative(content, subtype="html", charset="utf-8")

        try:
            await aiosmtplib.send(
                message,
                hostname=email_cfg["host"],
                port=email_cfg["port"],
                username=email_cfg["username"],
                password=email_cfg["password"],
                use_tls=email_cfg["use_ssl"],
            )
            await redis_pool.redis.set(
                EMAIL_CODE.format(mail, username),
                code,
                ex=settings.EMAIL_CODE_EXPIRE_SECONDS,
            )
            logger.info(f"发送邮件至 {mail} 成功")
            return True
        except Exception as exc:
            logger.exception(f"发送邮件失败: {exc}")
            return False

    @classmethod
    async def verify_code(cls, *, username: str, mail: str, code: str) -> dict:
        cache_key = EMAIL_CODE.format(mail, username)
        redis_code = await redis_pool.redis.get(cache_key)
        if redis_code is None:
            return {"status": False, "msg": "验证码已过期"}
        if str(redis_code).lower() == str(code).strip().lower():
            await redis_pool.redis.delete(cache_key)
            return {"status": True, "msg": "验证码正确"}
        return {"status": False, "msg": "验证码错误"}

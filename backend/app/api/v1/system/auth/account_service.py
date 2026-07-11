# -*- coding: utf-8 -*-
"""公开注册与忘记密码。"""

from app.api.v1.system.user.model import User
from app.config.setting import settings
from app.corelibs.codes import CodeEnum
from app.utils.mail import EmailService
from app.utils.security import hash_password

from .schema import EmailCodeIn, ForgetPasswordIn, RegisterIn


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
        await User.create(
            {
                "username": params.username,
                "password": hash_password(params.password),
                "email": params.email,
                "nickname": nickname,
                "roles": settings.REGISTER_DEFAULT_ROLE_IDS,
                "user_type": 20,
                "status": 1,
                "remarks": "自助注册",
                "avatar": "",
                "tags": [],
                "dept_id": dept_id,
            }
        )

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

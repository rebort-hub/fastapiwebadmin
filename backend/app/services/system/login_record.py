# -*- coding: utf-8 -*-
# @author: rebort
from app.models.system_models import UserLoginRecord
from app.schemas.system.user import UserLoginRecordQuery


class LoginRecordService:

    @staticmethod
    async def list(params: UserLoginRecordQuery):
        """获取登录记录列表"""
        return await UserLoginRecord.get_list(params)

# -*- coding: utf-8 -*-
# @author: rebort
from app.api.v1.system.login_record.model import UserLoginRecord
from app.api.v1.system.user.schema import UserLoginRecordQuery


class LoginRecordService:

    @staticmethod
    async def list(params: UserLoginRecordQuery):
        """获取登录记录列表"""
        return await UserLoginRecord.get_list(params)

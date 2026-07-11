# -*- coding: utf-8 -*-
from app.utils.common import get_str_uuid

from .schema import IdOut


class IdCenterService:
    @staticmethod
    async def get_id() -> IdOut:
        return IdOut(id=get_str_uuid())

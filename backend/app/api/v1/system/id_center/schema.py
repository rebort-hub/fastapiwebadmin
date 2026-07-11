# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field


class IdOut(BaseModel):
    id: str = Field(..., description="全局唯一 ID")

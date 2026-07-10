# -*- coding: utf-8 -*-
"""公共 Pydantic 基类"""

from pydantic import BaseModel, field_validator


class BaseSchema(BaseModel):
    def model_dump(self, *args, **kwargs):
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    @field_validator("*", mode="before")
    @classmethod
    def blank_strings(cls, v):
        if v == "":
            return None
        return v

# -*- coding: utf-8 -*-
"""定时任务查询模型"""

from typing import Optional

from app.common.schema import BaseSchema


class TimedTasksQuerySchema(BaseSchema):
    """定时任务列表查询"""

    id: Optional[int] = None
    name: Optional[str] = None
    created_by_name: Optional[str] = None
    user_ids: Optional[list[int]] = None
    created_by: Optional[int] = None
    project_ids: Optional[list[int]] = None

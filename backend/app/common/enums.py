# -*- coding: utf-8 -*-
"""公共枚举"""

from enum import Enum


class EnvironmentEnum(str, Enum):
    DEV = "dev"
    PROD = "prod"

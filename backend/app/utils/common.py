# -*- coding: utf-8 -*-
# @author: rebort
import uuid


def get_str_uuid():
    return str(uuid.uuid4()).replace("-", "")

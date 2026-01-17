# -*- coding: utf-8 -*-
# @author: rebort
"""测试配置文件"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

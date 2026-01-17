# -*- coding: utf-8 -*-
# @author: rebort
"""API 文档相关接口"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter()


@router.get("/swagger", summary="Swagger UI 文档", include_in_schema=False)
async def swagger_ui():
    """返回 Swagger UI 页面"""
    html_path = os.path.join("static", "swagger", "swagger.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@router.get("/redoc", summary="ReDoc 文档", include_in_schema=False)
async def redoc_ui():
    """返回 ReDoc 页面"""
    html_path = os.path.join("static", "swagger", "redoc.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

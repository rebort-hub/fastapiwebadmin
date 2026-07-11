# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, select

from app.api.v1.system.operation_log.schema import OperationLogQuery
from app.models.base import Base


class OperationLog(Base):
    __tablename__ = "operation_log"

    user_id = Column(Integer, nullable=True, comment="操作用户ID", index=True)
    username = Column(String(64), nullable=True, comment="操作用户名")
    request_path = Column(String(255), nullable=False, comment="请求路径")
    request_method = Column(String(10), nullable=False, comment="请求方式")
    request_payload = Column(Text, nullable=True, comment="请求参数")
    request_ip = Column(String(50), nullable=True, comment="请求IP")
    location = Column(String(255), nullable=True, comment="操作地址")
    browser = Column(String(64), nullable=True, comment="浏览器")
    os_name = Column(String(64), nullable=True, comment="操作系统")
    response_code = Column(Integer, nullable=True, comment="HTTP状态码")
    response_body = Column(Text, nullable=True, comment="响应摘要")
    process_time = Column(String(20), nullable=True, comment="耗时")
    description = Column(String(255), nullable=True, comment="接口描述")
    status = Column(Integer, nullable=True, default=1, comment="1成功 0失败")

    @classmethod
    async def get_list(cls, params: OperationLogQuery):
        q = [cls.enabled_flag == 1]
        if params.username:
            q.append(cls.username.like(f"%{params.username}%"))
        if params.request_path:
            q.append(cls.request_path.like(f"%{params.request_path}%"))
        if params.request_method:
            q.append(cls.request_method == params.request_method)
        if params.request_ip:
            q.append(cls.request_ip.like(f"%{params.request_ip}%"))
        stmt = select(*cls.get_table_columns()).where(*q).order_by(cls.creation_date.desc())
        return await cls.pagination(stmt)

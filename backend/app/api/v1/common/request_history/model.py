# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.models.base import Base


class RequestHistory(Base):
    __tablename__ = "request_history"

    id = Column(Integer, primary_key=True, comment="主键")
    remote_addr = Column(String(255), nullable=False, comment="用户名称")
    real_ip = Column(String(255), nullable=False, comment="用户名称")
    request = Column(Text, nullable=False, comment="用户名称")
    method = Column(String(255), nullable=True, comment="操作")
    url = Column(String(255), nullable=True, comment="操作")
    args = Column(String(255), nullable=True, comment="操作")
    form = Column(String(255), nullable=True, comment="操作")
    json = Column(Text, nullable=True, comment="操作")
    response = Column(Text, nullable=True, comment="操作")
    endpoint = Column(Text, nullable=True, comment="操作")
    elapsed = Column(Text, nullable=True, comment="操作")
    request_time = Column(DateTime, nullable=True, comment="操作")
    env = Column(String(255), nullable=True, comment="操作")
    employee_code = Column(String(255), nullable=True, comment="操作")
    toekn = Column(String(255), nullable=True, comment="操作")

# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String

from app.models.base import Base


class Notify(Base):
    """消息"""

    __tablename__ = "notify"

    user_id = Column(Integer(), nullable=True, comment="用户id", index=True)
    group = Column(String(64), nullable=True, comment="组")
    message = Column(String(500), nullable=True, comment="消息")
    send_status = Column(Integer(), nullable=True, comment="发送状态，10成功 20 失败")
    read_status = Column(Integer(), nullable=True, comment="消息状态，10未读 20 已读")

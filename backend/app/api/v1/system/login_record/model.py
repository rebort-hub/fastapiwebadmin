# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Index, Integer, String, select
from sqlalchemy.orm import aliased
from app.api.v1.system.user.schema import UserLoginRecordQuery
from app.models.base import Base


class UserLoginRecord(Base):
    __tablename__ = "user_login_record"
    __table_args__ = (Index("idx_login_record_code_logintime", "code", "login_time"),)

    token = Column(String(40), index=True, comment="登陆token")
    code = Column(String(64), index=True, comment="账号")
    user_id = Column(Integer, comment="用户id")
    user_name = Column(String(50), comment="用户名称")
    logout_type = Column(String(50), comment="退出类型")
    login_type = Column(String(50), index=True, comment="登陆方式")
    login_time = Column(DateTime, index=True, comment="登陆时间")
    logout_time = Column(DateTime, comment="退出时间")
    login_ip = Column(String(30), index=True, comment="登录IP")
    ret_msg = Column(String(255), comment="返回信息")
    ret_code = Column(String(9), index=True, comment="返回状态码")
    address = Column(String(255), comment="地址")
    source_type = Column(String(255), comment="来源")

    @classmethod
    async def get_list(cls, params: UserLoginRecordQuery):
        from app.api.v1.system.user.model import User

        q = [cls.enabled_flag == 1]
        if params.token:
            q.append(cls.token.like("%{}%".format(params.token)))
        if params.code:
            q.append(cls.code.like("%{}%".format(params.code)))
        if params.user_name:
            q.append(cls.user_name.like("%{}%".format(params.user_name)))
        if params.login_ip:
            q.append(cls.login_ip.like("%{}%".format(params.login_ip)))
        u = aliased(User)
        stmt = select(*cls.get_table_columns()).where(*q).outerjoin(u, u.id == cls.created_by).order_by(cls.id.desc())
        return await cls.pagination(stmt)

    @classmethod
    async def get_by_token(cls, token: str):
        if not token:
            return None
        stmt = select(cls.get_table_columns()).where(cls.enabled_flag == 1, cls.token == token).order_by(cls.id.desc())
        return await cls.get_result(stmt, first=True)

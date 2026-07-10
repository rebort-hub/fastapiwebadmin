# -*- coding: utf-8 -*-
import typing

from sqlalchemy import Column, Integer, String, select, update

from app.models.base import Base


class Menu(Base):
    """菜单表"""

    __tablename__ = "menu"

    path = Column(String(255), nullable=False, comment="菜单路径")
    name = Column(String(255), nullable=False, comment="菜单名称", index=True)
    component = Column(String(255), nullable=True, comment="组件路径")
    title = Column(String(255), nullable=True, comment="title", index=True)
    isLink = Column(Integer, nullable=True, comment="外链")
    isHide = Column(Integer, nullable=True, default=False, comment="菜单是否隐藏")
    isKeepAlive = Column(Integer, nullable=True, default=True, comment="菜单是否缓存")
    isAffix = Column(Integer, nullable=True, default=False, comment="固定标签")
    isIframe = Column(Integer, nullable=True, default=False, comment="是否内嵌")
    roles = Column(String(64), nullable=True, default="", comment="权限")
    icon = Column(String(64), nullable=True, comment="icon", index=True)
    parent_id = Column(Integer, nullable=True, comment="父级菜单id")
    redirect = Column(String(255), nullable=True, comment="重定向路由")
    sort = Column(Integer, nullable=True, comment="排序")
    menu_type = Column(Integer, nullable=True, comment="菜单类型")
    lookup_id = Column(Integer, nullable=True, comment="数据字典")
    active_menu = Column(String(255), nullable=True, comment="显示页签")
    views = Column(Integer, default=0, nullable=True, comment="访问数")

    @classmethod
    async def get_menu_by_ids(cls, ids: typing.List[int]):
        stmt = select(cls.get_table_columns()).where(cls.id.in_(ids), cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_menus_and_buttons_by_ids(cls, ids: typing.List[int]):
        stmt = select(cls.get_table_columns()).where(cls.id.in_(ids), cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_menu_all(cls):
        stmt = select(cls.get_table_columns()).where(cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_all_menus_with_buttons(cls):
        stmt = select(cls.get_table_columns()).where(cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_all_buttons(cls):
        stmt = (
            select(cls.get_table_columns())
            .where(cls.menu_type == 20, cls.roles.isnot(None), cls.roles != "")
            .order_by(cls.sort)
        )
        return await cls.get_result(stmt)

    @classmethod
    async def get_buttons_by_ids(cls, ids: typing.List[int]):
        if not ids:
            return []
        stmt = (
            select(cls.get_table_columns())
            .where(cls.id.in_(ids), cls.menu_type == 20, cls.roles.isnot(None), cls.roles != "")
            .order_by(cls.sort)
        )
        return await cls.get_result(stmt)

    @classmethod
    async def get_parent_id_by_ids(cls, ids: typing.List[int]):
        stmt = select(cls.get_table_columns()).where(cls.id.in_(ids), cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_parent_id_all(cls):
        stmt = select(cls.get_table_columns()).where(cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_menu_by_title(cls, title: str):
        stmt = select(cls.get_table_columns()).where(cls.title == title, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_menu_by_parent(cls, parent_id: int):
        stmt = (
            select(cls.get_table_columns())
            .where(cls.parent_id == parent_id, cls.enabled_flag == 1)
            .order_by(cls.sort)
        )
        return await cls.get_result(stmt, True)

    @classmethod
    async def add_menu_views(cls, menu_id: int):
        stmt = (
            update(cls.get_table_columns())
            .where(cls.id == menu_id, cls.enabled_flag == 1)
            .values(**{"views": cls.views + 1})
        )
        result = await cls.execute(stmt)
        return result.rowcount


class MenuViewHistory(Base):
    """菜单访问记录"""

    __tablename__ = "menu_view_history"

    menu_id = Column(Integer(), nullable=True, comment="菜单id", index=True)
    remote_addr = Column(String(64), nullable=True, comment="访问ip", index=True)
    user_id = Column(Integer(), nullable=True, comment="访问人", index=True)

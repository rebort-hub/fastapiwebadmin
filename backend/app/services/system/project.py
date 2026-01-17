# -*- coding: utf-8 -*-
# @author: rebort
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.corelibs.codes import CodeEnum
from app.models.api_models import ProjectInfo, ModuleInfo
from app.models.system_models import User
from app.schemas.system.project import ProjectIn, ProjectQuery, ProjectDel


class ProjectService:

    @staticmethod
    async def list(params: ProjectQuery):
        """获取项目列表"""
        q = [ProjectInfo.enabled_flag == 1]
        if params.name:
            q.append(ProjectInfo.name.like(f'%{params.name}%'))
        
        u = aliased(User)
        stmt = select(
            *ProjectInfo.get_table_columns(),
            u.nickname.label("created_by_name"),
            User.nickname.label("updated_by_name")
        ).where(*q) \
            .outerjoin(u, u.id == ProjectInfo.created_by) \
            .outerjoin(User, User.id == ProjectInfo.updated_by) \
            .order_by(ProjectInfo.id.desc())
        
        return await ProjectInfo.pagination(stmt)

    @staticmethod
    async def save_or_update(params: ProjectIn):
        """保存或更新项目"""
        # 检查项目名称是否已存在
        stmt = select(ProjectInfo).where(
            ProjectInfo.name == params.name,
            ProjectInfo.enabled_flag == 1
        )
        if params.id:
            stmt = stmt.where(ProjectInfo.id != params.id)
        
        existing = await ProjectInfo.get_result(stmt, first=True)
        if existing:
            raise ValueError(CodeEnum.PROJECT_NAME_EXIST.msg)
        
        # 使用 create_or_update 方法
        await ProjectInfo.create_or_update(params.dict(exclude_unset=True))

    @staticmethod
    async def deleted(params: ProjectDel):
        """删除项目"""
        # 检查是否有关联的模块
        stmt = select(ModuleInfo).where(
            ModuleInfo.project_id == params.id,
            ModuleInfo.enabled_flag == 1
        )
        modules = await ModuleInfo.get_result(stmt)
        if modules:
            raise ValueError(CodeEnum.PROJECT_HAS_MODULE_ASSOCIATION.msg)
        
        # 软删除
        await ProjectInfo.delete(params.id)

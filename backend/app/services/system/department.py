# -*- coding: utf-8 -*-
# @author: rebort
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.corelibs.codes import CodeEnum
from app.models.system_models import Department, User
from app.schemas.system.department import DepartmentIn, DepartmentDel


class DepartmentService:

    @staticmethod
    async def list():
        """获取部门列表（树形结构）"""
        all_depts = await Department.get_list()
        # 如果没有数据，返回空列表
        if not all_depts:
            return []
        # 构建树形结构
        return DepartmentService.build_tree(all_depts, 0)

    @staticmethod
    def build_tree(depts: list, parent_id: int = 0):
        """构建树形结构"""
        if not depts:
            return []
        tree = []
        for dept in depts:
            if dept.get('parent_id') == parent_id:
                children = DepartmentService.build_tree(depts, dept['id'])
                dept_node = {
                    **dept,
                    'children': children if children else None
                }
                tree.append(dept_node)
        return tree

    @staticmethod
    async def save_or_update(params: DepartmentIn):
        """保存或更新部门"""
        # 检查部门名称是否已存在
        existing = await Department.get_by_name(params.name, params.id)
        if existing:
            raise ValueError('部门名称已存在')
        
        # 使用 create_or_update 方法
        await Department.create_or_update(params.dict(exclude_unset=True))

    @staticmethod
    async def deleted(params: DepartmentDel):
        """删除部门"""
        # 检查是否有子部门
        children = await Department.get_children(params.id)
        if children:
            raise ValueError('该部门下有子部门，不能删除')
        
        # 检查是否有用户关联
        from app.models.system_models import User
        stmt = select(User).where(
            User.dept_id == params.id,
            User.enabled_flag == 1
        )
        users = await User.get_result(stmt)
        if users:
            raise ValueError('该部门下有用户，不能删除')
        
        # 软删除
        await Department.delete(params.id)

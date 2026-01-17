"""add_department_table_and_fields

Revision ID: d45d346a66e1
Revises: b1c76d9cbd3b
Create Date: 2026-01-17 15:04:59.688061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd45d346a66e1'
down_revision = 'b1c76d9cbd3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 department 表
    op.create_table('department',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='部门名称'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父部门ID'),
        sa.Column('sort', sa.Integer(), nullable=True, comment='排序'),
        sa.Column('status', sa.Integer(), nullable=True, comment='状态 1启用 0禁用'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='部门描述'),
        sa.Column('creation_date', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(length=255), nullable=True, comment='trace_id'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8'
    )
    op.create_index(op.f('ix_department_name'), 'department', ['name'], unique=False)
    
    # 为 user 表添加 dept_id 字段
    op.add_column('user', sa.Column('dept_id', sa.Integer(), nullable=True, comment='部门ID'))
    
    # 为 roles 表添加 dept_id 字段
    op.add_column('roles', sa.Column('dept_id', sa.Integer(), nullable=True, comment='部门ID'))


def downgrade() -> None:
    # 删除 roles 表的 dept_id 字段
    op.drop_column('roles', 'dept_id')
    
    # 删除 user 表的 dept_id 字段
    op.drop_column('user', 'dept_id')
    
    # 删除 department 表的索引
    op.drop_index(op.f('ix_department_name'), table_name='department')
    
    # 删除 department 表
    op.drop_table('department')

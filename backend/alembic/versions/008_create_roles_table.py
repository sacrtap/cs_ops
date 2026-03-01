"""create_roles_table

Revision ID: 008
Revises: 007_create_permission_matrix
Create Date: 2026-03-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建角色表"""
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_roles_name'),
        sa.CheckConstraint("status IN ('active', 'inactive')", name='chk_status')
    )
    
    # 创建索引优化查询性能
    op.create_index('idx_roles_status', 'roles', ['status'])
    op.create_index('idx_roles_name', 'roles', ['name'])
    
    # 插入系统默认角色数据
    default_roles = [
        {
            'name': 'admin',
            'description': '系统管理员角色，拥有所有权限',
            'status': 'active'
        },
        {
            'name': 'manager',
            'description': '经理角色，拥有大部分管理权限',
            'status': 'active'
        },
        {
            'name': 'specialist',
            'description': '专员角色，拥有基础操作权限',
            'status': 'active'
        },
        {
            'name': 'sales',
            'description': '销售角色，仅拥有客户相关只读权限',
            'status': 'active'
        }
    ]
    
    # 批量插入默认角色
    op.bulk_insert(
        sa.table('roles',
            sa.column('name', sa.String),
            sa.column('description', sa.Text),
            sa.column('status', sa.String),
        ),
        default_roles
    )


def downgrade() -> None:
    """删除角色表"""
    op.drop_index('idx_roles_name', table_name='roles')
    op.drop_index('idx_roles_status', table_name='roles')
    op.drop_table('roles')

"""create_permission_matrix_table

Revision ID: 007
Revises: 006_create_orgs_and_customers
Create Date: 2026-03-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006_create_orgs_and_customers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建权限矩阵表"""
    op.create_table(
        'permission_matrix',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('module', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role', 'module', 'action', name='uq_role_module_action')
    )
    
    # 创建索引优化查询性能
    op.create_index('idx_permission_role', 'permission_matrix', ['role'])
    op.create_index('idx_permission_module', 'permission_matrix', ['module'])
    op.create_index('idx_permission_role_module', 'permission_matrix', ['role', 'module'])
    
    # 插入默认权限数据
    # Admin: 所有权限
    admin_permissions = [
        ('admin', 'customer', 'read', True),
        ('admin', 'customer', 'create', True),
        ('admin', 'customer', 'update', True),
        ('admin', 'customer', 'delete', True),
        ('admin', 'settlement', 'read', True),
        ('admin', 'settlement', 'create', True),
        ('admin', 'settlement', 'update', True),
        ('admin', 'settlement', 'delete', True),
        ('admin', 'reporting', 'read', True),
        ('admin', 'reporting', 'create', True),
        ('admin', 'reporting', 'update', True),
        ('admin', 'reporting', 'delete', True),
        ('admin', 'permission', 'read', True),
        ('admin', 'permission', 'create', True),
        ('admin', 'permission', 'update', True),
        ('admin', 'permission', 'delete', True),
    ]
    
    # Manager: 大部分 read/update
    manager_permissions = [
        ('manager', 'customer', 'read', True),
        ('manager', 'customer', 'create', True),
        ('manager', 'customer', 'update', True),
        ('manager', 'customer', 'delete', False),
        ('manager', 'settlement', 'read', True),
        ('manager', 'settlement', 'create', False),
        ('manager', 'settlement', 'update', True),
        ('manager', 'settlement', 'delete', False),
        ('manager', 'reporting', 'read', True),
        ('manager', 'reporting', 'create', False),
        ('manager', 'reporting', 'update', False),
        ('manager', 'reporting', 'delete', False),
        ('manager', 'permission', 'read', True),
        ('manager', 'permission', 'create', False),
        ('manager', 'permission', 'update', False),
        ('manager', 'permission', 'delete', False),
    ]
    
    # Specialist: 大部分 read/create/update
    specialist_permissions = [
        ('specialist', 'customer', 'read', True),
        ('specialist', 'customer', 'create', True),
        ('specialist', 'customer', 'update', True),
        ('specialist', 'customer', 'delete', False),
        ('specialist', 'settlement', 'read', True),
        ('specialist', 'settlement', 'create', True),
        ('specialist', 'settlement', 'update', True),
        ('specialist', 'settlement', 'delete', False),
        ('specialist', 'reporting', 'read', True),
        ('specialist', 'reporting', 'create', False),
        ('specialist', 'reporting', 'update', False),
        ('specialist', 'reporting', 'delete', False),
        ('specialist', 'permission', 'read', True),
        ('specialist', 'permission', 'create', False),
        ('specialist', 'permission', 'update', False),
        ('specialist', 'permission', 'delete', False),
    ]
    
    # Sales: 仅客户相关 read
    sales_permissions = [
        ('sales', 'customer', 'read', True),
        ('sales', 'customer', 'create', False),
        ('sales', 'customer', 'update', True),
        ('sales', 'customer', 'delete', False),
        ('sales', 'settlement', 'read', True),
        ('sales', 'settlement', 'create', False),
        ('sales', 'settlement', 'update', False),
        ('sales', 'settlement', 'delete', False),
        ('sales', 'reporting', 'read', False),
        ('sales', 'reporting', 'create', False),
        ('sales', 'reporting', 'update', False),
        ('sales', 'reporting', 'delete', False),
        ('sales', 'permission', 'read', False),
        ('sales', 'permission', 'create', False),
        ('sales', 'permission', 'update', False),
        ('sales', 'permission', 'delete', False),
    ]
    
    # 合并所有默认权限
    default_permissions = admin_permissions + manager_permissions + specialist_permissions + sales_permissions
    
    # 批量插入默认权限
    op.bulk_insert(
        sa.table('permission_matrix',
            sa.column('role', sa.String),
            sa.column('module', sa.String),
            sa.column('action', sa.String),
            sa.column('granted', sa.Boolean),
        ),
        [
            {'role': role, 'module': module, 'action': action, 'granted': granted}
            for role, module, action, granted in default_permissions
        ]
    )


def downgrade() -> None:
    """删除权限矩阵表"""
    op.drop_index('idx_permission_role_module', table_name='permission_matrix')
    op.drop_index('idx_permission_module', table_name='permission_matrix')
    op.drop_index('idx_permission_role', table_name='permission_matrix')
    op.drop_table('permission_matrix')

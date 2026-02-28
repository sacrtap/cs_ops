"""
创建 users 表

迁移 ID: 001
创建日期：2026-02-27
描述：创建用户认证表，包含用户名、密码哈希、角色、状态等字段

依赖：无（首次迁移）
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 users 表"""
    
    # 创建枚举类型
    op.execute("""
        CREATE TYPE user_role AS ENUM ('admin', 'manager', 'specialist', 'sales')
    """)
    
    op.execute("""
        CREATE TYPE user_status AS ENUM ('active', 'inactive', 'locked')
    """)
    
    # 创建 users 表
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('real_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('admin', 'manager', 'specialist', 'sales', name='user_role'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'locked', name='user_status'), 
                  nullable=False, server_default='active'),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_login_ip', sa.String(length=45), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.CheckConstraint(
            "role IN ('admin', 'manager', 'specialist', 'sales')",
            name='check_user_role'
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'locked')",
            name='check_user_status'
        ),
    )
    
    # 创建索引
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    op.create_index('idx_users_status', 'users', ['status'], unique=False)
    op.create_index('idx_users_email', 'users', ['email'], unique=False)


def downgrade() -> None:
    """删除 users 表和枚举类型"""
    
    # 删除索引
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_status', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    
    # 删除表
    op.drop_table('users')
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS user_status')
    op.execute('DROP TYPE IF EXISTS user_role')

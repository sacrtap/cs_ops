"""
创建 token_blacklists 表

迁移 ID: 002
创建日期：2026-02-28
描述：创建 Token 黑名单表，用于存储已失效的 Token（登出、撤销等）

依赖：001_create_users_table.py
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 token_blacklists 表"""
    
    # 创建枚举类型
    op.execute("""
        CREATE TYPE token_blacklist_type AS ENUM ('access', 'refresh')
    """)
    
    op.execute("""
        CREATE TYPE blacklist_reason AS ENUM ('logout', 'revoked', 'compromised')
    """)
    
    # 创建 token_blacklists 表
    op.create_table(
        'token_blacklists',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('token_type', sa.Enum('access', 'refresh', name='token_blacklist_type'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('blacklisted_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('reason', sa.Enum('logout', 'revoked', 'compromised', name='blacklist_reason'), 
                  nullable=False, server_default='logout'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
        sa.CheckConstraint(
            "token_type IN ('access', 'refresh')",
            name='check_token_type'
        ),
        sa.CheckConstraint(
            "expires_at > blacklisted_at",
            name='check_expires'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_token_blacklists_user'
        ),
    )
    
    # 创建索引
    op.create_index('idx_token_blacklists_hash', 'token_blacklists', ['token_hash'], unique=False)
    op.create_index('idx_token_blacklists_user', 'token_blacklists', ['user_id'], unique=False)
    op.create_index('idx_token_blacklists_expires', 'token_blacklists', ['expires_at'], unique=False)


def downgrade() -> None:
    """删除 token_blacklists 表和枚举类型"""
    
    # 删除索引
    op.drop_index('idx_token_blacklists_expires', table_name='token_blacklists')
    op.drop_index('idx_token_blacklists_user', table_name='token_blacklists')
    op.drop_index('idx_token_blacklists_hash', table_name='token_blacklists')
    
    # 删除表
    op.drop_table('token_blacklists')
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS blacklist_reason')
    op.execute('DROP TYPE IF EXISTS token_blacklist_type')

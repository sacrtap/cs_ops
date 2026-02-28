"""
Token 黑名单模型 - 用于 Token 失效管理
"""
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, DateTime, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base


class TokenBlacklistType(str, Enum):
    """Token 黑名单类型"""
    ACCESS = "access"
    REFRESH = "refresh"


class BlacklistReason(str, Enum):
    """黑名单原因"""
    LOGOUT = "logout"  # 用户主动登出
    REVOKED = "revoked"  # 被管理员撤销
    COMPROMISED = "compromised"  # 疑似泄露


class TokenBlacklist(Base):
    """
    Token 黑名单表 - 存储已失效的 Token
    
    字段说明:
    - id: 数据库主键（自增整数）
    - token_hash: Token 的 SHA256 哈希（唯一索引）
    - token_type: Token 类型（access/refresh）
    - user_id: 关联用户 ID
    - blacklisted_at: 加入黑名单时间
    - expires_at: Token 原始过期时间
    - reason: 加入黑名单原因
    """
    __tablename__ = "token_blacklists"

    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID"
    )

    # Token 信息
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="Token SHA256 哈希"
    )
    token_type: Mapped[TokenBlacklistType] = mapped_column(
        String(20),
        nullable=False,
        comment="Token 类型"
    )

    # 用户关联
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="用户 ID"
    )

    # 时间戳
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="加入黑名单时间"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Token 过期时间"
    )

    # 原因
    reason: Mapped[BlacklistReason] = mapped_column(
        String(50),
        default=BlacklistReason.LOGOUT,
        nullable=False,
        comment="加入黑名单原因"
    )

    # 用户关系
    # user = relationship("User", back_populates="token_blacklists")

    # 表约束
    __table_args__ = (
        CheckConstraint(
            "token_type IN ('access', 'refresh')",
            name="check_token_type"
        ),
        CheckConstraint(
            "expires_at > blacklisted_at",
            name="check_expires"
        ),
    )

    def __repr__(self) -> str:
        return f"<TokenBlacklist(id={self.id}, token_hash='{self.token_hash[:16]}...', type={self.token_type.value})>"

    def is_expired(self) -> bool:
        """检查黑名单记录是否已过期"""
        return datetime.now(timezone.utc) > self.expires_at

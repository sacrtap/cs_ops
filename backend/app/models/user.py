"""
用户模型 - 数据库表定义
"""
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base


class UserRole(str, Enum):
    """用户角色枚举（4 级 RBAC）"""
    ADMIN = "admin"  # 系统管理员
    MANAGER = "manager"  # 运营经理
    SPECIALIST = "specialist"  # 运营专员
    SALES = "sales"  # 销售


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 不活跃
    LOCKED = "locked"  # 锁定（登录失败次数过多）


class User(Base):
    """
    用户表 - 认证与授权
    
    字段说明:
    - id: 数据库主键（自增整数），用于内部数据库关系
    - username: 用户名（唯一），用于登录
    - password_hash: bcrypt 加密的密码哈希
    - real_name: 真实姓名（显示用）
    - role: 用户角色（4 级 RBAC）
    - email: 邮箱（可选，用于接收通知）
    - phone: 手机号（可选，用于接收短信）
    - status: 用户状态（active/inactive/locked）
    - last_login_at: 最后登录时间
    - last_login_ip: 最后登录 IP
    - failed_login_attempts: 连续登录失败次数
    - locked_until: 锁定截止时间（防暴力破解）
    """
    __tablename__ = "users"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 认证字段
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,  # 登录查询优化
        comment="用户名（唯一）"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 加密的密码哈希"
    )

    # 用户信息
    real_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="真实姓名"
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.SALES,
        comment="用户角色（4 级 RBAC）"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="邮箱地址"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="手机号码"
    )

    # 状态管理
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE,
        comment="用户状态"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 最大长度
        nullable=True,
        comment="最后登录 IP"
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="连续登录失败次数"
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="锁定截止时间（防暴力破解）"
    )

    # 审计字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
        comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role={self.role.value})>"

    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if self.status != UserStatus.LOCKED:
            return False
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until

    def to_dict(self, exclude_password: bool = True) -> dict:
        """
        转换为字典（用于 API 响应）
        
        Args:
            exclude_password: 是否排除密码哈希（默认 True，永远不返回密码）
        """
        data = {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "role": self.role.value,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        # 永远不返回 password_hash
        return data

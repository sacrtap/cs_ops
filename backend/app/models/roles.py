"""
角色模型 - 系统角色管理
"""
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, CheckConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base


class Role(Base):
    """
    角色表 - 存储系统角色信息
    
    字段说明:
    - id: 数据库主键（自增整数）
    - name: 角色名称（admin/manager/specialist/sales）
    - description: 角色描述
    - status: 状态（active/inactive）
    - created_at: 创建时间
    - updated_at: 更新时间
    
    唯一约束：name - 角色名称必须唯一
    检查约束：status 必须是 'active' 或 'inactive'
    """
    __tablename__ = "roles"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 角色字段
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="角色名称")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="角色描述")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='active', comment="状态")
    level: Mapped[int] = mapped_column(nullable=False, default=1, comment="角色层级（数字越大权限越高）")
    parent_role_id: Mapped[Optional[int]] = mapped_column(comment="父角色 ID（用于权限继承）")
    
    # 时间戳
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP'),
        nullable=True
    )
    
    # 约束和索引
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name='chk_status'),
        Index('idx_roles_status', 'status'),
        Index('idx_roles_name', 'name'),
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name}, level={self.level}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "level": self.level,
            "parent_role_id": self.parent_role_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

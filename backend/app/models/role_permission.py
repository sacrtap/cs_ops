"""
Role Permission Model - 角色权限矩阵模型

用于动态配置角色权限矩阵（可选增强功能）。
如果使用静态权限矩阵，此模型可以省略。
"""
from datetime import datetime
from sqlalchemy import String, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base


class RolePermission(Base):
    """
    角色权限矩阵表
    
    字段说明:
    - id: 数据库主键
    - role: 角色名称（admin, manager, specialist, sales）
    - resource: 资源名称（customer, settlement, report, user, role）
    - action: 操作类型（create, read, update, delete, view, export）
    - created_at: 创建时间
    
    约束:
    - 唯一约束：(role, resource, action) 确保每个角色的每个资源的每个操作只有一条记录
    """
    __tablename__ = "role_permissions"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 权限字段
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,  # 加速角色查询
        comment="角色名称"
    )
    resource: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,  # 加速资源查询
        comment="资源名称（customer, settlement, report, user, role）"
    )
    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="操作类型（create, read, update, delete, view, export）"
    )
    
    # 审计字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="创建时间"
    )
    
    # 唯一约束：(role, resource, action)
    __table_args__ = (
        UniqueConstraint('role', 'resource', 'action', name='uq_role_resource_action'),
        Index('ix_role_permissions_role', 'role'),
        Index('ix_role_permissions_resource', 'resource'),
    )
    
    def __repr__(self) -> str:
        return f"<RolePermission(role={self.role}, resource={self.resource}, action={self.action})>"
    
    def to_dict(self) -> dict:
        """转换为字典（用于 API 响应）"""
        return {
            "id": self.id,
            "role": self.role,
            "resource": self.resource,
            "action": self.action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

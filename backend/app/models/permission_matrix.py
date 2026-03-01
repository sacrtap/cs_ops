"""
权限矩阵模型 - 功能权限配置
"""
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, UniqueConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base


class PermissionMatrix(Base):
    """
    权限矩阵表 - 存储角色 - 模块 - 操作权限映射
    
    字段说明:
    - id: 数据库主键（自增整数）
    - role: 角色名称（admin/manager/specialist/sales）
    - module: 功能模块名称（customer/settlement/reporting/permission）
    - action: 操作类型（read/create/update/delete）
    - granted: 是否授权（True/False）
    - created_at: 创建时间
    - updated_at: 更新时间
    
    唯一约束: (role, module, action) - 每个角色的每个模块的每个操作只能有一条记录
    """
    __tablename__ = "permission_matrix"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 权限字段
    role: Mapped[str] = mapped_column(String(50), nullable=False, comment="角色名称")
    module: Mapped[str] = mapped_column(String(100), nullable=False, comment="功能模块")
    action: Mapped[str] = mapped_column(String(20), nullable=False, comment="操作类型")
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否授权")
    
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
    
    # 唯一约束：每个角色的每个模块的每个操作只能有一条记录
    __table_args__ = (
        UniqueConstraint('role', 'module', 'action', name='uq_role_module_action'),
        Index('idx_permission_role', 'role'),
        Index('idx_permission_module', 'module'),
        Index('idx_permission_role_module', 'role', 'module'),
    )
    
    def __repr__(self) -> str:
        return f"<PermissionMatrix(role={self.role}, module={self.module}, action={self.action}, granted={self.granted})>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "role": self.role,
            "module": self.module,
            "action": self.action,
            "granted": self.granted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

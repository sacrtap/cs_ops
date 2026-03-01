"""
组织模型 - 数据权限的组织结构

用于支持数据权限过滤（Manager 可以看到本组织所有数据）
"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from .base import Base


class Organization(Base):
    """
    组织表 - 数据隔离边界
    
    字段说明:
    - id: 数据库主键（自增整数）
    - name: 组织名称
    - parent_id: 父组织 ID（支持组织层级）
    - code: 组织代码（用于系统间同步）
    - status: 组织状态（active/inactive）
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = "organizations"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 组织信息
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="组织名称"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="组织代码（用于系统间同步）"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=True,
        comment="父组织 ID（支持组织层级）"
    )
    
    # 组织状态
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="组织状态（active/inactive）"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="组织描述"
    )
    
    # 审计字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="更新时间"
    )
    
    # 关系：自引用（父子组织）
    parent: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        remote_side=[id],
        backref="children"
    )
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self) -> dict:
        """转换为字典（用于 API 响应）"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "parent_id": self.parent_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

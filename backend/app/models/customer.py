"""
客户模型 - 数据权限管理的核心业务对象

用于测试数据权限过滤（Sales 仅能看到自己的客户，Manager 能看到本组织所有客户）
"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base


class Customer(Base):
    """
    客户表 - 数据权限管理的核心业务对象
    
    字段说明:
    - id: 数据库主键（自增整数）
    - name: 客户名称（公司名称）
    - contact_name: 联系人姓名
    - contact_email: 联系人邮箱
    - contact_phone: 联系人电话
    - sales_rep_id: 销售代表 ID（数据权限关键字段）
    - org_id: 组织 ID（数据权限关键字段）
    - status: 客户状态（active/inactive/lead）
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = "customers"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 客户基本信息
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="客户名称（公司名称）"
    )
    contact_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="联系人姓名"
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="联系人邮箱"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="联系人电话"
    )
    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="客户地址"
    )
    
    # 数据权限关键字段
    sales_rep_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="销售代表 ID（数据权限过滤）"
    )
    org_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
        comment="组织 ID（数据权限过滤）"
    )
    
    # 客户关系
    sales_rep: Mapped[Optional["User"]] = relationship(
        "User",
        backref="customers"
    )
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        backref="customers"
    )
    
    # 客户状态
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="客户状态（active/inactive/lead）"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注信息"
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
    
    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.name}', sales_rep_id={self.sales_rep_id})>"
    
    def to_dict(self) -> dict:
        """转换为字典（用于 API 响应）"""
        return {
            "id": self.id,
            "name": self.name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "address": self.address,
            "sales_rep_id": self.sales_rep_id,
            "org_id": self.org_id,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # 如果有关系对象，也包含它们
            "sales_rep": self.sales_rep.to_dict() if self.sales_rep else None,
            "organization": self.organization.to_dict() if self.organization else None,
        }


# 延迟导入以避免循环依赖
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .organization import Organization

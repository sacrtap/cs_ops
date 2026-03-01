"""
Permission Audit Log Model - 权限审计日志模型
"""
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, CheckConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base


class PermissionAuditLog(Base):
    """
    权限审计日志表 - 记录权限使用日志
    
    字段说明:
    - id: 数据库主键（自增整数）
    - user_id: 用户 ID
    - role: 角色名称
    - resource: 资源名称
    - action: 操作类型
    - ip_address: 操作 IP 地址
    - is_anomaly: 是否异常访问
    - anomaly_type: 异常类型（unauthorized_access/frequent_access/location_anomaly/privilege_escalation）
    - details: 详细信息（JSON 格式）
    - timestamp: 操作时间
    
    索引:
    - idx_user_id: 按用户 ID 查询
    - idx_timestamp: 按时间查询
    - idx_is_anomaly: 按异常状态查询
    - idx_anomaly_type: 按异常类型查询
    """
    __tablename__ = "permission_audit_logs"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 审计字段
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="用户 ID")
    role: Mapped[str] = mapped_column(String(50), nullable=False, comment="角色名称")
    resource: Mapped[str] = mapped_column(String(100), nullable=False, comment="资源名称")
    action: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作类型")
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, comment="IP 地址")
    
    # 异常检测字段
    is_anomaly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True, comment="是否异常访问")
    anomaly_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True, comment="异常类型")
    
    # 详细信息（JSON 格式）
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="详细信息（JSON 格式）")
    
    # 时间戳
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        nullable=False,
        index=True,
        comment="操作时间"
    )
    
    # 约束和索引
    __table_args__ = (
        CheckConstraint(
            "anomaly_type IN ('unauthorized_access', 'frequent_access', 'location_anomaly', 'privilege_escalation')",
            name='chk_anomaly_type'
        ),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource_action', 'resource', 'action'),
    )
    
    def __repr__(self) -> str:
        return f"<PermissionAuditLog(id={self.id}, user_id={self.user_id}, resource={self.resource}, action={self.action}, is_anomaly={self.is_anomaly})>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role,
            "resource": self.resource,
            "action": self.action,
            "ip_address": self.ip_address,
            "is_anomaly": self.is_anomaly,
            "anomaly_type": self.anomaly_type,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

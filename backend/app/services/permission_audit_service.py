"""
Permission Audit Service - 权限审计服务

提供权限审计相关的业务逻辑：
- 查询权限使用日志
- 检测异常访问
- 统计异常访问数据
- 导出权限审计记录
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from ..models.permission_audit_log import PermissionAuditLog


class PermissionAuditService:
    """权限审计服务类"""
    
    @staticmethod
    async def query_audit_logs(
        session: AsyncSession,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        anomaly_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        查询权限审计记录
        
        Args:
            session: 数据库会话
            user_id: 用户 ID（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            anomaly_type: 异常类型（可选）
            page: 页码
            page_size: 每页数量
            sort_by: 排序字段
            sort_order: 排序顺序（asc/desc）
            
        Returns:
            Dict: 包含记录列表和分页信息
        """
        # 构建查询条件
        conditions = []
        
        if user_id:
            conditions.append(PermissionAuditLog.user_id == user_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            conditions.append(PermissionAuditLog.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            # 包含结束日期的整天
            end_dt = end_dt + timedelta(days=1)
            conditions.append(PermissionAuditLog.timestamp < end_dt)
        
        if anomaly_type:
            conditions.append(PermissionAuditLog.anomaly_type == anomaly_type)
        
        # 构建查询
        query = select(PermissionAuditLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序
        sort_column = getattr(PermissionAuditLog, sort_by, PermissionAuditLog.timestamp)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 分页
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await session.execute(query)
        logs = result.scalars().all()
        
        return {
            "records": [log.to_dict() for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    @staticmethod
    async def get_audit_statistics(
        session: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取权限审计统计信息
        
        Args:
            session: 数据库会话
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            Dict: 统计信息
        """
        # 构建查询条件
        conditions = []
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            conditions.append(PermissionAuditLog.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            end_dt = end_dt + timedelta(days=1)
            conditions.append(PermissionAuditLog.timestamp < end_dt)
        
        # 总记录数
        total_query = select(func.count(PermissionAuditLog.id))
        if conditions:
            total_query = total_query.where(and_(*conditions))
        
        total_result = await session.execute(total_query)
        total_records = total_result.scalar() or 0
        
        # 异常记录数
        anomaly_query = select(func.count(PermissionAuditLog.id)).where(
            PermissionAuditLog.is_anomaly == True
        )
        if conditions:
            anomaly_query = anomaly_query.where(and_(*conditions))
        
        anomaly_result = await session.execute(anomaly_query)
        anomaly_count = anomaly_result.scalar() or 0
        
        # 计算异常率
        anomaly_rate = (anomaly_count / total_records * 100) if total_records > 0 else 0.0
        
        return {
            "total_records": total_records,
            "anomaly_count": anomaly_count,
            "anomaly_rate": round(anomaly_rate, 2)
        }
    
    @staticmethod
    async def detect_anomaly(
        session: AsyncSession,
        user_id: str,
        resource: str,
        action: str,
        ip_address: str,
        role: str
    ) -> tuple[bool, Optional[str]]:
        """
        检测异常访问
        
        异常检测规则：
        1. 未授权访问：用户尝试访问没有权限的资源
        2. 频繁访问：短时间内大量访问
        3. 异地访问：IP 地址与常用地址不符
        4. 越权访问：低级别角色尝试访问高级别功能
        
        Args:
            session: 数据库会话
            user_id: 用户 ID
            resource: 资源名称
            action: 操作类型
            ip_address: IP 地址
            role: 角色名称
            
        Returns:
            tuple: (是否异常，异常类型)
        """
        # 规则 1: 检查权限（需要权限检查服务）
        # 这里简化处理，实际应该调用权限检查服务
        
        # 规则 2: 检查频繁访问（过去 1 分钟内超过 100 次）
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_query = select(func.count(PermissionAuditLog.id)).where(
            and_(
                PermissionAuditLog.user_id == user_id,
                PermissionAuditLog.timestamp >= one_minute_ago
            )
        )
        recent_result = await session.execute(recent_query)
        recent_count = recent_result.scalar() or 0
        
        if recent_count > 100:
            return True, "frequent_access"
        
        # 规则 3: 检查越权访问（简化版）
        high_privilege_resources = ["role", "permission", "audit"]
        low_level_roles = ["sales"]
        
        if resource in high_privilege_resources and role in low_level_roles:
            if action in ["delete", "update"]:
                return True, "unauthorized_access"
        
        # 未检测到异常
        return False, None
    
    @staticmethod
    async def create_audit_log(
        session: AsyncSession,
        user_id: str,
        role: str,
        resource: str,
        action: str,
        ip_address: str,
        details: Optional[Dict] = None
    ) -> PermissionAuditLog:
        """
        创建权限审计日志
        
        Args:
            session: 数据库会话
            user_id: 用户 ID
            role: 角色名称
            resource: 资源名称
            action: 操作类型
            ip_address: IP 地址
            details: 详细信息
            
        Returns:
            PermissionAuditLog: 创建的审计日志
        """
        # 检测异常
        is_anomaly, anomaly_type = await PermissionAuditService.detect_anomaly(
            session, user_id, resource, action, ip_address, role
        )
        
        # 创建审计日志
        audit_log = PermissionAuditLog(
            user_id=user_id,
            role=role,
            resource=resource,
            action=action,
            ip_address=ip_address,
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            details=details
        )
        
        session.add(audit_log)
        await session.commit()
        await session.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    async def export_audit_logs(
        session: AsyncSession,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "csv"
    ) -> str:
        """
        导出权限审计记录
        
        Args:
            session: 数据库会话
            user_id: 用户 ID（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            format: 导出格式（csv/json）
            
        Returns:
            str: 导出的文件内容
        """
        # 查询所有符合条件的记录（不分页）
        conditions = []
        
        if user_id:
            conditions.append(PermissionAuditLog.user_id == user_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            conditions.append(PermissionAuditLog.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            end_dt = end_dt + timedelta(days=1)
            conditions.append(PermissionAuditLog.timestamp < end_dt)
        
        query = select(PermissionAuditLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PermissionAuditLog.timestamp.desc())
        
        result = await session.execute(query)
        logs = result.scalars().all()
        
        if format.lower() == "csv":
            # 生成 CSV 格式
            csv_lines = ["id,user_id,role,resource,action,timestamp,ip_address,is_anomaly,anomaly_type"]
            for log in logs:
                csv_lines.append(
                    f"{log.id},{log.user_id},{log.role},{log.resource},{log.action},"
                    f"{log.timestamp.isoformat()},{log.ip_address},{log.is_anomaly},{log.anomaly_type or ''}"
                )
            return "\n".join(csv_lines)
        else:
            # 生成 JSON 格式
            import json
            return json.dumps([log.to_dict() for log in logs], ensure_ascii=False, indent=2)

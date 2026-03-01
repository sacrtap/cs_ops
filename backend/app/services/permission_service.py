"""
Permission Service - 权限服务层

集中式权限检查服务，实现 4 级 RBAC 权限验证。
已集成权限继承机制。
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ..models.role_permission import RolePermission
from ..models.user import User, UserRole
from .permission_inheritance_service import PermissionInheritanceService


# 权限缓存（生产环境建议使用 Redis）
_permission_cache: dict[tuple[str, str, str], bool] = {}


async def check_permission(
    role: str,
    resource: str,
    action: str,
    session: Optional[AsyncSession] = None
) -> bool:
    """
    检查角色是否有权限执行特定操作
    
    Args:
        role: 角色名称（admin, manager, specialist, sales）
        resource: 资源名称（customer, settlement, report, user, role）
        action: 操作类型（create, read, update, delete, view）
        session: 数据库会话（用于查询动态权限矩阵）
    
    Returns:
        bool: True 如果有权限，False 如果无权限
    
    Examples:
        >>> await check_permission("admin", "customer", "delete")
        True
        >>> await check_permission("sales", "customer", "delete")
        False
    """
    cache_key = (role, resource, action)
    
    # 检查缓存
    if cache_key in _permission_cache:
        return _permission_cache[cache_key]
    
    # Admin 拥有所有权限（快速路径）
    if role == UserRole.ADMIN.value:
        _permission_cache[cache_key] = True
        return True
    
    # 如果未提供 session，使用硬编码的权限矩阵（降级模式）
    if session is None:
        result = _check_static_permission(role, resource, action)
        _permission_cache[cache_key] = result
        return result
    
    # 使用权限继承服务检查权限（支持继承）
    try:
        result = await PermissionInheritanceService.check_permission_with_inheritance(
            role,
            resource,
            action,
            session
        )
        
        has_permission = result["has_permission"]
        _permission_cache[cache_key] = has_permission
        return has_permission
    except Exception:
        # 数据库查询失败时降级到静态权限检查
        result = _check_static_permission(role, resource, action)
        _permission_cache[cache_key] = result
        return result


def _check_static_permission(role: str, resource: str, action: str) -> bool:
    """
    静态权限矩阵检查（无数据库依赖）
    
    权限矩阵:
    ```
    Resource →    Customer    Settlement    Report    User    Role
    Role ↓
    Admin          ALL         ALL          ALL       ALL     ALL
    经理          CRUD        CRUD         VIEW      READ    -
    专员          CRUD        READ         VIEW      -       -
    销售          READ        -            -         -       -
    ```
    """
    # 定义每个角色的权限矩阵
    permissions = {
        UserRole.ADMIN.value: {
            # Admin 拥有所有权限
            "all": True
        },
        UserRole.MANAGER.value: {
            # 经理：除角色管理外的所有业务功能
            "customer": {"create", "read", "update", "delete"},
            "settlement": {"create", "read", "update", "delete"},
            "report": {"view", "export"},
            "user": {"read", "update"},  # 可以更新用户角色
        },
        UserRole.SPECIALIST.value: {
            # 专员：客户管理和结算处理
            "customer": {"create", "read", "update", "delete"},
            "settlement": {"read"},
            "report": {"view"},
            "user": {"read"},
        },
        UserRole.SALES.value: {
            # 销售：仅客户查看和创建
            "customer": {"create", "read"},
        },
    }
    
    # Admin 快速路径
    if role == UserRole.ADMIN.value:
        return True
    
    # 检查角色是否存在
    if role not in permissions:
        return False
    
    # 检查资源权限
    role_permissions = permissions[role]
    if resource not in role_permissions:
        return False
    
    # 检查操作权限
    return action in role_permissions[resource]


async def get_user_permissions(
    role: str,
    session: Optional[AsyncSession] = None
) -> dict[str, dict[str, list[str]]]:
    """
    获取角色的所有权限
    
    Args:
        role: 角色名称
        session: 数据库会话
    
    Returns:
        dict: {resource: {action: [permissions]}}
    """
    # Admin 特殊处理
    if role == UserRole.ADMIN.value:
        return {"all": {"all": ["*"]}}
    
    # 如果未提供 session，返回静态权限矩阵
    if session is None:
        return _get_static_permissions(role)
    
    # 从数据库查询权限矩阵
    try:
        stmt = select(RolePermission).where(RolePermission.role == role)
        result = await session.execute(stmt)
        permissions_list = result.scalars().all()
        
        # 组织权限数据结构
        permissions: dict[str, dict[str, list[str]]] = {}
        for perm in permissions_list:
            if perm.resource not in permissions:
                permissions[perm.resource] = {}
            if perm.action not in permissions[perm.resource]:
                permissions[perm.resource][perm.action] = []
            permissions[perm.resource][perm.action].append(perm.role)
        
        return permissions
    except Exception:
        # 数据库查询失败时降级到静态权限矩阵
        return _get_static_permissions(role)


def _get_static_permissions(role: str) -> dict[str, dict[str, list[str]]]:
    """获取角色的静态权限矩阵"""
    permissions = {
        UserRole.ADMIN.value: {"all": {"all": ["*"]}},
        UserRole.MANAGER.value: {
            "customer": {"create": [], "read": [], "update": [], "delete": []},
            "settlement": {"create": [], "read": [], "update": [], "delete": []},
            "report": {"view": [], "export": []},
            "user": {"read": [], "update": []},
        },
        UserRole.SPECIALIST.value: {
            "customer": {"create": [], "read": [], "update": [], "delete": []},
            "settlement": {"read": []},
            "report": {"view": []},
            "user": {"read": []},
        },
        UserRole.SALES.value: {
            "customer": {"create": [], "read": []},
        },
    }
    
    return permissions.get(role, {})


async def get_available_roles() -> list[dict]:
    """
    获取所有可用角色列表
    
    Returns:
        list[dict]: 角色信息列表，包含 role, name, level, description
    """
    roles = [
        {
            "role": UserRole.ADMIN.value,
            "name": "Admin",
            "level": 4,
            "description": "系统管理员，拥有所有功能和数据的权限"
        },
        {
            "role": UserRole.MANAGER.value,
            "name": "经理",
            "level": 3,
            "description": "运营经理，拥有除系统配置外的所有业务功能权限"
        },
        {
            "role": UserRole.SPECIALIST.value,
            "name": "专员",
            "level": 2,
            "description": "运营专员，负责客户管理和结算处理"
        },
        {
            "role": UserRole.SALES.value,
            "name": "销售",
            "level": 1,
            "description": "销售人员，仅可查看和管理自己的客户"
        },
    ]
    return roles


def clear_permission_cache():
    """清除权限缓存（在权限矩阵更新后调用）"""
    _permission_cache.clear()

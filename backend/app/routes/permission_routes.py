"""
Permission Routes - 权限管理 API 路由

提供权限矩阵查询、角色管理等功能。
"""
from sanic import Blueprint, Request, json
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from ..schemas.permission import (
    RoleResponse,
    RoleListResponse,
    PermissionMatrixResponse,
    PermissionCheckRequest,
    PermissionCheckResponse,
    PermissionMatrixUpdateRequest,
    PermissionMatrixUpdateResponse,
)
from ..models.user import User, UserRole
from ..models.role_permission import RolePermission
from ..middleware.auth_middleware import AuthMiddleware
from ..middleware.permission_middleware import PermissionMiddleware
from ..services.permission_service import (
    check_permission,
    get_user_permissions,
    get_available_roles,
    clear_permission_cache
)
from datetime import datetime, timezone

# 创建 Blueprint
permission_bp = Blueprint("Permission", url_prefix="/api/v1/permissions")


@permission_bp.route("/roles", methods=["GET"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("role", "read")
async def get_roles(request: Request):
    """
    获取所有可用角色列表
    
    Returns:
        {
            "data": [
                {
                    "role": "admin",
                    "name": "Admin",
                    "level": 4,
                    "description": "系统管理员，拥有所有功能和数据的权限"
                },
                ...
            ],
            "meta": {...}
        }
    """
    roles = await get_available_roles()
    
    return json({
        "data": roles,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(roles)
        }
    })


@permission_bp.route("/matrix", methods=["GET"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("role", "read")
async def get_permission_matrix(request: Request):
    """
    获取完整的权限矩阵
    
    Returns:
        {
            "data": {
                "admin": {
                    "customer": ["create", "read", "update", "delete"],
                    "settlement": ["create", "read", "update", "delete"],
                    ...
                },
                "manager": {...},
                ...
            },
            "meta": {...}
        }
    """
    db: AsyncSession = request.ctx.db
    
    # 查询数据库中存储的权限矩阵
    result = await db.execute(select(RolePermission))
    permissions_list = result.scalars().all()
    
    # 组织数据结构
    matrix: Dict[str, Dict[str, List[str]]] = {}
    for perm in permissions_list:
        if perm.role not in matrix:
            matrix[perm.role] = {}
        if perm.resource not in matrix[perm.role]:
            matrix[perm.role][perm.resource] = []
        matrix[perm.role][perm.resource].append(perm.action)
    
    # 如果没有数据，返回静态权限矩阵
    if not matrix:
        for role in UserRole:
            matrix[role.value] = await get_user_permissions(role.value)
    
    return json({
        "data": matrix,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "roles_count": len(matrix)
        }
    })


@permission_bp.route("/check", methods=["POST"])
@AuthMiddleware.require_auth
async def check_user_permission(request: Request):
    """
    检查当前用户是否有特定权限
    
    Request Body:
        {
            "resource": "customer",
            "action": "delete"
        }
    
    Returns:
        {
            "data": {
                "has_permission": true,
                "role": "manager",
                "resource": "customer",
                "action": "delete"
            },
            "meta": {...}
        }
    """
    user: User = request.ctx.current_user
    db: AsyncSession = request.ctx.db
    
    data = request.json
    resource = data.get("resource")
    action = data.get("action")
    
    if not resource or not action:
        return json({
            "data": None,
            "error": {
                "code": "INVALID_REQUEST",
                "message": "缺少必需字段：resource, action"
            }
        }, status=400)
    
    has_permission = await check_permission(
        user.role.value,
        resource,
        action,
        db
    )
    
    return json({
        "data": {
            "has_permission": has_permission,
            "role": user.role.value,
            "resource": resource,
            "action": action
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })


@permission_bp.route("/users/<user_id:int>/role", methods=["PUT"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("user", "update")
async def update_user_role(request: Request, user_id: int):
    """
    更新用户角色（仅 Manager 及以上角色）
    
    Request Body:
        {
            "role": "manager"  # 新角色
        }
    
    Returns:
        {
            "data": {
                "success": true,
                "message": "用户角色已更新",
                "user": {...}
            },
            "meta": {...}
        }
    """
    user: User = request.ctx.current_user
    db: AsyncSession = request.ctx.db
    
    data = request.json
    new_role = data.get("role")
    
    if not new_role:
        return json({
            "data": None,
            "error": {
                "code": "INVALID_REQUEST",
                "message": "缺少必需字段：role"
            }
        }, status=400)
    
    # 验证角色有效性
    if new_role not in [r.value for r in UserRole]:
        return json({
            "data": None,
            "error": {
                "code": "INVALID_ROLE",
                "message": f"无效的角色：{new_role}。有效值：admin, manager, specialist, sales"
            }
        }, status=400)
    
    # 查询目标用户
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        return json({
            "data": None,
            "error": {
                "code": "USER_NOT_FOUND",
                "message": f"用户不存在：{user_id}"
            }
        }, status=404)
    
    # 权限检查：不能修改比自己角色高的用户
    role_hierarchy = {
        UserRole.SALES.value: 1,
        UserRole.SPECIALIST.value: 2,
        UserRole.MANAGER.value: 3,
        UserRole.ADMIN.value: 4,
    }
    
    current_user_level = role_hierarchy.get(user.role.value, 0)
    target_user_level = role_hierarchy.get(target_user.role.value, 0)
    new_role_level = role_hierarchy.get(new_role, 0)
    
    # 不能修改比自己角色级别高或相等的用户
    if target_user_level >= current_user_level:
        return json({
            "data": None,
            "error": {
                "code": "PERMISSION_DENIED",
                "message": "您没有权限修改该用户的角色"
            }
        }, status=403)
    
    # 不能将用户角色提升到比自己高
    if new_role_level > current_user_level:
        return json({
            "data": None,
            "error": {
                "code": "PERMISSION_DENIED",
                "message": "您没有权限将用户角色提升到比您更高的级别"
            }
        }, status=403)
    
    # Admin 可以修改任何用户角色（包括提升自己）
    if user.role == UserRole.ADMIN:
        pass  # Admin 无限制
    
    try:
        # 更新用户角色
        target_user.role = UserRole(new_role)
        target_user.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(target_user)
        
        return json({
            "data": {
                "success": True,
                "message": f"用户 {target_user.username} 角色已更新为 {new_role}",
                "user": target_user.to_dict()
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        })
    
    except Exception as e:
        await db.rollback()
        return json({
            "data": None,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"更新用户角色失败：{str(e)}"
            }
        }, status=500)
@permission_bp.route("/matrix", methods=["PUT"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("role", "update")
async def update_permission_matrix(request: Request):
    """
    更新权限矩阵（仅 Admin）
    
    Request Body:
        {
            "role": "manager",
            "resource": "customer",
            "action": "delete",
            "enabled": true  # true=添加权限，false=移除权限
        }
    
    Returns:
        {
            "data": {
                "success": true,
                "message": "权限已更新"
            },
            "meta": {...}
        }
    """
    user: User = request.ctx.current_user
    db: AsyncSession = request.ctx.db
    
    # 仅 Admin 可以修改权限矩阵
    if user.role != UserRole.ADMIN:
        return json({
            "data": None,
            "error": {
                "code": "PERMISSION_DENIED",
                "message": "仅 Admin 可以修改权限矩阵"
            }
        }, status=403)
    
    data = request.json
    role = data.get("role")
    resource = data.get("resource")
    action = data.get("action")
    enabled = data.get("enabled", True)
    
    if not all([role, resource, action]):
        return json({
            "data": None,
            "error": {
                "code": "INVALID_REQUEST",
                "message": "缺少必需字段：role, resource, action"
            }
        }, status=400)
    
    # 验证角色有效性
    if role not in [r.value for r in UserRole]:
        return json({
            "data": None,
            "error": {
                "code": "INVALID_ROLE",
                "message": f"无效的角色：{role}"
            }
        }, status=400)
    
    try:
        if enabled:
            # 添加权限（使用 INSERT ... ON CONFLICT DO NOTHING）
            new_permission = RolePermission(
                role=role,
                resource=resource,
                action=action,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_permission)
            await db.flush()  # 触发 INSERT
        else:
            # 移除权限
            stmt = (
                update(RolePermission)
                .where(
                    RolePermission.role == role,
                    RolePermission.resource == resource,
                    RolePermission.action == action
                )
            )
            await db.execute(stmt)
            await db.commit()
        
        await db.commit()
        
        # 清除权限缓存
        clear_permission_cache()
        
        return json({
            "data": {
                "success": True,
                "message": "权限已更新" if enabled else "权限已移除"
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        })
    
    except Exception as e:
        await db.rollback()
        return json({
            "data": None,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"更新权限失败：{str(e)}"
            }
        }, status=500)

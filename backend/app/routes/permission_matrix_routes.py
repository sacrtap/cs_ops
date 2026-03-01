"""
权限矩阵 API 路由
"""
from sanic import Blueprint
from sanic.response import json
from app.middleware.permission_matrix_middleware import require_permission
from app.services.permission_matrix_service import PermissionMatrixService
from app.schemas.permission_matrix import (
    PermissionUpdateRequest,
    PermissionBulkUpdateRequest,
    AllPermissionsResponse,
    PermissionCheckRequest,
    CacheStatsResponse,
)
from app.utils.response import success_response, error_response
from app.middleware.auth_middleware import AuthMiddleware
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# 创建 Blueprint
permission_matrix_bp = Blueprint("permission_matrix", url_prefix="/api/v1/permission-matrix")


@permission_matrix_bp.route("", methods=["GET"])
@AuthMiddleware.require_auth
async def get_permission_matrix(request):
    """
    获取所有角色的权限矩阵
    
    GET /api/v1/permission-matrix
    
    响应:
    {
        "data": {
            "admin": {"customer": {"read": true, ...}, ...},
            "manager": {...},
            "specialist": {...},
            "sales": {...}
        },
        "meta": {"timestamp": "...", "request_id": "..."}
    }
    """
    try:
        service = PermissionMatrixService(request.app.ctx.db_session)
        
        # 获取所有角色的权限
        roles = ["admin", "manager", "specialist", "sales"]
        all_permissions = {}
        
        for role in roles:
            permissions = await service.get_role_permissions(role)
            all_permissions[role] = permissions
        
        return success_response(
            data=all_permissions,
            meta={"total": len(roles)}
        )
    
    except Exception as e:
        logger.error(f"Error getting permission matrix: {e}")
        return error_response(
            status_code=500,
            message="获取权限矩阵失败",
            details={"error": str(e)}
        )


@permission_matrix_bp.route("", methods=["PUT"])
@AuthMiddleware.require_auth
@require_permission(module="permission", action="update")
async def update_permission(request):
    """
    更新单个权限配置
    
    PUT /api/v1/permission-matrix
    
    Body:
    {
        "role": "sales",
        "module": "reporting",
        "action": "read",
        "granted": true
    }
    """
    try:
        # 验证请求数据
        req_data = PermissionUpdateRequest(**request.json)
        
        service = PermissionMatrixService(request.app.ctx.db_session)
        
        # 更新权限
        matrix = await service.update_permission(
            role=req_data.role,
            module=req_data.module,
            action=req_data.action,
            granted=req_data.granted
        )
        
        return success_response(
            data={
                "success": True,
                "permission": matrix.to_dict() if matrix else None
            }
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=f"验证错误：{str(e)}",
            code="VALIDATION_ERROR"
        )
    
    except Exception as e:
        logger.error(f"Error updating permission: {e}")
        return error_response(
            status_code=500,
            message="更新权限失败",
            details={"error": str(e)}
        )


@permission_matrix_bp.route("/bulk", methods=["PUT"])
@AuthMiddleware.require_auth
@require_permission(module="permission", action="update")
async def bulk_update_permissions(request):
    """
    批量更新权限配置
    
    PUT /api/v1/permission-matrix/bulk
    
    Body:
    {
        "permissions": [
            {"role": "sales", "module": "reporting", "action": "read", "granted": true},
            ...
        ]
    }
    """
    try:
        # 验证请求数据
        req_data = PermissionBulkUpdateRequest(**request.json)
        
        service = PermissionMatrixService(request.app.ctx.db_session)
        
        # 批量更新
        updated_count = await service.bulk_update_permissions(req_data.permissions)
        
        return success_response(
            data={
                "success": True,
                "updated_count": updated_count
            }
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=f"验证错误：{str(e)}",
            code="VALIDATION_ERROR"
        )
    
    except Exception as e:
        logger.error(f"Error bulk updating permissions: {e}")
        return error_response(
            status_code=500,
            message="批量更新权限失败",
            details={"error": str(e)}
        )


@permission_matrix_bp.route("/check", methods=["POST"])
@AuthMiddleware.require_auth
async def check_permission(request):
    """
    检查当前用户是否有指定权限
    
    POST /api/v1/permission-matrix/check
    
    Body:
    {
        "module": "customer",
        "action": "read"
    }
    
    Response:
    {
        "data": {
            "granted": true,
            "role": "sales",
            "module": "customer",
            "action": "read"
        },
        "meta": {
            "cache_hit": false
        }
    }
    """
    try:
        # 验证请求数据
        req_data = PermissionCheckRequest(**request.json)
        
        # 获取用户角色
        user = request.ctx.user
        role = user.role
        
        service = PermissionMatrixService(request.app.ctx.db_session)
        cache = service.cache
        
        # 检查缓存
        cached = await cache.get(role)
        cache_hit = cached is not None
        
        # 检查权限
        granted = await service.check_permission(role, req_data.module, req_data.action)
        
        return success_response(
            data={
                "granted": granted,
                "role": role,
                "module": req_data.module,
                "action": req_data.action
            },
            meta={
                "cache_hit": cache_hit,
                "cache_key": f"permission:{role}"
            }
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=f"验证错误：{str(e)}",
            code="VALIDATION_ERROR"
        )
    
    except Exception as e:
        logger.error(f"Error checking permission: {e}")
        return error_response(
            status_code=500,
            message="检查权限失败",
            details={"error": str(e)}
        )


@permission_matrix_bp.route("/cache/stats", methods=["GET"])
@AuthMiddleware.require_auth
@require_permission(module="permission", action="read")
async def get_cache_stats(request):
    """
    获取权限缓存统计信息
    
    GET /api/v1/permission-matrix/cache/stats
    
    Response:
    {
        "data": {
            "size": 4,
            "max_size": 128,
            "hits": 100,
            "misses": 10,
            "hit_rate": 90.91,
            "ttl_seconds": 1800
        }
    }
    """
    try:
        service = PermissionMatrixService(request.app.ctx.db_session)
        stats = await service.get_cache_stats()
        
        return success_response(data=stats)
    
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return error_response(
            status_code=500,
            message="获取缓存统计失败",
            details={"error": str(e)}
        )


@permission_matrix_bp.route("/cache", methods=["DELETE"])
@AuthMiddleware.require_auth
@require_permission(module="permission", action="update")
async def clear_cache(request):
    """
    清除权限缓存
    
    DELETE /api/v1/permission-matrix/cache?role=sales
    
    Query 参数:
    - role: 可选，指定清除某个角色的缓存；不指定则清除所有
    """
    try:
        role = request.args.get("role", None)
        
        service = PermissionMatrixService(request.app.ctx.db_session)
        await service.clear_cache(role)
        
        return success_response(
            data={
                "success": True,
                "cleared_role": role or "all"
            }
        )
    
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return error_response(
            status_code=500,
            message="清除缓存失败",
            details={"error": str(e)}
        )

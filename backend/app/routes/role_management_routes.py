"""
角色管理 API 路由
"""
from sanic import Blueprint
from sanic.response import json
from app.services.role_management_service import RoleManagementService
from app.schemas.role_management import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RolePermissionsUpdateRequest,
    RoleResponse,
    RoleWithPermissionsResponse,
    RoleListResponse,
    RoleStatsResponse,
)
from app.utils.response import success_response, error_response
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.permission_matrix_middleware import require_permission
import logging

logger = logging.getLogger(__name__)

# 创建 Blueprint
role_management_bp = Blueprint("role_management", url_prefix="/api/v1/roles")


@role_management_bp.route("", methods=["GET"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="read")
async def get_roles(request):
    """
    获取所有角色列表
    
    GET /api/v1/roles
    
    响应:
    {
        "data": [
            {"id": 1, "name": "admin", "description": "...", "status": "active", ...},
            ...
        ],
        "meta": {"total": 4}
    }
    """
    try:
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 获取所有角色
        roles = await service.get_all_roles()
        
        return success_response(
            data=roles,
            meta={"total": len(roles)}
        )
    
    except Exception as e:
        logger.error(f"Error getting roles: {e}")
        return error_response(
            status_code=500,
            message="获取角色列表失败",
            details={"error": str(e)}
        )


@role_management_bp.route("/stats", methods=["GET"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="read")
async def get_role_stats(request):
    """
    获取角色统计信息
    
    GET /api/v1/roles/stats
    
    响应:
    {
        "data": {
            "total_roles": 4,
            "active_roles": 4,
            "inactive_roles": 0,
            "roles": [...]
        }
    }
    """
    try:
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 获取统计信息
        stats = await service.get_role_stats()
        
        return success_response(data=stats)
    
    except Exception as e:
        logger.error(f"Error getting role stats: {e}")
        return error_response(
            status_code=500,
            message="获取角色统计失败",
            details={"error": str(e)}
        )


@role_management_bp.route("/<role_id:int>", methods=["GET"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="read")
async def get_role(request, role_id):
    """
    通过 ID 获取角色信息
    
    GET /api/v1/roles/1
    
    响应:
    {
        "data": {"id": 1, "name": "admin", ...}
    }
    """
    try:
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 获取角色
        role = await service.get_role_by_id(role_id)
        
        if not role:
            return error_response(
                status_code=404,
                message=f"角色 {role_id} 不存在",
                code="ROLE_NOT_FOUND"
            )
        
        return success_response(data=role)
    
    except Exception as e:
        logger.error(f"Error getting role: {e}")
        return error_response(
            status_code=500,
            message="获取角色失败",
            details={"error": str(e)}
        )


@role_management_bp.route("/<role_id:int>/permissions", methods=["GET"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="read")
async def get_role_permissions(request, role_id):
    """
    获取角色的所有权限
    
    GET /api/v1/roles/1/permissions
    
    响应:
    {
        "data": {
            "customer": {"read": true, "create": true, ...},
            ...
        }
    }
    """
    try:
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 获取角色权限
        permissions = await service.get_role_permissions(role_id)
        
        if permissions is None:
            return error_response(
                status_code=404,
                message=f"角色 {role_id} 不存在",
                code="ROLE_NOT_FOUND"
            )
        
        return success_response(data=permissions)
    
    except Exception as e:
        logger.error(f"Error getting role permissions: {e}")
        return error_response(
            status_code=500,
            message="获取角色权限失败",
            details={"error": str(e)}
        )


@role_management_bp.route("", methods=["POST"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="create")
async def create_role(request):
    """
    创建新角色
    
    POST /api/v1/roles
    
    Body:
    {
        "name": "custom_role",
        "description": "自定义角色",
        "status": "active"
    }
    """
    try:
        # 验证请求数据
        req_data = RoleCreateRequest(**request.json)
        
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 检查角色名称是否已存在
        existing_role = await service.get_role_by_name(req_data.name)
        if existing_role:
            return error_response(
                status_code=409,
                message=f"角色名称 '{req_data.name}' 已存在",
                code="ROLE_ALREADY_EXISTS"
            )
        
        # 创建角色
        role = await service.create_role(req_data.model_dump())
        
        return success_response(
            data=role,
            message="角色创建成功"
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=f"验证错误：{str(e)}",
            code="VALIDATION_ERROR"
        )
    
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        return error_response(
            status_code=500,
            message="创建角色失败",
            details={"error": str(e)}
        )


@role_management_bp.route("/<role_id:int>", methods=["PUT"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="update")
async def update_role(request, role_id):
    """
    更新角色信息
    
    PUT /api/v1/roles/1
    
    Body:
    {
        "name": "updated_name",
        "description": "更新描述",
        "status": "inactive"
    }
    """
    try:
        # 验证请求数据
        req_data = RoleUpdateRequest(**request.json)
        
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 更新角色
        role = await service.update_role(role_id, req_data.model_dump(exclude_unset=True))
        
        if not role:
            return error_response(
                status_code=404,
                message=f"角色 {role_id} 不存在",
                code="ROLE_NOT_FOUND"
            )
        
        return success_response(
            data=role,
            message="角色更新成功"
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=f"验证错误：{str(e)}",
            code="VALIDATION_ERROR"
        )
    
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        return error_response(
            status_code=500,
            message="更新角色失败",
            details={"error": str(e)}
        )


@role_management_bp.route("/<role_id:int>", methods=["DELETE"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="delete")
async def delete_role(request, role_id):
    """
    删除角色
    
    DELETE /api/v1/roles/1
    """
    try:
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 删除角色
        success = await service.delete_role(role_id)
        
        if not success:
            return error_response(
                status_code=404,
                message=f"角色 {role_id} 不存在",
                code="ROLE_NOT_FOUND"
            )
        
        return success_response(
            data={"success": True},
            message="角色删除成功"
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=str(e),
            code="ROLE_DELETION_FAILED"
        )
    
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        return error_response(
            status_code=500,
            message="删除角色失败",
            details={"error": str(e)}
        )


@role_management_bp.route("/<role_id:int>/permissions", methods=["PUT"])
@AuthMiddleware.require_auth
@require_permission(module="role", action="update")
async def update_role_permissions(request, role_id):
    """
    更新角色的权限配置
    
    PUT /api/v1/roles/1/permissions
    
    Body:
    {
        "permissions": {
            "customer": {
                "read": true,
                "create": true,
                "update": false,
                "delete": false
            },
            ...
        }
    }
    """
    try:
        # 验证请求数据
        req_data = RolePermissionsUpdateRequest(**request.json)
        
        service = RoleManagementService(request.app.ctx.db_session)
        
        # 更新角色权限
        role = await service.update_role_permissions(role_id, req_data.permissions)
        
        if not role:
            return error_response(
                status_code=404,
                message=f"角色 {role_id} 不存在",
                code="ROLE_NOT_FOUND"
            )
        
        return success_response(
            data=role,
            message="角色权限更新成功"
        )
    
    except ValueError as e:
        return error_response(
            status_code=400,
            message=str(e),
            code="VALIDATION_ERROR"
        )
    
    except Exception as e:
        logger.error(f"Error updating role permissions: {e}")
        return error_response(
            status_code=500,
            message="更新角色权限失败",
            details={"error": str(e)}
        )

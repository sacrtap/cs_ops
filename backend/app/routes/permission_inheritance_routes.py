"""
Permission Inheritance Routes - 权限继承路由

提供权限继承相关的 API 接口：
- GET /api/v1/roles/hierarchy - 获取角色层级结构
- GET /api/v1/roles/{role_name}/permissions - 获取角色权限（包含继承）
- POST /api/v1/permissions/check - 检查权限
- POST /api/v1/permissions/cache/clear - 清除缓存
- POST /api/v1/roles/{role_name}/permissions/additional - 添加额外授权
- DELETE /api/v1/roles/{role_name}/permissions/additional - 撤销额外授权
- GET /api/v1/roles/{role_name}/permissions/additional - 获取额外授权列表
"""
from sanic import Blueprint
from sanic.response import json
from ..services.permission_inheritance_service import PermissionInheritanceService
from ..models.user import UserRole
from ..middleware.permission_middleware import PermissionMiddleware
from ..middleware.auth_middleware import AuthMiddleware

permission_inheritance_bp = Blueprint('permission_inheritance', url_prefix='/api/v1')


@permission_inheritance_bp.route('/roles/hierarchy', methods=['GET'])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("role", "read")
async def get_role_hierarchy(request):
    """
    获取角色层级结构
    
    Returns:
        JSON: 角色层级结构
    """
    try:
        session = request.ctx.db
        hierarchy = await PermissionInheritanceService.get_role_hierarchy(session)
        
        return json({
            "success": True,
            "data": hierarchy
        }, status=200)
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_inheritance_bp.route('/roles/<role_name:string>/permissions', methods=['GET'])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("role", "read")
async def get_role_permissions(request, role_name):
    """
    获取角色的所有权限（包含继承权限）
    
    Args:
        role_name: 角色名称
    
    Returns:
        JSON: 角色权限信息
    """
    try:
        session = request.ctx.db
        permissions = await PermissionInheritanceService.get_role_permissions_with_inheritance(
            role_name,
            session
        )
        
        if "error" in permissions:
            return json({
                "success": False,
                "message": permissions["error"]
            }, status=404)
        
        return json({
            "success": True,
            "data": permissions
        }, status=200)
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_inheritance_bp.route('/permissions/check', methods=['POST'])
@AuthMiddleware.require_auth
async def check_permission(request):
    """
    检查权限（支持继承和额外授权）
    
    Request Body:
        role: 角色名称
        resource: 资源名称
        action: 操作类型
    
    Returns:
        JSON: 权限检查结果
    """
    try:
        data = request.json
        role = data.get('role')
        resource = data.get('resource')
        action = data.get('action')
        
        if not all([role, resource, action]):
            return json({
                "success": False,
                "message": "Missing required fields: role, resource, action"
            }, status=400)
        
        session = request.ctx.db
        result = await PermissionInheritanceService.check_permission_with_inheritance(
            role, resource, action, session
        )
        
        return json({
            "success": True,
            "data": result
        }, status=200)
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_inheritance_bp.route('/permissions/cache/clear', methods=['POST'])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("role", "delete")
async def clear_permission_cache(request):
    """
    清除权限缓存（管理员操作）
    
    Returns:
        JSON: 操作结果
    """
    try:
        PermissionInheritanceService.clear_cache()
        
        return json({
            "success": True,
            "message": "Permission cache cleared successfully"
        }, status=200)
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


# ==================== 额外授权管理 API ====================

@permission_inheritance_bp.route('/roles/<role_name:string>/permissions/additional', methods=['POST'])
@AuthMiddleware.require_auth
async def grant_additional_permission(request, role_name):
    """
    为角色添加额外授权
    
    Request Body:
        resource: 资源名称
        action: 操作类型
    
    Returns:
        JSON: 授权结果
    """
    try:
        data = request.json
        resource = data.get('resource')
        action = data.get('action')
        
        if not resource or not action:
            return json({
                "success": False,
                "message": "Missing required fields: resource, action"
            }, status=400)
        
        session = request.ctx.db
        result = await PermissionInheritanceService.grant_additional_permission(
            role_name, resource, action, session
        )
        await session.commit()
        
        status_code = 200 if result["success"] else 400
        return json(result, status=status_code)
        
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_inheritance_bp.route('/roles/<role_name:string>/permissions/additional', methods=['DELETE'])
@AuthMiddleware.require_auth
async def revoke_additional_permission(request, role_name):
    """
    撤销角色的额外授权
    
    Query Parameters:
        resource: 资源名称
        action: 操作类型
    
    Returns:
        JSON: 撤销结果
    """
    try:
        resource = request.args.get('resource')
        action = request.args.get('action')
        
        if not resource or not action:
            return json({
                "success": False,
                "message": "Missing required parameters: resource, action"
            }, status=400)
        
        session = request.ctx.db
        result = await PermissionInheritanceService.revoke_additional_permission(
            role_name, resource, action, session
        )
        await session.commit()
        
        status_code = 200 if result["success"] else 400
        return json(result, status=status_code)
        
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_inheritance_bp.route('/roles/<role_name:string>/permissions/additional', methods=['GET'])
@AuthMiddleware.require_auth
async def get_additional_permissions(request, role_name):
    """
    获取角色的所有额外授权
    
    Returns:
        JSON: 额外授权列表
    """
    try:
        session = request.ctx.db
        result = await PermissionInheritanceService.get_additional_permissions(
            role_name, session
        )
        
        if result["success"]:
            return json(result, status=200)
        else:
            return json(result, status=400)
            
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)

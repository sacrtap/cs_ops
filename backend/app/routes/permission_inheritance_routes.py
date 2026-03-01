"""
Permission Inheritance Routes - 权限继承路由

提供权限继承相关的 API 接口：
- GET /api/v1/roles/hierarchy - 获取角色层级结构
- GET /api/v1/roles/{role_name}/permissions - 获取角色权限（包含继承）
- POST /api/v1/permissions/check - 检查权限
"""
from sanic import Blueprint
from sanic.response import json
from sanic_jwt import protected
from ..services.permission_inheritance_service import PermissionInheritanceService
from ..models.user import UserRole
from ..middleware.permission_middleware import PermissionMiddleware

permission_inheritance_bp = Blueprint('permission_inheritance', url_prefix='/api/v1')


@permission_inheritance_bp.route('/roles/hierarchy', methods=['GET'])
@protected()
@PermissionMiddleware.require_permission("role", "read")
async def get_role_hierarchy(request):
    """
    获取角色层级结构
    
    Returns:
        JSON: 角色层级结构
    """
    try:
        async with request.app.ctx.db_session() as session:
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
@protected()
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
        async with request.app.ctx.db_session() as session:
            permissions = await PermissionInheritanceService.get_role_permissions_with_inheritance(
                role_name,
                session
            )
            
            if "error" in permissions:
                return json({
                    "success": False,
                    "error": permissions["error"]
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
@protected()
async def check_permission(request):
    """
    检查角色是否有权限执行特定操作
    
    Request Body:
        role: 角色名称
        resource: 资源名称
        action: 操作类型
    
    Returns:
        JSON: 权限检查结果
    """
    try:
        data = request.json
        role_name = data.get('role')
        resource = data.get('resource')
        action = data.get('action')
        
        if not all([role_name, resource, action]):
            return json({
                "success": False,
                "error": "Missing required fields: role, resource, action"
            }, status=400)
        
        async with request.app.ctx.db_session() as session:
            result = await PermissionInheritanceService.check_permission_with_inheritance(
                role_name,
                resource,
                action,
                session
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
@protected()
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

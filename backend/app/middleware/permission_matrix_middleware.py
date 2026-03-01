"""
功能权限中间件 - 验证用户是否有访问某功能的权限
"""
from functools import wraps
from sanic import Request
from sanic.exceptions import HTTPException
from typing import Tuple, Optional
from app.utils.permission_cache import get_permission_cache
from app.services.permission_matrix_service import PermissionMatrixService
import logging

logger = logging.getLogger(__name__)


def require_permission(module: str, action: str):
    """
    权限验证装饰器
    
    用法:
        @permission_bp.route("/settlement", methods=["POST"])
        @require_permission(module="settlement", action="create")
        async def create_settlement(request):
            ...
    
    Args:
        module: 功能模块名称
        action: 操作类型
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            # 获取用户角色（从 JWT 中间件设置）
            if not hasattr(request.ctx, 'user') or not request.ctx.user:
                raise HTTPException(
                    status_code=401,
                    message="未认证用户"
                )
            
            user = request.ctx.user
            role = user.role
            
            # 跳过 Admin 的权限检查（Admin 拥有所有权限）
            if role == 'admin':
                return await f(request, *args, **kwargs)
            
            # 检查权限
            cache = get_permission_cache()
            cached_perms = await cache.get(role)
            
            if cached_perms:
                # 从缓存检查
                has_permission = (
                    module in cached_perms and
                    action in cached_perms[module] and
                    cached_perms[module][action]
                )
            else:
                # 从数据库检查
                service = PermissionMatrixService(request.app.ctx.db_session)
                has_permission = await service.check_permission(role, module, action)
                
                # 写入缓存
                permissions = await service.get_role_permissions(role)
                await cache.set(role, permissions)
            
            if not has_permission:
                # 记录越权访问日志
                logger.warning(
                    f"Permission denied: user={user.username}, role={role}, "
                    f"module={module}, action={action}, path={request.path}"
                )
                
                raise HTTPException(
                    status_code=403,
                    message="您没有权限访问此功能",
                    context={
                        "required_module": module,
                        "required_action": action,
                        "user_role": role,
                        "user_id": user.id,
                        "username": user.username
                    }
                )
            
            return await f(request, *args, **kwargs)
        
        return decorated_function
    return decorator


async def check_permission(request: Request, module: str, action: str) -> bool:
    """
    检查用户是否有指定权限（非装饰器方式）
    
    用法:
        @permission_bp.route("/check")
        async def check_perms(request):
            has_access = await check_permission(request, "customer", "read")
            if not has_access:
                raise HTTPException(status_code=403, message="无权限")
    
    Args:
        request: Sanic 请求对象
        module: 功能模块
        action: 操作类型
        
    Returns:
        True 如果有权限，False 如果无权限
    """
    if not hasattr(request.ctx, 'user') or not request.ctx.user:
        return False
    
    user = request.ctx.user
    role = user.role
    
    # Admin 拥有所有权限
    if role == 'admin':
        return True
    
    # 检查缓存
    cache = get_permission_cache()
    cached_perms = await cache.get(role)
    
    if cached_perms:
        return (
            module in cached_perms and
            action in cached_perms[module] and
            cached_perms[module][action]
        )
    
    # 从数据库检查
    service = PermissionMatrixService(request.app.ctx.db_session)
    return await service.check_permission(role, module, action)

"""
Permission Middleware - 权限验证中间件

基于角色 - 资源 - 操作的细粒度权限验证中间件。
提供装饰器用于路由级别的权限控制。
"""
from functools import wraps
from typing import Optional, Callable
from sanic import Request, HTTPResponse
from sanic.exceptions import Forbidden, Unauthorized
from sanic.log import logger
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User, UserRole
from ..services.permission_service import check_permission
from ..utils.data_permission_filter import set_current_user_context, apply_data_permission_filter
import json


class PermissionMiddleware:
    """
    权限验证中间件
    
    功能:
    - 基于资源 + 操作的权限检查
    - 自动记录权限拒绝日志
    - 注入用户权限上下文到 data_permission_filter
    """
    
    @staticmethod
    def require_permission(resource: str, action: str):
        """
        装饰器：要求特定资源和操作的权限
        
        Args:
            resource: 资源名称（customer, settlement, report, user, role）
            action: 操作类型（create, read, update, delete, view, export）
        
        Usage:
            @bp.route("/customers", methods=["POST"])
            @AuthMiddleware.require_auth
            @PermissionMiddleware.require_permission("customer", "create")
            async def create_customer(request):
                ...
        """
        def decorator(f: Callable):
            @wraps(f)
            async def decorated_function(request: Request, *args, **kwargs):
                # 确保已认证（require_roles 或 require_auth 应该已经调用）
                if not hasattr(request.ctx, 'current_user'):
                    raise Unauthorized("请先进行身份认证")
                
                user: User = request.ctx.current_user
                user_role = user.role.value
                user_id = user.id
                org_id = user.org_id if hasattr(user, 'org_id') else None
                
                # 设置当前用户上下文（用于数据权限过滤）
                request.ctx.user_context = set_current_user_context(user_id, user_role, org_id)
                
                try:
                    # 检查权限
                    has_permission = await check_permission(
                        user_role,
                        resource,
                        action,
                        request.ctx.db
                    )
                    
                    if not has_permission:
                        # 记录权限拒绝日志
                        logger.warning(
                            f"Permission denied: user_id={user_id}, username={user.username}, "
                            f"role={user_role}, resource={resource}, action={action}"
                        )
                        
                        # 返回 403 错误
                        raise Forbidden(
                            "您没有权限执行此操作",
                            extra={
                                "code": "PERMISSION_DENIED",
                                "required_permission": f"{resource}:{action}",
                                "user_role": user_role
                            }
                        )
                    
                    # 权限通过，继续执行
                    return await f(request, *args, **kwargs)
                
                finally:
                    # 清除用户上下文（可选）
                    if hasattr(request.ctx, 'user_context'):
                        delattr(request.ctx, 'user_context')
            
            return decorated_function
        
        return decorator
    
    @staticmethod
    def require_any_permission(*permissions: tuple[str, str]):
        """
        装饰器：要求多个权限中的任意一个
        
        Args:
            *permissions: 权限列表，每个权限是 (resource, action) 元组
        
        Usage:
            @bp.route("/dashboard")
            @AuthMiddleware.require_auth
            @PermissionMiddleware.require_any_permission(
                ("customer", "read"),
                ("settlement", "read"),
                ("report", "view")
            )
            async def dashboard(request):
                ...
        """
        def decorator(f: Callable):
            @wraps(f)
            async def decorated_function(request: Request, *args, **kwargs):
                if not hasattr(request.ctx, 'current_user'):
                    raise Unauthorized("请先进行身份认证")
                
                user: User = request.ctx.current_user
                user_role = user.role.value
                
                # 检查是否至少有一个权限
                has_any_permission = False
                for resource, action in permissions:
                    if await check_permission(user_role, resource, action, request.ctx.db):
                        has_any_permission = True
                        break
                
                if not has_any_permission:
                    logger.warning(
                        f"Permission denied: user_id={user.id}, role={user_role}, "
                        f"required_any={permissions}"
                    )
                    raise Forbidden("您没有权限访问此资源")
                
                return await f(request, *args, **kwargs)
            
            return decorated_function
        
        return decorator
    
    @staticmethod
    def require_all_permissions(*permissions: tuple[str, str]):
        """
        装饰器：要求所有权限
        
        Args:
            *permissions: 权限列表，每个权限是 (resource, action) 元组
        
        Usage:
            @bp.route("/reports/full")
            @AuthMiddleware.require_auth
            @PermissionMiddleware.require_all_permissions(
                ("customer", "read"),
                ("settlement", "read"),
                ("report", "view")
            )
            async def full_report(request):
                ...
        """
        def decorator(f: Callable):
            @wraps(f)
            async def decorated_function(request: Request, *args, **kwargs):
                if not hasattr(request.ctx, 'current_user'):
                    raise Unauthorized("请先进行身份认证")
                
                user: User = request.ctx.current_user
                user_role = user.role.value
                
                # 检查是否所有权限都具备
                for resource, action in permissions:
                    if not await check_permission(user_role, resource, action, request.ctx.db):
                        logger.warning(
                            f"Permission denied: user_id={user.id}, role={user_role}, "
                            f"missing_permission={resource}:{action}"
                        )
                        raise Forbidden(f"您没有权限执行此操作：{resource}:{action}")
                
                return await f(request, *args, **kwargs)
            
            return decorated_function
        
        return decorator


async def setup_permission_middleware(app):
    """
    设置权限中间件（在应用启动时调用）
    
    Args:
        app: Sanic 应用实例
    """
    @app.middleware("request")
    async def before_request(request):
        """请求前：初始化权限上下文"""
        request.ctx.permission_checked = False
    
    @app.middleware("response")
    async def after_response(request, response):
        """响应后：清理权限上下文"""
        clear_current_user()

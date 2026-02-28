"""
JWT 认证中间件 - 验证请求 Token 并注入用户信息

功能：
- Token 签名验证
- Token 过期检查
- Token 黑名单检查
- 用户信息注入
"""
from functools import wraps
from typing import Optional
from sanic import Request, HTTPResponse
from sanic.exceptions import Unauthorized, Forbidden
from jose import JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.token_service import token_service
from app.services.token_blacklist_service import TokenBlacklistService
from app.models.user import User, UserRole, UserStatus
import hashlib


class AuthMiddleware:
    """JWT 认证中间件"""

    @staticmethod
    async def authenticate(request: Request) -> Optional[User]:
        """
        验证请求的 JWT Token 并返回用户对象
        
        Args:
            request: Sanic 请求对象
            
        Returns:
            Optional[User]: 认证成功的用户对象，失败返回 None
            
        Raises:
            Unauthorized: Token 缺失或无效
            Forbidden: Token 过期或用户未激活
        """
        # 从 Header 获取 Token
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            raise Unauthorized("缺少认证 Token")

        token = auth_header.replace("Bearer ", "", 1)

        try:
            # 验证 Token
            payload = token_service.verify_token(token, token_type="access")
            user_id = int(payload["sub"])
            username = payload["username"]
            role = UserRole(payload["role"])

        except JWTError as e:
            raise Unauthorized("认证令牌无效或已过期")
        except JWTClaimsError as e:
            raise Unauthorized("认证令牌无效或已过期")
        except (KeyError, ValueError):
            raise Unauthorized("认证令牌无效或已过期")

        # 检查 Token 是否在黑名单中
        db: AsyncSession = request.ctx.db
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        blacklist_service = TokenBlacklistService(db)
        is_blacklisted = await blacklist_service.is_blacklisted(token_hash)
        
        if is_blacklisted:
            raise Unauthorized("认证令牌已失效")

        # 查询用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise Unauthorized("用户不存在")

        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise Forbidden("账户已被禁用")

        # 将用户信息注入请求上下文
        request.ctx.current_user = user
        request.ctx.user_id = user.id
        request.ctx.username = user.username
        request.ctx.user_role = user.role

        return user

    @staticmethod
    def require_auth(f):
        """
        装饰器：要求认证
        
        Usage:
            @bp.route("/protected")
            @AuthMiddleware.require_auth
            async def protected_route(request):
                user = request.ctx.current_user
                ...
        """
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            await AuthMiddleware.authenticate(request)
            return await f(request, *args, **kwargs)
        
        return decorated_function

    @staticmethod
    def require_roles(*allowed_roles: UserRole):
        """
        装饰器：要求特定角色
        
        Args:
            *allowed_roles: 允许的角色列表
            
        Usage:
            @bp.route("/admin")
            @AuthMiddleware.require_auth
            @AuthMiddleware.require_roles(UserRole.ADMIN)
            async def admin_route(request):
                ...
        """
        def decorator(f):
            @wraps(f)
            async def decorated_function(request: Request, *args, **kwargs):
                # 先认证
                user = await AuthMiddleware.authenticate(request)
                
                # 检查角色
                if user.role not in allowed_roles:
                    raise Forbidden(f"需要权限：{', '.join([r.value for r in allowed_roles])}")
                
                return await f(request, *args, **kwargs)
            
            return decorated_function
        
        return decorator

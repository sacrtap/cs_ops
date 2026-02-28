"""
认证服务 - 用户认证、Token 管理、登录失败处理
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from app.models.user import User, UserRole, UserStatus
from app.utils.password import hash_password, verify_password
from app.services.token_service import token_service
from app.config.settings import settings


class AuthenticationError(Exception):
    """认证错误基类"""
    def __init__(self, code: str, message: str, status_code: int = 401):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidCredentialsError(AuthenticationError):
    """无效凭据错误"""
    def __init__(self, message: str = "用户名或密码错误"):
        super().__init__("INVALID_CREDENTIALS", message, 401)


class UserLockedError(AuthenticationError):
    """用户被锁定错误"""
    def __init__(self, locked_until: datetime):
        message = f"账户已被锁定，直到 {locked_until.strftime('%Y-%m-%d %H:%M:%S')}"
        super().__init__("USER_LOCKED", message, 403)


class UserInactiveError(AuthenticationError):
    """用户未激活错误"""
    def __init__(self):
        super().__init__("USER_INACTIVE", "账户已被禁用，请联系管理员", 403)


class TokenExpiredError(AuthenticationError):
    """Token 过期错误"""
    def __init__(self):
        super().__init__("TOKEN_EXPIRED", "Token 已过期，请重新登录", 401)


class TokenInvalidError(AuthenticationError):
    """Token 无效错误"""
    def __init__(self):
        super().__init__("TOKEN_INVALID", "Token 无效", 401)


class TokenUsedError(AuthenticationError):
    """Token 已被使用错误（防重放）"""
    def __init__(self):
        super().__init__("REFRESH_TOKEN_USED", "刷新令牌已被使用", 401)


class TokenRateLimitError(AuthenticationError):
    """Token 刷新速率限制错误"""
    def __init__(self):
        super().__init__("TOKEN_REFRESH_LIMIT_EXCEEDED", "Token 刷新过于频繁，请稍后再试", 429)


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(
        self,
        username: str,
        password: str,
        client_ip: Optional[str] = None
    ) -> Tuple[User, str, str]:
        """
        用户认证并生成 Token
        
        Args:
            username: 用户名
            password: 密码
            client_ip: 客户端 IP（用于记录）
            
        Returns:
            Tuple[User, str, str]: (用户对象，access_token, refresh_token)
            
        Raises:
            InvalidCredentialsError: 用户名或密码错误
            UserLockedError: 账户被锁定
            UserInactiveError: 账户被禁用
        """
        # 查询用户
        user = await self._get_user_by_username(username)
        if not user:
            # 防止用户枚举，统一错误消息
            raise InvalidCredentialsError()

        # 检查用户是否被锁定
        if user.is_locked():
            raise UserLockedError(user.locked_until)

        # 验证密码
        if not verify_password(password, user.password_hash):
            await self._record_failed_login(user, client_ip)
            raise InvalidCredentialsError()

        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise UserInactiveError()

        # 认证成功，更新登录信息
        await self._record_successful_login(user, client_ip)

        # 生成 Token
        access_token = token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        refresh_token = token_service.create_refresh_token(
            user_id=user.id,
            username=user.username
        )

        return user, access_token, refresh_token

    async def refresh_tokens(
        self,
        refresh_token: str,
        client_ip: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        刷新 Token（Refresh Token 单次使用 + 速率限制）
        
        Args:
            refresh_token: 刷新 Token
            client_ip: 客户端 IP
            
        Returns:
            Tuple[str, str]: (new_access_token, new_refresh_token)
            
        Raises:
            TokenInvalidError: Token 无效
            TokenExpiredError: Token 过期
            TokenUsedError: Token 已被使用（防重放）
            TokenRateLimitError: 刷新速率超限
            UserInactiveError: 用户未激活
        """
        import hashlib
        import time
        from datetime import datetime, timezone
        from jose import JWTError
        from jose.exceptions import JWTClaimsError
        
        try:
            # 验证 Refresh Token
            payload = token_service.verify_token(refresh_token, token_type="refresh")
            user_id = int(payload["sub"])
            username = payload["username"]
            token_jti = payload.get("jti")

        except JWTError:
            raise TokenInvalidError()
        except JWTClaimsError:
            raise TokenInvalidError()
        except (KeyError, ValueError):
            raise TokenInvalidError()

        # 查询用户
        user = await self._get_user_by_id(user_id)
        if not user:
            raise TokenInvalidError()

        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise UserInactiveError()

        # 速率限制检查（同一用户 1 分钟内最多 3 次）
        await self._check_token_refresh_rate_limit(user_id)

        # 计算 Token 哈希（用于检查是否已使用）
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # 检查 Token 是否已在黑名单中（已被使用）
        from app.models.token_blacklist import TokenBlacklist, TokenBlacklistType
        from sqlalchemy import select
        result = await self.db.execute(
            select(TokenBlacklist).where(
                TokenBlacklist.token_hash == token_hash,
                TokenBlacklist.token_type == TokenBlacklistType.REFRESH,
                TokenBlacklist.expires_at > datetime.now(timezone.utc)
            )
        )
        if result.scalar_one_or_none() is not None:
            raise TokenUsedError()

        # 生成新 Token
        new_access_token = token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        new_refresh_token = token_service.create_refresh_token(
            user_id=user.id,
            username=user.username
        )

        # 将旧 Refresh Token 加入黑名单（单次使用）
        from app.models.token_blacklist import BlacklistReason
        from app.services.token_blacklist_service import TokenBlacklistService
        
        # 解码旧 Token 获取过期时间
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        blacklist_service = TokenBlacklistService(self.db)
        await blacklist_service.add_token_to_blacklist(
            token=refresh_token,
            token_type=TokenBlacklistType.REFRESH,
            user_id=user_id,
            expires_at=expires_at,
            reason=BlacklistReason.LOGOUT  # 使用 logout 作为默认原因
        )

        return new_access_token, new_refresh_token

    async def _check_token_refresh_rate_limit(self, user_id: int) -> None:
        """
        检查 Token 刷新速率限制
        
        Args:
            user_id: 用户 ID
            
        Raises:
            TokenRateLimitError: 超出速率限制
        """
        import time
        from app.models.token_blacklist import TokenBlacklist, TokenBlacklistType
        from sqlalchemy import select, func
        from datetime import datetime, timezone, timedelta
        
        # 计算时间窗口（1 分钟前）
        window_start = datetime.now(timezone.utc) - timedelta(seconds=settings.TOKEN_REFRESH_RATE_WINDOW)
        
        # 查询用户在时间窗口内的刷新次数
        result = await self.db.execute(
            select(func.count(TokenBlacklist.id)).where(
                TokenBlacklist.user_id == user_id,
                TokenBlacklist.token_type == TokenBlacklistType.REFRESH,
                TokenBlacklist.blacklisted_at >= window_start
            )
        )
        count = result.scalar()
        
        # 检查是否超出限制
        if count >= settings.TOKEN_REFRESH_RATE_LIMIT:
            raise TokenRateLimitError()

    async def logout(
        self,
        refresh_token: str,
        client_ip: Optional[str] = None
    ) -> bool:
        """
        用户登出（将 Token 加入黑名单）
        
        Args:
            refresh_token: 刷新 Token
            client_ip: 客户端 IP
            
        Returns:
            bool: 登出成功返回 True
            
        Raises:
            TokenInvalidError: Token 无效
        """
        import hashlib
        from datetime import datetime, timezone
        from jose import JWTError
        from jose.exceptions import JWTClaimsError
        
        try:
            # 验证 Refresh Token
            payload = token_service.verify_token(refresh_token, token_type="refresh")
            user_id = int(payload["sub"])
            username = payload["username"]

        except JWTError:
            # 即使 Token 无效也返回成功（防止信息泄露）
            return True
        except JWTClaimsError:
            return True
        except (KeyError, ValueError):
            return True

        # 查询用户
        user = await self._get_user_by_id(user_id)
        
        # 将 Refresh Token 加入黑名单
        from app.models.token_blacklist import TokenBlacklist, TokenBlacklistType, BlacklistReason
        from app.services.token_blacklist_service import TokenBlacklistService
        
        # 解码 Token 获取过期时间
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        blacklist_service = TokenBlacklistService(self.db)
        await blacklist_service.add_token_to_blacklist(
            token=refresh_token,
            token_type=TokenBlacklistType.REFRESH,
            user_id=user_id,
            expires_at=expires_at,
            reason=BlacklistReason.LOGOUT
        )

        # TODO: 添加审计日志记录
        # await log_audit_event(user_id=user_id, action='logout', details={'ip': client_ip})

        return True

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 查询用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _record_failed_login(self, user: User, client_ip: Optional[str]) -> None:
        """记录登录失败"""
        user.failed_login_attempts += 1

        # 检查是否达到锁定阈值
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.status = UserStatus.LOCKED
        user.locked_until = datetime.now() + \
            timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)

        user.last_login_ip = client_ip
        user.updated_at = datetime.now()

        await self.db.commit()

    async def _record_successful_login(self, user: User, client_ip: Optional[str]) -> None:
        """记录登录成功"""
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now()
        user.last_login_ip = client_ip
        user.updated_at = datetime.now()

        await self.db.commit()

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
        刷新 Token
        
        Args:
            refresh_token: 刷新 Token
            client_ip: 客户端 IP
            
        Returns:
            Tuple[str, str]: (new_access_token, new_refresh_token)
            
        Raises:
            TokenInvalidError: Token 无效
            TokenExpiredError: Token 过期
            UserInactiveError: 用户未激活
        """
        try:
            # 验证 Refresh Token
            payload = token_service.verify_token(refresh_token, token_type="refresh")
            user_id = int(payload["sub"])
            username = payload["username"]

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

        return new_access_token, new_refresh_token

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

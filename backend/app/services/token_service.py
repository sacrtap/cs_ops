"""
Token 服务 - JWT Token 生成和验证
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Literal
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from app.config.settings import settings
from app.models.user import UserRole


class TokenService:
    """JWT Token 服务"""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(
        self,
        user_id: int,
        username: str,
        role: UserRole,
        additional_claims: Optional[dict] = None
    ) -> str:
        """
        创建 Access Token
        
        Args:
            user_id: 用户 ID
            username: 用户名
            role: 用户角色
            additional_claims: 额外的 JWT claims
            
        Returns:
            str: JWT Access Token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        claims = {
            "sub": str(user_id),  # Subject (用户 ID)
            "username": username,
            "role": role.value,
            "exp": expire,
            "iat": now,
            "type": "access",
        }

        if additional_claims:
            claims.update(additional_claims)

        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        user_id: int,
        username: str,
        additional_claims: Optional[dict] = None
    ) -> str:
        """
        创建 Refresh Token
        
        Args:
            user_id: 用户 ID
            username: 用户名
            additional_claims: 额外的 JWT claims
            
        Returns:
            str: JWT Refresh Token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)

        claims = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }

        if additional_claims:
            claims.update(additional_claims)

        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> dict:
        """
        验证 Token
        
        Args:
            token: JWT Token
            token_type: Token 类型（access 或 refresh）
            
        Returns:
            dict: Token claims
            
        Raises:
            JWTError: Token 无效或过期
            JWTClaimsError: Token claims 错误
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )

            # 验证 Token 类型
            if payload.get("type") != token_type:
                raise JWTClaimsError(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")

            return payload

        except jwt.ExpiredSignatureError:
            raise JWTError("Token has expired")
        except jwt.JWTClaimsError as e:
            raise JWTClaimsError(str(e))
        except Exception as e:
            raise JWTError(f"Invalid token: {str(e)}")

    def get_token_expire_seconds(self) -> int:
        """获取 Access Token 过期时间（秒）"""
        return self.access_token_expire_minutes * 60


# 全局 Token 服务实例
token_service = TokenService()

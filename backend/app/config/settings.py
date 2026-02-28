"""
应用配置管理
"""
import os
from typing import Optional
from datetime import timedelta


class Settings:
    """应用配置"""

    # 应用配置
    APP_NAME: str = "cs_ops"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops"
    )

    # JWT 配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))  # 2 小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7 天

    @property
    def JWT_ACCESS_TOKEN_EXPIRES(self) -> timedelta:
        return timedelta(minutes=self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def JWT_REFRESH_TOKEN_EXPIRES(self) -> timedelta:
        return timedelta(days=self.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # 安全配置
    BCRYPT_ROUNDS: int = 10
    MAX_LOGIN_ATTEMPTS: int = 5  # 最大登录失败次数
    LOCKOUT_DURATION_MINUTES: int = 15  # 锁定时长（分钟）

    # CORS 配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        case_sensitive = True


# 全局配置实例
settings = Settings()

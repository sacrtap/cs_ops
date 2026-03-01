"""
认证相关的 Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, UserStatus


# ==================== 请求 Schemas ====================


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(..., description="刷新 Token")


# ==================== 响应 Schemas ====================


class UserResponse(BaseModel):
    """用户信息响应（不包含敏感数据）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    role: str  # UserRole 枚举值 (admin/manager/specialist/sales)
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str  # UserStatus 枚举值 (active/inactive/locked)
    created_at: datetime


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str = Field(..., description="访问 Token")
    refresh_token: str = Field(..., description="刷新 Token")
    token_type: str = Field(default="bearer", description="Token 类型")
    expires_in: int = Field(..., description="Access Token 过期时间（秒）")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    """刷新 Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ==================== 错误 Schemas ====================


class LoginError(BaseModel):
    """登录错误详情"""
    field: str
    message: str


class LoginErrorResponse(BaseModel):
    """登录错误响应"""
    error: str
    message: str
    details: Optional[list[LoginError]] = None

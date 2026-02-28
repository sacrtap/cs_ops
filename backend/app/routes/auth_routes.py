"""
认证 API 路由
"""
from datetime import datetime, timezone
from sanic import Blueprint, json
from sanic.request import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    LoginResponse,
    RefreshTokenResponse,
)
from app.services.auth_service import AuthService, AuthenticationError, TokenUsedError, TokenRateLimitError
from app.services.token_service import token_service
from app.models.token_blacklist import TokenBlacklistType, BlacklistReason

# 创建认证 Blueprint
auth_bp = Blueprint("auth", url_prefix="/api/v1/auth")


@auth_bp.post("/login")
async def login(request: Request):
    """
    用户登录
    
    请求体:
        username: 用户名
        password: 密码
        
    响应:
        access_token: 访问 Token
        refresh_token: 刷新 Token
        token_type: Token 类型 (bearer)
        expires_in: Access Token 过期时间（秒）
        user: 用户信息
    """
    try:
        # 验证请求数据
        data = LoginRequest(**request.json)

        # 获取数据库会话
        db: AsyncSession = request.ctx.db

        # 创建认证服务
        auth_service = AuthService(db)

        # 获取客户端 IP
        client_ip = request.remote_addr

        # 认证并生成 Token
        user, access_token, refresh_token = await auth_service.authenticate(
            username=data.username,
            password=data.password,
            client_ip=client_ip
        )

        # 返回响应
        response_data = LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=token_service.get_token_expire_seconds(),
            user=user.to_dict()
        )

        return json(
            {"data": response_data.model_dump()},
            status=200
        )

    except AuthenticationError as e:
        return json(
            {
                "error": {
                    "code": e.code,
                    "message": e.message,
                }
            },
            status=e.status_code
        )

    except ValueError as e:
        return json(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求参数验证失败",
                    "details": [{"field": "request_body", "message": str(e)}]
                }
            },
            status=400
        )

    except Exception as e:
        # 生产环境应记录详细日志
        return json(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                }
            },
            status=500
        )


@auth_bp.post("/refresh")
async def refresh_token(request: Request):
    """
    刷新 Token
    
    请求体:
        refresh_token: 刷新 Token
        
    响应:
        access_token: 新的访问 Token
        refresh_token: 新的刷新 Token
        token_type: Token 类型 (bearer)
        expires_in: Access Token 过期时间（秒）
    """
    try:
        # 验证请求数据
        data = RefreshTokenRequest(**request.json)

        # 获取数据库会话
        db: AsyncSession = request.ctx.db

        # 创建认证服务
        auth_service = AuthService(db)

        # 刷新 Token
        access_token, refresh_token = await auth_service.refresh_tokens(
            refresh_token=data.refresh_token,
            client_ip=request.remote_addr
        )

        # 返回响应
        response_data = RefreshTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=token_service.get_token_expire_seconds()
        )

        return json(
            {"data": response_data.model_dump()},
            status=200
        )

    except AuthenticationError as e:
        return json(
            {
                "error": {
                    "code": e.code,
                    "message": e.message,
                }
            },
            status=e.status_code
        )

    except ValueError as e:
        return json(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求参数验证失败",
                    "details": [{"field": "request_body", "message": str(e)}]
                }
            },
            status=400
        )

    except Exception as e:
        return json(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                }
            },
            status=500
        )


@auth_bp.post("/logout")
async def logout(request: Request):
    """
    用户登出（将 Token 加入黑名单）
    
    请求体:
        refresh_token: 刷新 Token
        
    响应:
        message: 登出成功消息
    """
    try:
        # 验证请求数据
        data = RefreshTokenRequest(**request.json)

        # 获取数据库会话
        db: AsyncSession = request.ctx.db

        # 创建认证服务
        auth_service = AuthService(db)

        # 登出（将 Token 加入黑名单）
        success = await auth_service.logout(
            refresh_token=data.refresh_token,
            client_ip=request.remote_addr
        )

        # 返回响应（无论 Token 是否有效都返回成功，防止信息泄露）
        return json(
            {
                "data": {
                    "message": "已成功登出"
                }
            },
            status=200
        )

    except ValueError as e:
        return json(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求参数验证失败",
                    "details": [{"field": "request_body", "message": str(e)}]
                }
            },
            status=400
        )

    except Exception as e:
        # 记录异常但不返回给客户端（防止信息泄露）
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"登出 API 异常：{e}, user_ip: {request.remote_addr}")
        
        return json(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                }
            },
            status=500
        )

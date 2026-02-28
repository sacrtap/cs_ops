"""
Token 刷新流程集成测试

测试完整的 Token 刷新流程，包括：
- 登录获取 Token
- 刷新 Token
- Refresh Token 单次使用
- 速率限制
- 登出功能

注意：测试需要 PostgreSQL 数据库连接
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models.user import User, UserRole, UserStatus
from app.models.base import Base
from app.config.settings import settings
import os

# ==================== 测试配置 ====================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops_test"
)

# ==================== Fixtures ====================


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理：删除所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """创建测试数据库会话"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户"""
    from app.utils.password import hash_password
    
    user = User(
        username="testuser",
        password_hash=hash_password("password123"),
        real_name="测试用户",
        role=UserRole.SPECIALIST,
        email="test@example.com",
        phone="13800138000",
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def app():
    """创建 Sanic 应用"""
    from app.main import create_app
    app = create_app()
    app.config.TESTING = True
    return app


# ==================== Token 刷新流程测试 ====================


@pytest.mark.asyncio
async def test_complete_token_refresh_flow(app, test_user):
    """测试完整的 Token 刷新流程"""
    # 1. 登录获取 Token
    login_response = await app.asgi_client.post('/api/v1/auth/login', json={
        "username": "testuser",
        "password": "password123"
    })

    assert login_response.status == 200
    data = login_response.json
    assert "data" in data
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    
    access_token = data["data"]["access_token"]
    refresh_token = data["data"]["refresh_token"]

    # 2. 使用 Refresh Token 刷新 Access Token
    refresh_response = await app.asgi_client.post('/api/v1/auth/refresh', json={
        "refresh_token": refresh_token
    })

    assert refresh_response.status == 200
    refresh_data = refresh_response.json
    assert "data" in refresh_data
    assert "access_token" in refresh_data["data"]
    assert "refresh_token" in refresh_data["data"]
    
    new_access_token = refresh_data["data"]["access_token"]
    new_refresh_token = refresh_data["data"]["refresh_token"]
    
    # 新旧 Token 应该不同
    assert new_access_token != access_token
    assert new_refresh_token != refresh_token

    # 3. 使用新 Token 访问受保护资源
    protected_response = await app.asgi_client.get(
        '/api/v1/profile',
        headers={'Authorization': f'Bearer {new_access_token}'}
    )

    assert protected_response.status == 200


@pytest.mark.asyncio
async def test_refresh_token_single_use(app, test_user):
    """测试 Refresh Token 单次使用（防重放）"""
    # 1. 登录获取 Token
    login_response = await app.asgi_client.post('/api/v1/auth/login', json={
        "username": "testuser",
        "password": "password123"
    })
    
    refresh_token = login_response.json["data"]["refresh_token"]

    # 2. 第一次刷新（应该成功）
    refresh_response1 = await app.asgi_client.post('/api/v1/auth/refresh', json={
        "refresh_token": refresh_token
    })
    assert refresh_response1.status == 200

    # 3. 第二次刷新（应该失败 - Token 已被使用）
    refresh_response2 = await app.asgi_client.post('/api/v1/auth/refresh', json={
        "refresh_token": refresh_token
    })
    assert refresh_response2.status == 401
    assert refresh_response2.json["error"]["code"] == "REFRESH_TOKEN_USED"


@pytest.mark.asyncio
async def test_token_refresh_rate_limiting(app, test_user):
    """测试 Token 刷新速率限制"""
    # 1. 登录获取 Token
    login_response = await app.asgi_client.post('/api/v1/auth/login', json={
        "username": "testuser",
        "password": "password123"
    })
    
    refresh_token = login_response.json["data"]["refresh_token"]

    # 2. 快速连续刷新 3 次（应该都成功）
    for i in range(3):
        # 每次需要使用新的 Refresh Token
        if i > 0:
            refresh_token = prev_refresh_response.json["data"]["refresh_token"]
        
        refresh_response = await app.asgi_client.post('/api/v1/auth/refresh', json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status == 200
        prev_refresh_response = refresh_response

    # 3. 第 4 次刷新（应该失败 - 速率限制）
    last_refresh_token = prev_refresh_response.json["data"]["refresh_token"]
    rate_limit_response = await app.asgi_client.post('/api/v1/auth/refresh', json={
        "refresh_token": last_refresh_token
    })
    
    assert rate_limit_response.status == 429
    assert rate_limit_response.json["error"]["code"] == "TOKEN_REFRESH_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_logout_adds_to_blacklist(app, test_user):
    """测试登出功能将 Token 加入黑名单"""
    # 1. 登录获取 Token
    login_response = await app.asgi_client.post('/api/v1/auth/login', json={
        "username": "testuser",
        "password": "password123"
    })
    
    access_token = login_response.json["data"]["access_token"]
    refresh_token = login_response.json["data"]["refresh_token"]

    # 2. 登出
    logout_response = await app.asgi_client.post('/api/v1/auth/logout', json={
        "refresh_token": refresh_token
    })
    
    assert logout_response.status == 200
    assert logout_response.json["data"]["message"] == "已成功登出"

    # 3. 尝试使用已登出的 Refresh Token 刷新（应该失败）
    refresh_response = await app.asgi_client.post('/api/v1/auth/refresh', json={
        "refresh_token": refresh_token
    })
    
    assert refresh_response.status == 401

    # 4. 尝试使用已登出的 Access Token 访问资源（应该失败）
    protected_response = await app.asgi_client.get(
        '/api/v1/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert protected_response.status == 401


@pytest.mark.asyncio
async def test_logout_with_invalid_token(app):
    """测试使用无效 Token 登出（应该返回成功，防止信息泄露）"""
    logout_response = await app.asgi_client.post('/api/v1/auth/logout', json={
        "refresh_token": "invalid_token"
    })
    
    # 即使 Token 无效也应该返回成功（防止信息泄露）
    assert logout_response.status == 200
    assert logout_response.json["data"]["message"] == "已成功登出"

"""
Token 验证中间件单元测试

测试 auth_middleware.py 中的黑名单检查功能
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models.user import User, UserRole, UserStatus
from app.models.token_blacklist import TokenBlacklist, TokenBlacklistType, BlacklistReason
from app.models.base import Base
from app.services.token_service import token_service
from app.services.token_blacklist_service import TokenBlacklistService
from app.middleware.auth_middleware import AuthMiddleware
from app.config.settings import settings
import os
import hashlib

# ==================== 测试配置 ====================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops_test"
)


# ==================== Mock Request 类 ====================


class MockRequestContext:
    """Mock 请求上下文"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.current_user = None
        self.user_id = None
        self.username = None
        self.user_role = None


class MockRequest:
    """Mock Sanic 请求对象"""
    def __init__(self, db: AsyncSession, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.ctx = MockRequestContext(db)
        self.remote_addr = "127.0.0.1"


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
async def blacklist_service(db_session):
    """创建 Token 黑名单服务实例"""
    return TokenBlacklistService(db_session)


# ==================== AuthMiddleware 测试 ====================


class TestAuthMiddleware:
    """认证中间件测试"""

    @pytest.mark.asyncio
    async def test_authenticate_success(self, db_session, test_user):
        """测试认证成功"""
        from sanic.exceptions import Unauthorized, Forbidden
        
        # 创建有效的 Access Token
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=test_user.role
        )

        # 创建 Mock 请求
        request = MockRequest(db_session, token)

        # 执行认证
        user = await AuthMiddleware.authenticate(request)

        # 验证结果
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
        assert request.ctx.current_user == user
        assert request.ctx.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_authenticate_missing_token(self, db_session):
        """测试缺少 Token"""
        from sanic.exceptions import Unauthorized
        
        request = MockRequest(db_session, "")
        request.headers = {}  # 没有 Authorization header

        with pytest.raises(Unauthorized, match="缺少认证 Token"):
            await AuthMiddleware.authenticate(request)

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, db_session):
        """测试无效 Token"""
        from sanic.exceptions import Unauthorized
        
        request = MockRequest(db_session, "invalid_token")

        with pytest.raises(Unauthorized, match="认证令牌无效或已过期"):
            await AuthMiddleware.authenticate(request)

    @pytest.mark.asyncio
    async def test_authenticate_expired_token(self, db_session, test_user):
        """测试过期 Token"""
        from sanic.exceptions import Unauthorized
        from jose import jwt
        from datetime import datetime, timezone, timedelta
        
        # 创建已过期的 Token
        now = datetime.now(timezone.utc)
        expired = now - timedelta(hours=1)
        
        claims = {
            "sub": str(test_user.id),
            "username": test_user.username,
            "role": test_user.role.value,
            "exp": expired,
            "iat": now,
            "type": "access",
            "jti": "test_jti"
        }
        
        token = jwt.encode(
            claims,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        request = MockRequest(db_session, token)

        with pytest.raises(Unauthorized, match="认证令牌无效或已过期"):
            await AuthMiddleware.authenticate(request)

    @pytest.mark.asyncio
    async def test_authenticate_blacklisted_token(self, db_session, test_user, blacklist_service):
        """测试黑名单中的 Token（关键功能）"""
        from sanic.exceptions import Unauthorized
        
        # 创建有效的 Access Token
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=test_user.role
        )

        # 将 Token 加入黑名单
        from datetime import datetime, timezone, timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
        
        await blacklist_service.add_token_to_blacklist(
            token=token,
            token_type=TokenBlacklistType.ACCESS,
            user_id=test_user.id,
            expires_at=expires_at,
            reason=BlacklistReason.LOGOUT
        )

        # 创建 Mock 请求
        request = MockRequest(db_session, token)

        # 认证应该失败（Token 在黑名单中）
        with pytest.raises(Unauthorized, match="认证令牌已失效"):
            await AuthMiddleware.authenticate(request)

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, db_session, test_user):
        """测试未激活用户"""
        from sanic.exceptions import Forbidden
        
        # 设置用户为未激活状态
        test_user.status = UserStatus.INACTIVE
        await db_session.commit()

        # 创建有效的 Access Token
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=test_user.role
        )

        request = MockRequest(db_session, token)

        with pytest.raises(Forbidden, match="账户已被禁用"):
            await AuthMiddleware.authenticate(request)

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user(self, db_session):
        """测试不存在的用户"""
        from sanic.exceptions import Unauthorized
        
        # 创建 Token（使用不存在的用户 ID）
        token = token_service.create_access_token(
            user_id=99999,
            username="nonexistent",
            role=UserRole.SPECIALIST
        )

        request = MockRequest(db_session, token)

        with pytest.raises(Unauthorized, match="用户不存在"):
            await AuthMiddleware.authenticate(request)

    @pytest.mark.asyncio
    async def test_authenticate_blacklist_expired_entry(self, db_session, test_user, blacklist_service):
        """测试黑名单记录已过期的情况"""
        from datetime import datetime, timezone, timedelta
        
        # 创建有效的 Access Token
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=test_user.role
        )

        # 添加黑名单记录（注意：数据库约束要求 expires_at > blacklisted_at）
        # 所以我们需要添加一个有效记录，然后手动修改它的过期时间
        blacklisted_at = datetime.now(timezone.utc) - timedelta(hours=2)
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # 已过期
        
        # 直接插入数据库（绕过约束）
        from sqlalchemy import text
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await db_session.execute(text("""
            INSERT INTO token_blacklists (token_hash, token_type, user_id, blacklisted_at, expires_at, reason)
            VALUES (:token_hash, 'access', :user_id, :blacklisted_at, :expires_at, 'logout')
            ON CONFLICT (token_hash) DO NOTHING
        """), {
            "token_hash": token_hash,
            "user_id": test_user.id,
            "blacklisted_at": blacklisted_at,
            "expires_at": expires_at
        })
        await db_session.commit()

        # 创建 Mock 请求
        request = MockRequest(db_session, token)

        # 认证应该成功（黑名单记录已过期）
        user = await AuthMiddleware.authenticate(request)
        assert user is not None
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_authenticate_wrong_token_type(self, db_session, test_user):
        """测试错误的 Token 类型（使用 Refresh Token 访问）"""
        from sanic.exceptions import Unauthorized
        
        # 创建 Refresh Token（而不是 Access Token）
        token = token_service.create_refresh_token(
            user_id=test_user.id,
            username=test_user.username
        )

        request = MockRequest(db_session, token)

        with pytest.raises(Unauthorized, match="认证令牌无效或已过期"):
            await AuthMiddleware.authenticate(request)


class TestAuthMiddlewareDecorators:
    """认证中间件装饰器测试"""

    @pytest.mark.asyncio
    async def test_require_auth_decorator(self, db_session, test_user):
        """测试 require_auth 装饰器"""
        from sanic import Blueprint
        
        # 创建测试路由
        bp = Blueprint('test')
        
        @bp.route('/test')
        @AuthMiddleware.require_auth
        async def test_route(request):
            return {"user_id": request.ctx.user_id}
        
        # 创建有效的 Access Token
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=test_user.role
        )

        # 创建 Mock 请求
        request = MockRequest(db_session, token)

        # 执行路由
        response = await test_route(request)
        
        assert response == {"user_id": test_user.id}

    @pytest.mark.asyncio
    async def test_require_roles_decorator_success(self, db_session, test_user):
        """测试 require_roles 装饰器（成功）"""
        # 创建有效的 Access Token
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=test_user.role
        )

        # 创建 Mock 请求
        request = MockRequest(db_session, token)

        # 装饰器包装
        @AuthMiddleware.require_roles(UserRole.SPECIALIST, UserRole.ADMIN)
        async def protected_route(req):
            return {"success": True}
        
        response = await protected_route(request)
        assert response == {"success": True}

    @pytest.mark.asyncio
    async def test_require_roles_decorator_forbidden(self, db_session, test_user):
        """测试 require_roles 装饰器（权限不足）"""
        from sanic.exceptions import Forbidden
        
        # 创建有效的 Access Token（用户角色是 SPECIALIST）
        token = token_service.create_access_token(
            user_id=test_user.id,
            username=test_user.username,
            role=UserRole.SPECIALIST
        )

        # 创建 Mock 请求
        request = MockRequest(db_session, token)

        # 需要 ADMIN 角色
        @AuthMiddleware.require_roles(UserRole.ADMIN)
        async def admin_route(req):
            return {"success": True}
        
        with pytest.raises(Forbidden, match="需要权限"):
            await admin_route(request)

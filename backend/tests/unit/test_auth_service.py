"""
认证服务单元测试

注意：测试需要 PostgreSQL 数据库连接
设置测试数据库：
1. 创建测试数据库：CREATE DATABASE cs_ops_test;
2. 设置环境变量：DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops_test
3. 运行测试：pytest tests/unit/test_auth_service.py
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, text
from app.models.user import User, UserRole, UserStatus
from app.models.base import Base
from app.services.auth_service import AuthService, InvalidCredentialsError, UserLockedError, UserInactiveError
from app.utils.password import hash_password, verify_password
from app.config.settings import settings
import os

# ==================== 测试配置 ====================

# 使用环境变量中的数据库 URL，如果没有则使用测试数据库
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
async def auth_service(db_session):
    """创建认证服务实例"""
    return AuthService(db_session)


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户"""
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


# ==================== 密码测试 ====================


class TestPassword:
    """密码服务测试"""

    def test_hash_password(self):
        """测试密码加密"""
        password = "password123"
        hashed = hash_password(password)

        # 验证哈希不为空且不同
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_different_salts(self):
        """测试每次加密生成不同的哈希"""
        password = "password123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # 两次哈希应该不同（因为 salt 不同）
        assert hash1 != hash2

    def test_verify_password_success(self):
        """测试密码验证成功"""
        password = "password123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """测试密码验证失败"""
        password = "password123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


# ==================== 认证服务测试 ====================


class TestAuthService:
    """认证服务测试"""

    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service, test_user):
        """测试认证成功"""
        user, access_token, refresh_token = await auth_service.authenticate(
            username="testuser",
            password="password123"
        )

        assert user.id == test_user.id
        assert user.username == test_user.username
        assert access_token is not None
        assert refresh_token is not None
        assert len(access_token) > 0
        assert len(refresh_token) > 0

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, auth_service, test_user):
        """测试认证 - 密码错误"""
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate(
                username="testuser",
                password="wrongpassword"
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service):
        """测试认证 - 用户不存在"""
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate(
                username="nonexistent",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, db_session, auth_service):
        """测试认证 - 用户未激活"""
        # 创建未激活用户
        user = User(
            username="inactive_user",
            password_hash=hash_password("password123"),
            real_name="未激活用户",
            role=UserRole.SPECIALIST,
            status=UserStatus.INACTIVE,
        )
        db_session.add(user)
        await db_session.commit()

        with pytest.raises(UserInactiveError):
            await auth_service.authenticate(
                username="inactive_user",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, auth_service, test_user):
        """测试刷新 Token 成功"""
        # 先登录获取 Token
        _, _, refresh_token = await auth_service.authenticate(
            username="testuser",
            password="password123"
        )

        # 刷新 Token
        new_access_token, new_refresh_token = await auth_service.refresh_tokens(
            refresh_token=refresh_token
        )

        assert new_access_token is not None
        assert new_refresh_token is not None
        assert new_access_token != refresh_token  # 新 Token 应该不同

    @pytest.mark.asyncio
    async def test_refresh_tokens_invalid_token(self, auth_service):
        """测试刷新 Token - Token 无效"""
        from app.services.auth_service import TokenInvalidError

        with pytest.raises(TokenInvalidError):
            await auth_service.refresh_tokens(
                refresh_token="invalid_token"
            )

    @pytest.mark.asyncio
    async def test_login_updates_last_login(self, auth_service, test_user, db_session):
        """测试登录更新最后登录时间"""
        await auth_service.authenticate(
            username="testuser",
            password="password123"
        )

        # 查询更新后的用户
        from sqlalchemy import select
        result = await db_session.execute(
            select(User).where(User.id == test_user.id)
        )
        updated_user = result.scalar_one_or_none()

        assert updated_user is not None
        assert updated_user.last_login_at is not None
        assert updated_user.failed_login_attempts == 0


# ==================== 登录失败限制测试 ====================


class TestLoginFailureLimit:
    """登录失败限制测试"""

    @pytest.mark.asyncio
    async def test_account_locked_after_max_attempts(self, db_session, auth_service):
        """测试账户在最大失败次数后被锁定"""
        # 创建用户
        user = User(
            username="lock_test_user",
            password_hash=hash_password("password123"),
            real_name="锁定测试用户",
            role=UserRole.SPECIALIST,
            status=UserStatus.ACTIVE,
            failed_login_attempts=0,
        )
        db_session.add(user)
        await db_session.commit()

        # 尝试登录失败 5 次
        for i in range(settings.MAX_LOGIN_ATTEMPTS):
            try:
                await auth_service.authenticate(
                    username="lock_test_user",
                    password="wrongpassword"
                )
            except InvalidCredentialsError:
                pass

        # 查询用户状态
        from sqlalchemy import select
        result = await db_session.execute(
            select(User).where(User.username == "lock_test_user")
        )
        locked_user = result.scalar_one_or_none()

        assert locked_user is not None
        assert locked_user.status == UserStatus.LOCKED
        assert locked_user.failed_login_attempts == settings.MAX_LOGIN_ATTEMPTS
        assert locked_user.locked_until is not None

        # 尝试登录应该失败（用户被锁定）
        with pytest.raises(UserLockedError):
            await auth_service.authenticate(
                username="lock_test_user",
                password="password123"
            )

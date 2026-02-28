"""
Token 服务单元测试

注意：测试需要 PostgreSQL 数据库连接
设置测试数据库：
1. 创建测试数据库：CREATE DATABASE cs_ops_test;
2. 设置环境变量：DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops_test
3. 运行测试：pytest tests/unit/test_token_service.py
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, text
from app.models.user import User, UserRole, UserStatus
from app.models.token_blacklist import TokenBlacklist, TokenBlacklistType, BlacklistReason
from app.models.base import Base
from app.services.token_service import token_service
from app.services.token_blacklist_service import TokenBlacklistService
from app.config.settings import settings
import os
import hashlib

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
async def blacklist_service(db_session):
    """创建 Token 黑名单服务实例"""
    return TokenBlacklistService(db_session)


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


# ==================== Token 服务测试 ====================


class TestTokenService:
    """Token 服务测试"""

    def test_create_access_token(self):
        """测试创建 Access Token"""
        token = token_service.create_access_token(
            user_id=1,
            username="zhangsan",
            role=UserRole.SALES
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """测试创建 Refresh Token"""
        token = token_service.create_refresh_token(
            user_id=1,
            username="zhangsan"
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_has_jti_claim(self):
        """测试 Access Token 包含 jti claim（防重放）"""
        token = token_service.create_access_token(
            user_id=1,
            username="zhangsan",
            role=UserRole.SALES
        )

        # 验证 Token 内容
        payload = token_service.verify_token(token, token_type="access")
        assert payload is not None
        assert "jti" in payload
        assert len(payload["jti"]) > 0  # UUID 格式

    def test_refresh_token_has_jti_claim(self):
        """测试 Refresh Token 包含 jti claim（防重放）"""
        token = token_service.create_refresh_token(
            user_id=1,
            username="zhangsan"
        )

        payload = token_service.verify_token(token, token_type="refresh")
        assert payload is not None
        assert "jti" in payload
        assert len(payload["jti"]) > 0

    def test_verify_access_token_success(self):
        """测试验证 Access Token 成功"""
        token = token_service.create_access_token(
            user_id=1,
            username="zhangsan",
            role=UserRole.SALES
        )

        payload = token_service.verify_token(token, token_type="access")
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "zhangsan"
        assert payload["role"] == "sales"
        assert payload["type"] == "access"

    def test_verify_refresh_token_success(self):
        """测试验证 Refresh Token 成功"""
        token = token_service.create_refresh_token(
            user_id=1,
            username="zhangsan"
        )

        payload = token_service.verify_token(token, token_type="refresh")
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "zhangsan"
        assert payload["type"] == "refresh"

    def test_verify_wrong_token_type(self):
        """测试验证错误的 Token 类型"""
        from jose import JWTError, JWTClaimsError

        access_token = token_service.create_access_token(
            user_id=1,
            username="zhangsan",
            role=UserRole.SALES
        )

        # 尝试用 refresh 类型验证 access token
        with pytest.raises(JWTClaimsError):
            token_service.verify_token(access_token, token_type="refresh")

    def test_get_token_expire_seconds(self):
        """测试获取 Token 过期时间"""
        expire_seconds = token_service.get_token_expire_seconds()
        assert expire_seconds == settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60


# ==================== Token 黑名单服务测试 ====================


class TestTokenBlacklistService:
    """Token 黑名单服务测试"""

    @pytest.mark.asyncio
    async def test_hash_token(self, blacklist_service):
        """测试 Token 哈希计算"""
        token = "test_token_123"
        token_hash = blacklist_service.hash_token(token)

        assert token_hash is not None
        assert len(token_hash) == 64  # SHA256 输出 64 字符十六进制

    @pytest.mark.asyncio
    async def test_hash_token_consistent(self, blacklist_service):
        """测试 Token 哈希一致性"""
        token = "test_token_123"
        hash1 = blacklist_service.hash_token(token)
        hash2 = blacklist_service.hash_token(token)

        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_add_to_blacklist(self, blacklist_service, test_user):
        """测试添加 Token 到黑名单"""
        from datetime import datetime, timezone, timedelta
        
        token_hash = "test_hash_123"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)

        blacklist_entry = await blacklist_service.add_to_blacklist(
            token_hash=token_hash,
            token_type=TokenBlacklistType.ACCESS,
            user_id=test_user.id,
            expires_at=expires_at,
            reason=BlacklistReason.LOGOUT
        )

        assert blacklist_entry is not None
        assert blacklist_entry.token_hash == token_hash
        assert blacklist_entry.token_type == TokenBlacklistType.ACCESS
        assert blacklist_entry.user_id == test_user.id
        assert blacklist_entry.reason == BlacklistReason.LOGOUT

    @pytest.mark.asyncio
    async def test_is_blacklisted_true(self, blacklist_service, test_user):
        """测试检查 Token 在黑名单中"""
        from datetime import datetime, timezone, timedelta
        
        token_hash = "blacklisted_hash"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)

        # 添加到黑名单
        await blacklist_service.add_to_blacklist(
            token_hash=token_hash,
            token_type=TokenBlacklistType.ACCESS,
            user_id=test_user.id,
            expires_at=expires_at
        )

        # 检查是否在黑名单中
        is_blacklisted = await blacklist_service.is_blacklisted(token_hash)
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_is_blacklisted_false(self, blacklist_service):
        """测试检查 Token 不在黑名单中"""
        token_hash = "not_blacklisted_hash"
        is_blacklisted = await blacklist_service.is_blacklisted(token_hash)
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_expired(self, blacklist_service, test_user):
        """测试检查已过期的黑名单记录"""
        from datetime import datetime, timezone, timedelta
        
        token_hash = "expired_hash"
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # 已过期

        # 添加已过期的黑名单记录
        await blacklist_service.add_to_blacklist(
            token_hash=token_hash,
            token_type=TokenBlacklistType.ACCESS,
            user_id=test_user.id,
            expires_at=expires_at
        )

        # 已过期的记录不应被视为在黑名单中
        is_blacklisted = await blacklist_service.is_blacklisted(token_hash)
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist(self, blacklist_service, test_user):
        """测试添加 Token 到黑名单（便捷方法）"""
        from datetime import datetime, timezone, timedelta
        
        token = "test_jwt_token"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        blacklist_entry = await blacklist_service.add_token_to_blacklist(
            token=token,
            token_type=TokenBlacklistType.REFRESH,
            user_id=test_user.id,
            expires_at=expires_at,
            reason=BlacklistReason.LOGOUT
        )

        assert blacklist_entry.token_hash == token_hash
        assert blacklist_entry.token_type == TokenBlacklistType.REFRESH

    @pytest.mark.asyncio
    async def test_get_user_blacklist_count(self, blacklist_service, test_user):
        """测试获取用户黑名单记录数"""
        from datetime import datetime, timezone, timedelta
        
        # 添加 3 条黑名单记录
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
        
        for i in range(3):
            await blacklist_service.add_to_blacklist(
                token_hash=f"hash_{i}",
                token_type=TokenBlacklistType.ACCESS,
                user_id=test_user.id,
                expires_at=expires_at
            )

        count = await blacklist_service.get_user_blacklist_count(test_user.id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, blacklist_service, test_user):
        """测试清理过期黑名单记录"""
        from datetime import datetime, timezone, timedelta
        
        # 添加 1 条有效记录和 1 条过期记录
        valid_expires = datetime.now(timezone.utc) + timedelta(hours=2)
        expired_expires = datetime.now(timezone.utc) - timedelta(hours=1)

        await blacklist_service.add_to_blacklist(
            token_hash="valid_hash",
            token_type=TokenBlacklistType.ACCESS,
            user_id=test_user.id,
            expires_at=valid_expires
        )

        await blacklist_service.add_to_blacklist(
            token_hash="expired_hash",
            token_type=TokenBlacklistType.ACCESS,
            user_id=test_user.id,
            expires_at=expired_expires
        )

        # 清理过期记录
        deleted_count = await blacklist_service.cleanup_expired()
        assert deleted_count == 1

        # 验证有效记录仍在
        count = await blacklist_service.get_user_blacklist_count(test_user.id)
        assert count == 1

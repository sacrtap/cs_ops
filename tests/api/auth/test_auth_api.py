"""
用户认证 API 测试 - ATDD (TDD Red Phase)

Story: 1-1-user-authentication
Epic: 1 - 权限与认证
Generated: 2026-02-27
TDD Phase: RED (tests will fail until feature implemented)

验收标准覆盖:
1. 用户能够使用用户名和密码登录系统
2. 系统验证用户名和密码的正确性
3. 验证成功后生成 JWT Access Token 和 Refresh Token
4. Token 返回给前端并存储
5. 失败的登录请求返回标准错误响应
6. 密码使用 bcrypt 加密存储
7. 实现登录失败次数限制（防暴力破解）
8. 所有敏感操作记录审计日志
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.models.user import User, UserRole, UserStatus
from app.utils.password import hash_password, verify_password
from app.config.settings import settings


# ===========================================
# Test Class: 登录 API 测试
# ===========================================

class TestLoginAPI:
    """
    登录 API 测试 - POST /api/v1/auth/login
    
    覆盖验收标准: 1, 2, 3, 4, 5
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_success_returns_tokens(self, app, db_session, user_factory):
        """
        测试登录成功返回 Token
        
        Given: 已注册的有效用户
        When: 使用正确的用户名和密码发送登录请求
        Then: 返回 access_token 和 refresh_token，状态码 200
        
        覆盖 AC-1, AC-3, AC-4
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "email": "test@example.com",
            "real_name": "测试用户",
            "role": UserRole.OPERATOR,
            "status": UserStatus.ACTIVE,
        })
        
        # 在数据库中创建用户（密码已加密）
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name=user_data["real_name"],
            email=user_data["email"],
            role=user_data["role"],
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        login_payload = {
            "username": "testuser",
            "password": "Test123456!",
        }
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        # Then: 验证响应
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "data" in data
        response_data = data["data"]
        
        # 验证 Token 存在
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert "token_type" in response_data
        assert "expires_in" in response_data
        
        # 验证 Token 类型和格式
        assert response_data["token_type"] == "bearer"
        assert len(response_data["access_token"]) > 0
        assert len(response_data["refresh_token"]) > 0
        assert response_data["expires_in"] == settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        # 验证用户信息
        assert "user" in response_data
        user_info = response_data["user"]
        assert user_info["id"] == user.id
        assert user_info["username"] == user.username
        assert user_info["real_name"] == user.real_name
        assert user_info["role"] == user.role.value
        assert user_info["email"] == user.email
        
        # 验证密码不在响应中
        assert "password" not in user_info
        assert "password_hash" not in user_info
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_wrong_password_returns_401(self, app, db_session, user_factory):
        """
        测试密码错误返回 401
        
        Given: 已注册的有效用户
        When: 使用错误的密码发送登录请求
        Then: 返回 401 错误，错误码 INVALID_CREDENTIALS
        
        覆盖 AC-2, AC-5
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="测试用户",
            email="test@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        login_payload = {
            "username": "testuser",
            "password": "WrongPassword123!",  # 错误的密码
        }
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 401
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "INVALID_CREDENTIALS"
        assert "message" in data["error"]
        
        # 验证失败次数增加
        await db_session.refresh(user)
        assert user.failed_login_attempts == 1
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_user_not_found_returns_401(self, app):
        """
        测试用户不存在返回 401
        
        Given: 用户不存在于数据库
        When: 使用不存在的用户名发送登录请求
        Then: 返回 401 错误（统一错误消息，防止用户枚举）
        
        覆盖 AC-2, AC-5
        """
        login_payload = {
            "username": "nonexistent_user",
            "password": "Test123456!",
        }
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        # Then: 验证错误响应（与密码错误相同的响应）
        assert response.status_code == 401
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "INVALID_CREDENTIALS"
        
        # 错误消息应该与密码错误相同，防止用户枚举攻击
        assert data["error"]["message"] == "用户名或密码错误"
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_inactive_user_returns_403(self, app, db_session, user_factory):
        """
        测试未激活用户返回 403
        
        Given: 用户状态为 inactive
        When: 使用该用户凭证发送登录请求
        Then: 返回 403 错误，错误码 USER_INACTIVE
        
        覆盖 AC-2, AC-5
        """
        # Given: 创建未激活用户
        user_data = user_factory.create(overrides={
            "username": "inactive_user",
            "password": "Test123456!",
            "status": UserStatus.INACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="未激活用户",
            email="inactive@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        login_payload = {
            "username": "inactive_user",
            "password": "Test123456!",
        }
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 403
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "USER_INACTIVE"
        assert "已被禁用" in data["error"]["message"]
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_validation_error_returns_422(self, app):
        """
        测试请求验证错误返回 422
        
        Given: 无效的登录请求数据（用户名为空或密码太短）
        When: 发送格式错误的登录请求
        Then: 返回 422 验证错误
        
        覆盖 AC-5
        """
        # Given: 无效的请求数据
        invalid_payloads = [
            {"username": "", "password": "Test123456!"},  # 用户名为空
            {"username": "ab", "password": "Test123456!"},  # 用户名太短
            {"username": "testuser", "password": "123"},  # 密码太短
            {"username": "testuser", "password": ""},  # 密码为空
        ]
        
        # When & Then: 验证每个无效请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            for payload in invalid_payloads:
                response = await client.post("/api/v1/auth/login", json=payload)
                assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_updates_last_login_time(self, app, db_session, user_factory):
        """
        测试登录成功更新最后登录时间
        
        Given: 已注册的有效用户
        When: 成功登录后
        Then: 用户的 last_login_at 被更新，failed_login_attempts 清零
        
        覆盖 AC-1, AC-8
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
            "failed_login_attempts": 2,  # 之前有失败记录
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="测试用户",
            email="test@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
            failed_login_attempts=user_data["failed_login_attempts"],
        )
        db_session.add(user)
        await db_session.commit()
        
        before_login = datetime.now(timezone.utc)
        
        login_payload = {
            "username": "testuser",
            "password": "Test123456!",
        }
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        after_login = datetime.now(timezone.utc)
        
        # Then: 验证数据库更新
        assert response.status_code == 200
        
        # 刷新用户数据
        await db_session.refresh(user)
        
        # 验证最后登录时间被更新
        assert user.last_login_at is not None
        assert before_login <= user.last_login_at <= after_login
        
        # 验证失败次数清零
        assert user.failed_login_attempts == 0
        
        # 验证锁定状态清除
        assert user.locked_until is None


# ===========================================
# Test Class: 登录失败限制测试
# ===========================================

class TestLoginFailureLimit:
    """
    登录失败限制测试 - 防暴力破解
    
    覆盖验收标准: 7
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_account_locked_after_max_failed_attempts(self, app, db_session, user_factory):
        """
        测试账户在最大失败次数后被锁定
        
        Given: 有效用户
        When: 连续登录失败达到 MAX_LOGIN_ATTEMPTS 次
        Then: 账户状态变为 LOCKED，locked_until 被设置
        
        覆盖 AC-7
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "lock_test_user",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
            "failed_login_attempts": 0,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="锁定测试用户",
            email="locktest@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
            failed_login_attempts=0,
        )
        db_session.add(user)
        await db_session.commit()
        
        login_payload = {
            "username": "lock_test_user",
            "password": "WrongPassword!",
        }
        
        # When: 连续登录失败 MAX_LOGIN_ATTEMPTS 次
        async with AsyncClient(app=app, base_url="http://test") as client:
            for i in range(settings.MAX_LOGIN_ATTEMPTS):
                response = await client.post("/api/v1/auth/login", json=login_payload)
                assert response.status_code == 401
        
        # Then: 验证账户被锁定
        await db_session.refresh(user)
        assert user.status == UserStatus.LOCKED
        assert user.failed_login_attempts == settings.MAX_LOGIN_ATTEMPTS
        assert user.locked_until is not None
        
        # 验证锁定时间是未来时间
        lockout_end = user.locked_until
        assert lockout_end > datetime.now(timezone.utc)
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_login_locked_account_returns_403(self, app, db_session, user_factory):
        """
        测试登录被锁定的账户返回 403
        
        Given: 账户已被锁定（status=LOCKED）
        When: 尝试使用该账户登录
        Then: 返回 403 错误，错误码 USER_LOCKED
        
        覆盖 AC-5, AC-7
        """
        # Given: 创建已锁定的用户
        locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        user_data = user_factory.create(overrides={
            "username": "locked_user",
            "password": "Test123456!",
            "status": UserStatus.LOCKED,
            "failed_login_attempts": settings.MAX_LOGIN_ATTEMPTS,
            "locked_until": locked_until,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="已锁定用户",
            email="locked@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
            failed_login_attempts=user_data["failed_login_attempts"],
            locked_until=user_data["locked_until"],
        )
        db_session.add(user)
        await db_session.commit()
        
        login_payload = {
            "username": "locked_user",
            "password": "Test123456!",  # 即使是正确的密码
        }
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 403
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "USER_LOCKED"
        assert "账户已被锁定" in data["error"]["message"]
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - login endpoint not implemented")
    async def test_failed_login_increments_counter(self, app, db_session, user_factory):
        """
        测试每次失败登录增加失败计数器
        
        Given: 有效用户
        When: 登录失败多次但未达到最大值
        Then: 每次失败登录次数递增
        
        覆盖 AC-7, AC-8
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "counter_test_user",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
            "failed_login_attempts": 0,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="计数器测试用户",
            email="counter@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
            failed_login_attempts=0,
        )
        db_session.add(user)
        await db_session.commit()
        
        login_payload = {
            "username": "counter_test_user",
            "password": "WrongPassword!",
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # When: 第 1 次失败
            response = await client.post("/api/v1/auth/login", json=login_payload)
            assert response.status_code == 401
            
            # Then: 验证失败次数为 1
            await db_session.refresh(user)
            assert user.failed_login_attempts == 1
            
            # When: 第 2 次失败
            response = await client.post("/api/v1/auth/login", json=login_payload)
            assert response.status_code == 401
            
            # Then: 验证失败次数为 2
            await db_session.refresh(user)
            assert user.failed_login_attempts == 2
            
            # When: 第 3 次失败
            response = await client.post("/api/v1/auth/login", json=login_payload)
            assert response.status_code == 401
            
            # Then: 验证失败次数为 3
            await db_session.refresh(user)
            assert user.failed_login_attempts == 3


# ===========================================
# Test Class: 刷新 Token API 测试
# ===========================================

class TestRefreshTokenAPI:
    """
    刷新 Token API 测试 - POST /api/v1/auth/refresh
    
    覆盖验收标准: 3, 4, 5
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - refresh endpoint not implemented")
    async def test_refresh_token_success(self, app, db_session, user_factory, token_service):
        """
        测试刷新 Token 成功
        
        Given: 有效的 refresh_token
        When: 发送刷新 Token 请求
        Then: 返回新的 access_token 和 refresh_token
        
        覆盖 AC-3, AC-4
        """
        # Given: 创建测试用户并生成 Token
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="测试用户",
            email="test@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 生成有效的 refresh_token
        refresh_token = token_service.create_refresh_token(
            user_id=user.id,
            username=user.username,
        )
        
        refresh_payload = {
            "refresh_token": refresh_token,
        }
        
        # When: 发送刷新 Token 请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
        
        # Then: 验证响应
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        response_data = data["data"]
        
        # 验证新 Token
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert "token_type" in response_data
        assert "expires_in" in response_data
        
        assert response_data["token_type"] == "bearer"
        assert len(response_data["access_token"]) > 0
        assert len(response_data["refresh_token"]) > 0
        
        # 验证新旧 Token 不同
        assert response_data["refresh_token"] != refresh_token
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - refresh endpoint not implemented")
    async def test_refresh_token_invalid_returns_401(self, app):
        """
        测试无效 Token 返回 401
        
        Given: 无效的 refresh_token
        When: 发送刷新 Token 请求
        Then: 返回 401 错误，错误码 TOKEN_INVALID
        
        覆盖 AC-5
        """
        refresh_payload = {
            "refresh_token": "invalid_token_string",
        }
        
        # When: 发送刷新 Token 请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 401
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "TOKEN_INVALID"
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - refresh endpoint not implemented")
    async def test_refresh_token_expired_returns_401(self, app, db_session, user_factory, token_service):
        """
        测试过期 Token 返回 401
        
        Given: 已过期的 refresh_token
        When: 发送刷新 Token 请求
        Then: 返回 401 错误，错误码 TOKEN_EXPIRED
        
        覆盖 AC-5
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="测试用户",
            email="test@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        # 生成已过期 token（通过修改时间模拟）
        import time
        from jose import jwt
        
        now = int(time.time())
        expired_payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": now - 3600,  # 1 小时前过期
            "iat": now - 86400,  # 1 天前签发
            "type": "refresh",
        }
        
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        
        refresh_payload = {
            "refresh_token": expired_token,
        }
        
        # When: 发送刷新 Token 请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 401
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] in ["TOKEN_EXPIRED", "TOKEN_INVALID"]
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - refresh endpoint not implemented")
    async def test_refresh_token_inactive_user_returns_403(self, app, db_session, user_factory, token_service):
        """
        测试未激活用户刷新 Token 返回 403
        
        Given: 用户状态为 inactive，但持有有效的 refresh_token
        When: 发送刷新 Token 请求
        Then: 返回 403 错误，错误码 USER_INACTIVE
        
        覆盖 AC-5
        """
        # Given: 创建未激活用户
        user_data = user_factory.create(overrides={
            "username": "inactive_user",
            "password": "Test123456!",
            "status": UserStatus.INACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="未激活用户",
            email="inactive@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        # 生成有效的 refresh_token
        refresh_token = token_service.create_refresh_token(
            user_id=user.id,
            username=user.username,
        )
        
        refresh_payload = {
            "refresh_token": refresh_token,
        }
        
        # When: 发送刷新 Token 请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 403
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "USER_INACTIVE"
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - refresh endpoint not implemented")
    async def test_refresh_token_wrong_type_returns_401(self, app, db_session, user_factory, token_service):
        """
        测试使用 access_token 作为 refresh_token 返回 401
        
        Given: access_token（类型错误）
        When: 尝试用 access_token 刷新
        Then: 返回 401 错误，错误码 TOKEN_INVALID
        
        覆盖 AC-5
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="测试用户",
            email="test@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        # 生成 access_token（不是 refresh_token）
        access_token = token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
        )
        
        refresh_payload = {
            "refresh_token": access_token,  # 使用 access_token
        }
        
        # When: 发送刷新 Token 请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
        
        # Then: 验证错误响应
        assert response.status_code == 401
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "TOKEN_INVALID"


# ===========================================
# Test Class: 密码安全测试
# ===========================================

class TestPasswordSecurity:
    """
    密码安全测试 - 验证 bcrypt 加密
    
    覆盖验收标准: 6
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - password hashing verification")
    async def test_password_stored_as_bcrypt_hash(self, app, db_session, user_factory):
        """
        测试密码以 bcrypt 哈希形式存储
        
        Given: 新用户注册
        When: 用户密码被存储到数据库
        Then: 密码以 bcrypt 哈希形式存储，不是明文
        
        覆盖 AC-6
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "password_test_user",
            "password": "MySecurePassword123!",
            "status": UserStatus.ACTIVE,
        })
        
        password_hash = hash_password(user_data["password"])
        
        user = User(
            username=user_data["username"],
            password_hash=password_hash,
            real_name="密码测试用户",
            email="passwordtest@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        # Then: 验证数据库中的密码是哈希形式
        assert user.password_hash is not None
        assert user.password_hash != user_data["password"]  # 不是明文
        assert len(user.password_hash) > 0
        assert user.password_hash.startswith("$2")  # bcrypt 哈希以 $2 开头
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - password hashing verification")
    async def test_password_hash_unique_per_user(self, app, db_session, user_factory):
        """
        测试相同密码生成不同的哈希
        
        Given: 两个用户使用相同的密码
        When: 密码被加密存储
        Then: 两个用户的密码哈希不同（因为 salt 不同）
        
        覆盖 AC-6
        """
        # Given: 两个用户使用相同的密码
        common_password = "SamePassword123!"
        
        user1 = User(
            username="user1",
            password_hash=hash_password(common_password),
            real_name="用户 1",
            email="user1@example.com",
            role=UserRole.OPERATOR,
            status=UserStatus.ACTIVE,
        )
        
        user2 = User(
            username="user2",
            password_hash=hash_password(common_password),
            real_name="用户 2",
            email="user2@example.com",
            role=UserRole.OPERATOR,
            status=UserStatus.ACTIVE,
        )
        
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()
        
        # Then: 验证哈希不同
        assert user1.password_hash != user2.password_hash
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - password verification")
    async def test_password_verification_with_bcrypt(self, app, db_session, user_factory):
        """
        测试 bcrypt 密码验证
        
        Given: 用户密码已用 bcrypt 加密
        When: 使用正确或错误的密码验证
        Then: 正确密码返回 True，错误密码返回 False
        
        覆盖 AC-6
        """
        # Given: 创建测试用户
        password = "TestPassword123!"
        password_hash = hash_password(password)
        
        user = User(
            username="verify_test_user",
            password_hash=password_hash,
            real_name="验证测试用户",
            email="verify@example.com",
            role=UserRole.OPERATOR,
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        await db_session.commit()
        
        # When & Then: 验证密码
        # 正确密码应该返回 True
        assert verify_password(password, user.password_hash) is True
        
        # 错误密码应该返回 False
        assert verify_password("WrongPassword!", user.password_hash) is False
        assert verify_password("testpassword123!", user.password_hash) is False  # 大小写敏感
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - bcrypt rounds verification")
    async def test_bcrypt_rounds_configuration(self, app):
        """
        测试 bcrypt rounds 配置
        
        Given: 系统配置了 BCRYPT_ROUNDS
        When: 密码被加密
        Then: 使用正确的 rounds 数进行加密
        
        覆盖 AC-6
        """
        # Given: 配置中的 bcrypt rounds
        expected_rounds = settings.BCRYPT_ROUNDS
        
        password = "TestPassword123!"
        password_hash = hash_password(password)
        
        # Then: 验证 rounds 配置
        # bcrypt 哈希格式：$2b${rounds}${salt}${hash}
        parts = password_hash.split("$")
        assert len(parts) >= 4
        actual_rounds = int(parts[2])
        
        assert actual_rounds == expected_rounds
        assert actual_rounds >= 10  # 安全最佳实践


# ===========================================
# Test Class: 审计日志测试
# ===========================================

class TestAuditLogging:
    """
    审计日志测试 - 敏感操作记录
    
    覆盖验收标准: 8
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - audit logging not implemented")
    async def test_login_success_records_audit_log(self, app, db_session, user_factory):
        """
        测试登录成功记录审计日志
        
        Given: 用户成功登录
        When: 认证成功
        Then: 创建审计日志记录，包含用户 ID、时间、IP、操作类型
        
        覆盖 AC-8
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "audit_test_user",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="审计测试用户",
            email="audit@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        client_ip = "192.168.1.100"
        login_payload = {
            "username": "audit_test_user",
            "password": "Test123456!",
        }
        
        before_login = datetime.now(timezone.utc)
        
        # When: 发送登录请求
        async with AsyncClient(app=app, base_url="http://test", headers={"X-Forwarded-For": client_ip}) as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        after_login = datetime.now(timezone.utc)
        
        assert response.status_code == 200
        
        # Then: 验证审计日志记录
        # 注意：需要实现 AuditLog 模型和查询
        # from app.models.audit_log import AuditLog
        # result = await db_session.execute(
        #     select(AuditLog).where(
        #         AuditLog.user_id == user.id,
        #         AuditLog.action == "LOGIN_SUCCESS",
        #         AuditLog.timestamp >= before_login,
        #         AuditLog.timestamp <= after_login,
        #     )
        # )
        # audit_log = result.scalar_one_or_none()
        # assert audit_log is not None
        # assert audit_log.client_ip == client_ip
        
        # 暂时跳过，等待 AuditLog 模型实现
        pytest.skip("AuditLog model not implemented yet")
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - audit logging not implemented")
    async def test_login_failure_records_audit_log(self, app, db_session, user_factory):
        """
        测试登录失败记录审计日志
        
        Given: 用户登录失败
        When: 认证失败
        Then: 创建审计日志记录，包含用户 ID、时间、IP、操作类型、失败原因
        
        覆盖 AC-8
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "failure_audit_user",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="失败审计用户",
            email="failure@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        client_ip = "192.168.1.101"
        login_payload = {
            "username": "failure_audit_user",
            "password": "WrongPassword!",  # 错误的密码
        }
        
        # When: 发送登录请求（失败）
        async with AsyncClient(app=app, base_url="http://test", headers={"X-Forwarded-For": client_ip}) as client:
            response = await client.post("/api/v1/auth/login", json=login_payload)
        
        assert response.status_code == 401
        
        # Then: 验证审计日志记录
        # 类似上面的测试，验证失败日志被记录
        pytest.skip("AuditLog model not implemented yet")
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - audit logging not implemented")
    async def test_refresh_token_records_audit_log(self, app, db_session, user_factory, token_service):
        """
        测试刷新 Token 记录审计日志
        
        Given: 用户刷新 Token
        When: Token 刷新成功
        Then: 创建审计日志记录，包含用户 ID、时间、IP、操作类型
        
        覆盖 AC-8
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "refresh_audit_user",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="刷新审计用户",
            email="refresh@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        refresh_token = token_service.create_refresh_token(
            user_id=user.id,
            username=user.username,
        )
        
        client_ip = "192.168.1.102"
        refresh_payload = {
            "refresh_token": refresh_token,
        }
        
        # When: 发送刷新 Token 请求
        async with AsyncClient(app=app, base_url="http://test", headers={"X-Forwarded-For": client_ip}) as client:
            response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
        
        assert response.status_code == 200
        
        # Then: 验证审计日志记录
        pytest.skip("AuditLog model not implemented yet")


# ===========================================
# Test Class: 边界条件测试
# ===========================================

class TestBoundaryConditions:
    """
    边界条件测试 - 特殊场景处理
    
    覆盖验收标准: 2, 5, 7
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - boundary conditions")
    async def test_login_case_sensitive_username(self, app, db_session, user_factory):
        """
        测试用户名大小写敏感性
        
        Given: 用户名为 "TestUser"
        When: 使用 "testuser" 或 "TESTUSER" 登录
        Then: 根据系统设计返回成功或失败
        
        覆盖 AC-2
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "TestUser",  # 注意大小写
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="大小写测试用户",
            email="case@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        # When & Then: 测试不同大小写组合
        test_cases = [
            ("TestUser", True),   # 正确大小写
            ("testuser", False),  # 全小写
            ("TESTUSER", False),  # 全大写
            ("testUser", False),  # 混合
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for username, should_succeed in test_cases:
                login_payload = {
                    "username": username,
                    "password": "Test123456!",
                }
                
                response = await client.post("/api/v1/auth/login", json=login_payload)
                
                if should_succeed:
                    assert response.status_code == 200, f"Username {username} should succeed"
                else:
                    assert response.status_code == 401, f"Username {username} should fail"
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - boundary conditions")
    async def test_login_with_whitespace_in_username(self, app, db_session, user_factory):
        """
        测试用户名包含空格
        
        Given: 用户名包含前后空格
        When: 发送登录请求
        Then: 根据系统设计处理（通常应该 trim 或拒绝）
        
        覆盖 AC-2, AC-5
        """
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "testuser",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="空格测试用户",
            email="whitespace@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
        )
        db_session.add(user)
        await db_session.commit()
        
        # When: 发送带空格的登录请求
        test_cases = [
            {"username": " testuser", "password": "Test123456!"},
            {"username": "testuser ", "password": "Test123456!"},
            {"username": " testuser ", "password": "Test123456!"},
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for payload in test_cases:
                response = await client.post("/api/v1/auth/login", json=payload)
                # 根据系统设计，可能返回 401 或自动 trim 后成功
                # 这里假设系统会自动 trim
                assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="TDD red phase - boundary conditions")
    async def test_concurrent_login_attempts(self, app, db_session, user_factory):
        """
        测试并发登录尝试
        
        Given: 同一用户同时进行多次登录请求
        When: 并发发送登录请求
        Then: 正确处理失败次数计数，不会丢失更新
        
        覆盖 AC-7, AC-8
        """
        import asyncio
        
        # Given: 创建测试用户
        user_data = user_factory.create(overrides={
            "username": "concurrent_user",
            "password": "Test123456!",
            "status": UserStatus.ACTIVE,
            "failed_login_attempts": 0,
        })
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name="并发测试用户",
            email="concurrent@example.com",
            role=UserRole.OPERATOR,
            status=user_data["status"],
            failed_login_attempts=0,
        )
        db_session.add(user)
        await db_session.commit()
        
        login_payload = {
            "username": "concurrent_user",
            "password": "WrongPassword!",
        }
        
        # When: 并发发送 5 次登录请求
        async def make_login_request():
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post("/api/v1/auth/login", json=login_payload)
                return response.status_code
        
        tasks = [make_login_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Then: 验证所有请求都返回 401
        assert all(status == 401 for status in results)
        
        # 验证失败次数正确累加（考虑并发锁）
        await db_session.refresh(user)
        assert user.failed_login_attempts == 5

"""
pytest 测试 Fixtures - 内部运营中台客户信息管理与运营系统

架构模式：
1. 会话级数据库连接
2. 自动回滚事务
3. 数据工厂集成
4. 异步测试支持
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime
from faker import Faker

# 导入应用模型和服务
# from backend.models.customer import Customer
# from backend.models.user import User
# from backend.database.session import get_async_session

fake = Faker('zh_CN')

# ===========================================
# 数据库 Fixtures
# ===========================================

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """创建测试数据库引擎"""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:password@localhost:5432/cs_ops_test",
        echo=False,
        pool_pre_ping=True,
    )
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator:
    """
    创建测试数据库会话
    
    每个测试运行在独立的事务中，测试完成后自动回滚
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_session
    from sqlalchemy.orm import sessionmaker
    
    connection = await db_engine.connect()
    transaction = await connection.begin()
    
    session_maker = sessionmaker(
        connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    session = session_maker()
    
    yield session
    
    # 回滚事务（清理测试数据）
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def app(db_session):
    """创建 Sanic 测试应用实例"""
    from backend.app import create_app
    
    app = await create_app()
    
    # 注入数据库会话
    app.ctx.db_session = db_session
    
    yield app


# ===========================================
# 认证 Fixtures
# ===========================================

@pytest_asyncio.fixture
async def auth_token(app, db_session):
    """生成测试用户 JWT 令牌"""
    from jose import jwt
    
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "operator",
        "exp": datetime.utcnow().timestamp() + 3600,
    }
    
    token = jwt.encode(
        payload,
        app.config.SECRET_KEY,
        algorithm=app.config.JWT_ALGORITHM,
    )
    
    return f"Bearer {token}"


@pytest_asyncio.fixture
async def authenticated_client(app, auth_token):
    """创建带认证的测试客户端"""
    from httpx import AsyncClient, ASGITransport
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        client.headers["Authorization"] = auth_token
        yield client


# ===========================================
# 数据工厂 Fixtures
# ===========================================

class CustomerFactory:
    """客户数据工厂"""
    
    _created_customers = []
    
    @classmethod
    def create(cls, overrides=None):
        """创建客户数据"""
        data = {
            "name": fake.company(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "status": "active",
        }
        
        if overrides:
            data.update(overrides)
        
        cls._created_customers.append(data)
        return data
    
    @classmethod
    async def create_in_db(cls, session, overrides=None):
        """在数据库中创建客户"""
        from backend.models.customer import Customer
        
        data = cls.create(overrides)
        
        customer = Customer(**data)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        
        cls._created_customers.append({"id": customer.id, **data})
        return customer
    
    @classmethod
    def cleanup(cls):
        """清理工厂创建的数据"""
        cls._created_customers.clear()


class UserFactory:
    """用户数据工厂"""
    
    _created_users = []
    
    @classmethod
    def create(cls, overrides=None):
        """创建用户数据"""
        data = {
            "email": fake.email(),
            "username": fake.user_name(),
            "password": "Test123456!",
            "role": "operator",
        }
        
        if overrides:
            data.update(overrides)
        
        cls._created_users.append(data)
        return data


@pytest.fixture
def customer_factory():
    """客户工厂 fixture"""
    yield CustomerFactory
    CustomerFactory.cleanup()


@pytest.fixture
def user_factory():
    """用户工厂 fixture"""
    yield UserFactory
    UserFactory._created_users.clear()


# ===========================================
# 通用 Fixtures
# ===========================================

@pytest.fixture
def sample_date_range():
    """生成样例日期范围"""
    from datetime import timedelta
    
    start_date = datetime(2024, 1, 1)
    end_date = start_date + timedelta(days=30)
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_date_str": start_date.isoformat(),
        "end_date_str": end_date.isoformat(),
    }


@pytest.fixture
def pagination_params():
    """生成分页参数"""
    return {
        "page": 1,
        "page_size": 20,
        "offset": 0,
        "limit": 20,
    }


@pytest.fixture(autouse=True)
def reset_factories():
    """每个测试前重置工厂状态"""
    yield
    CustomerFactory.cleanup()
    UserFactory._created_users.clear()

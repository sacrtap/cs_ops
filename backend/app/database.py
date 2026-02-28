"""
数据库连接管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from app.config.settings import settings
from app.models.base import Base


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境打印 SQL
    pool_pre_ping=True,  # 连接前 ping 测试
    pool_size=20,  # 连接池大小
    max_overflow=40,  # 最大溢出连接数
)

# 创建异步 Session 工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    获取数据库会话依赖（用于 API 路由）
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库（创建所有表）
    
    注意：生产环境应使用 Alembic 迁移
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()

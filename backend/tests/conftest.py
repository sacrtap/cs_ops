# -*- coding: utf-8 -*-
"""
Pytest 配置 Fixtures - 后端测试

提供数据库引擎、会话和测试数据的 fixtures
"""

import asyncio
import pytest
import pytest_asyncio
import sys
import os
from typing import AsyncGenerator, Generator

# 添加 backend 目录到 Python 路径
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# 现在可以导入 app 模块
from app.models.user import User, UserRole, UserStatus
from app.models.customer import Customer
from app.models.organization import Organization
from app.models.base import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

# 测试数据库 URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops_test"
)

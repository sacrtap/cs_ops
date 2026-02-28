"""
数据库模型初始化模块
"""
from app.models.user import User
from app.models.base import Base

__all__ = ["Base", "User"]

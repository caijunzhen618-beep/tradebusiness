"""
Repository 模块 - 包含数据访问层
"""

from app.repositories.base import BaseRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.user_repo import UserRepository

__all__ = ["BaseRepository", "UserRepository", "CustomerRepository"]

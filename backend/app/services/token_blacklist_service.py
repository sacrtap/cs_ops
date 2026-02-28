"""
Token 黑名单服务 - 管理 Token 失效
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
import hashlib
from app.models.token_blacklist import TokenBlacklist, TokenBlacklistType, BlacklistReason


class TokenBlacklistService:
    """Token 黑名单服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def hash_token(self, token: str) -> str:
        """
        计算 Token 的 SHA256 哈希
        
        Args:
            token: JWT Token 字符串
            
        Returns:
            str: SHA256 哈希（64 字符十六进制）
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def is_blacklisted(self, token_hash: str) -> bool:
        """
        检查 Token 是否在黑名单中
        
        Args:
            token_hash: Token 哈希
            
        Returns:
            bool: True 如果在黑名单中
        """
        result = await self.db.execute(
            select(TokenBlacklist).where(
                TokenBlacklist.token_hash == token_hash,
                TokenBlacklist.expires_at > datetime.now(timezone.utc)
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_to_blacklist(
        self,
        token_hash: str,
        token_type: TokenBlacklistType,
        user_id: int,
        expires_at: datetime,
        reason: BlacklistReason = BlacklistReason.LOGOUT
    ) -> TokenBlacklist:
        """
        将 Token 加入黑名单
        
        Args:
            token_hash: Token 哈希
            token_type: Token 类型
            user_id: 用户 ID
            expires_at: Token 过期时间
            reason: 加入黑名单原因
            
        Returns:
            TokenBlacklist: 黑名单记录
        """
        blacklist_entry = TokenBlacklist(
            token_hash=token_hash,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason
        )
        
        self.db.add(blacklist_entry)
        await self.db.commit()
        await self.db.refresh(blacklist_entry)
        
        return blacklist_entry

    async def add_token_to_blacklist(
        self,
        token: str,
        token_type: TokenBlacklistType,
        user_id: int,
        expires_at: datetime,
        reason: BlacklistReason = BlacklistReason.LOGOUT
    ) -> TokenBlacklist:
        """
        将 Token 加入黑名单（便捷方法）
        
        Args:
            token: JWT Token 字符串
            token_type: Token 类型
            user_id: 用户 ID
            expires_at: Token 过期时间
            reason: 加入黑名单原因
            
        Returns:
            TokenBlacklist: 黑名单记录
        """
        token_hash = self.hash_token(token)
        return await self.add_to_blacklist(
            token_hash, token_type, user_id, expires_at, reason
        )

    async def cleanup_expired(self) -> int:
        """
        清理过期的黑名单记录
        
        Returns:
            int: 删除的记录数
        """
        result = await self.db.execute(
            delete(TokenBlacklist).where(
                TokenBlacklist.expires_at < datetime.now(timezone.utc)
            )
        )
        await self.db.commit()
        return result.rowcount

    async def cleanup_old_blacklist_records(self, days_old: int = 30) -> int:
        """
        清理指定天数之前的黑名单记录（定时任务使用）
        
        Args:
            days_old: 清理多少天之前的记录，默认 30 天
            
        Returns:
            int: 删除的记录数
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        result = await self.db.execute(
            delete(TokenBlacklist).where(
                TokenBlacklist.blacklisted_at < cutoff_date
            )
        )
        await self.db.commit()
        
        # 记录日志
        deleted_count = result.rowcount
        if deleted_count > 0:
            print(f"[TokenBlacklist] 清理了 {deleted_count} 条 {days_old} 天前的黑名单记录")
        
        return deleted_count

    async def get_user_blacklist_count(
        self,
        user_id: int,
        include_expired: bool = False
    ) -> int:
        """
        获取用户的黑名单记录数
        
        Args:
            user_id: 用户 ID
            include_expired: 是否包含过期记录
            
        Returns:
            int: 黑名单记录数
        """
        query = select(TokenBlacklist).where(TokenBlacklist.user_id == user_id)
        
        if not include_expired:
            query = query.where(
                TokenBlacklist.expires_at > datetime.now(timezone.utc)
            )
        
        result = await self.db.execute(query)
        return len(result.scalars().all())


# 注意：此服务需要在 AsyncSession 上下文中使用
# 示例用法：
# async with get_db() as db:
#     service = TokenBlacklistService(db)
#     is_valid = not await service.is_blacklisted(token_hash)

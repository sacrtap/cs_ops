"""
权限缓存工具 - LRU 缓存实现
"""
from functools import lru_cache
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio


class PermissionCache:
    """
    权限矩阵 LRU 缓存
    
    特性:
    - 最大 128 个条目
    - 30 分钟 TTL
    - 支持按角色清除缓存
    - 支持清除所有缓存
    """
    
    def __init__(self, max_size: int = 128, ttl_minutes: int = 30):
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._hits = 0
        self._misses = 0
    
    def _get_cache_key(self, role: str) -> str:
        """生成缓存键"""
        return f"permission:{role}"
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if key not in self._timestamps:
            return True
        return datetime.now() - self._timestamps[key] > self.ttl
    
    async def get(self, role: str) -> Optional[Dict]:
        """
        获取角色的权限缓存
        
        Args:
            role: 角色名称
            
        Returns:
            权限字典或 None（缓存未命中或已过期）
        """
        key = self._get_cache_key(role)
        
        # 检查缓存是否存在且未过期
        if key not in self._cache or self._is_expired(key):
            self._misses += 1
            return None
        
        self._hits += 1
        return self._cache[key]
    
    async def set(self, role: str, permissions: Dict) -> None:
        """
        设置角色的权限缓存
        
        Args:
            role: 角色名称
            permissions: 权限字典
        """
        key = self._get_cache_key(role)
        
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self.max_size and key not in self._cache:
            # 简单策略：删除第一个条目
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        self._cache[key] = permissions
        self._timestamps[key] = datetime.now()
    
    async def clear(self, role: Optional[str] = None) -> None:
        """
        清除缓存
        
        Args:
            role: 可选，指定清除某个角色的缓存；如果不指定，清除所有缓存
        """
        if role:
            key = self._get_cache_key(role)
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
        else:
            self._cache.clear()
            self._timestamps.clear()
    
    def get_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            包含缓存大小、命中次数、未命中次数、命中率的字典
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "ttl_seconds": self.ttl.total_seconds(),
        }
    
    async def refresh(self, role: str, refresh_func) -> Optional[Dict]:
        """
        刷新缓存（如果过期或不存在）
        
        Args:
            role: 角色名称
            refresh_func: 异步函数，用于刷新数据（接收 role 参数）
            
        Returns:
            权限字典
        """
        # 尝试从缓存获取
        cached = await self.get(role)
        if cached is not None:
            return cached
        
        # 缓存未命中，刷新数据
        fresh_data = await refresh_func(role)
        await self.set(role, fresh_data)
        return fresh_data


# 全局缓存实例
_permission_cache: Optional[PermissionCache] = None


def get_permission_cache() -> PermissionCache:
    """获取全局权限缓存实例"""
    global _permission_cache
    if _permission_cache is None:
        _permission_cache = PermissionCache(max_size=128, ttl_minutes=30)
    return _permission_cache


def reset_permission_cache() -> None:
    """重置全局缓存（用于测试）"""
    global _permission_cache
    _permission_cache = None

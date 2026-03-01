"""
权限矩阵服务 - 功能权限管理
"""
from typing import Dict, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.permission_matrix import PermissionMatrix
from app.utils.permission_cache import get_permission_cache


class PermissionMatrixService:
    """
    权限矩阵服务层
    
    提供权限查询、更新、缓存管理等功能
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = get_permission_cache()
    
    async def get_role_permissions(self, role: str) -> Dict[str, Dict[str, bool]]:
        """
        获取角色的所有权限
        
        Args:
            role: 角色名称 (admin/manager/specialist/sales)
            
        Returns:
            权限字典：{module: {action: granted}}
            例如：{"customer": {"read": True, "create": False, ...}, ...}
        """
        # 尝试从缓存获取
        cached = await self.cache.get(role)
        if cached is not None:
            return cached
        
        # 缓存未命中，从数据库查询
        permissions = await self._query_from_db(role)
        
        # 写入缓存
        await self.cache.set(role, permissions)
        
        return permissions
    
    async def _query_from_db(self, role: str) -> Dict[str, Dict[str, bool]]:
        """
        从数据库查询角色权限
        
        Args:
            role: 角色名称
            
        Returns:
            权限字典
        """
        stmt = select(PermissionMatrix).where(PermissionMatrix.role == role)
        result = await self.session.execute(stmt)
        matrices = result.scalars().all()
        
        # 转换为嵌套字典
        permissions: Dict[str, Dict[str, bool]] = {}
        for matrix in matrices:
            if matrix.module not in permissions:
                permissions[matrix.module] = {}
            permissions[matrix.module][matrix.action] = matrix.granted
        
        return permissions
    
    async def check_permission(self, role: str, module: str, action: str) -> bool:
        """
        检查角色是否有某功能的某操作权限
        
        Args:
            role: 角色名称
            module: 功能模块
            action: 操作类型
            
        Returns:
            True 如果有权限，False 如果无权限
        """
        permissions = await self.get_role_permissions(role)
        
        # 检查模块是否存在
        if module not in permissions:
            return False
        
        # 检查操作是否存在
        if action not in permissions[module]:
            return False
        
        return permissions[module][action]
    
    async def update_permission(
        self,
        role: str,
        module: str,
        action: str,
        granted: bool
    ) -> Optional[PermissionMatrix]:
        """
        更新单个权限配置
        
        Args:
            role: 角色名称
            module: 功能模块
            action: 操作类型
            granted: 是否授权
            
        Returns:
            更新后的权限记录，如果不存在则返回 None
        """
        # 查询现有记录
        stmt = select(PermissionMatrix).where(
            and_(
                PermissionMatrix.role == role,
                PermissionMatrix.module == module,
                PermissionMatrix.action == action
            )
        )
        result = await self.session.execute(stmt)
        matrix = result.scalar_one_or_none()
        
        if matrix:
            # 更新现有记录
            matrix.granted = granted
            await self.session.commit()
            await self.session.refresh(matrix)
        else:
            # 创建新记录
            matrix = PermissionMatrix(
                role=role,
                module=module,
                action=action,
                granted=granted
            )
            self.session.add(matrix)
            await self.session.commit()
            await self.session.refresh(matrix)
        
        # 清除相关角色的缓存
        await self.cache.clear(role)
        
        return matrix
    
    async def bulk_update_permissions(self, permissions: List[Dict]) -> int:
        """
        批量更新权限配置
        
        Args:
            permissions: 权限列表，每项包含 role, module, action, granted
            
        Returns:
            更新的记录数量
        """
        updated_count = 0
        
        for perm in permissions:
            await self.update_permission(
                role=perm["role"],
                module=perm["module"],
                action=perm["action"],
                granted=perm["granted"]
            )
            updated_count += 1
        
        return updated_count
    
    async def get_default_permissions(self) -> List[Dict]:
        """
        获取默认权限矩阵
        
        Returns:
            默认权限列表
        """
        # 获取所有角色的权限
        roles = ["admin", "manager", "specialist", "sales"]
        defaults = []
        
        for role in roles:
            permissions = await self.get_role_permissions(role)
            for module, actions in permissions.items():
                for action, granted in actions.items():
                    defaults.append({
                        "role": role,
                        "module": module,
                        "action": action,
                        "granted": granted,
                    })
        
        return defaults
    
    async def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        return self.cache.get_stats()
    
    async def clear_cache(self, role: Optional[str] = None) -> None:
        """
        清除权限缓存
        
        Args:
            role: 可选，指定清除某个角色的缓存；如果不指定，清除所有缓存
        """
        await self.cache.clear(role)

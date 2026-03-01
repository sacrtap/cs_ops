"""
Permission Inheritance Service - 权限继承服务

实现角色权限继承机制：
- 高级角色自动继承低级角色的所有权限
- 支持额外授权机制
- 权限缓存优化
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Set
from ..models.roles import Role
from ..models.role_permission import RolePermission
from ..models.user import UserRole

# 权限缓存（生产环境建议使用 Redis）
_permission_cache: Dict[str, Dict] = {}
_hierarchy_cache: Optional[Dict] = None


class PermissionInheritanceService:
    """权限继承服务"""
    
    @staticmethod
    async def get_role_hierarchy(session: AsyncSession) -> Dict:
        """
        获取角色层级结构
        
        Returns:
            Dict: 角色层级结构，包含所有角色及其继承关系
        """
        global _hierarchy_cache
        
        # 检查缓存
        if _hierarchy_cache is not None:
            return _hierarchy_cache
        
        # 查询所有角色
        stmt = select(Role).where(Role.status == 'active').order_by(Role.level.desc())
        result = await session.execute(stmt)
        roles = result.scalars().all()
        
        # 构建层级结构
        hierarchy = {
            "levels": []
        }
        
        for role in roles:
            # 查询该角色继承的所有角色
            inherited_roles = await PermissionInheritanceService.get_inherited_roles(role, session)
            
            hierarchy["levels"].append({
                "level": role.level,
                "role": role.name,
                "name": role.name,
                "inherits": [r.name for r in inherited_roles]
            })
        
        # 缓存结果
        _hierarchy_cache = hierarchy
        return hierarchy
    
    @staticmethod
    async def get_inherited_roles(role: Role, session: AsyncSession) -> List[Role]:
        """
        获取角色继承的所有下级角色
        
        Args:
            role: 角色对象
            session: 数据库会话
            
        Returns:
            List[Role]: 继承的角色列表
        """
        # 查询所有级别低于当前角色的活跃角色
        stmt = select(Role).where(
            Role.level < role.level,
            Role.status == 'active'
        ).order_by(Role.level.desc())
        
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_role_permissions_with_inheritance(
        role_name: str,
        session: AsyncSession
    ) -> Dict:
        """
        获取角色的所有权限（包含继承的权限）
        
        Args:
            role_name: 角色名称
            session: 数据库会话
            
        Returns:
            Dict: 权限信息，包含继承权限和额外授权
        """
        cache_key = f"role_perms_{role_name}"
        
        # 检查缓存
        if cache_key in _permission_cache:
            return _permission_cache[cache_key]
        
        # 查询角色
        stmt = select(Role).where(Role.name == role_name)
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            return {
                "error": f"Role '{role_name}' not found",
                "inherited_from": [],
                "inherited_permissions": [],
                "additional_permissions": []
            }
        
        # 获取继承的角色列表
        inherited_roles = await PermissionInheritanceService.get_inherited_roles(role, session)
        inherited_role_names = [r.name for r in inherited_roles]
        
        # 查询角色的直接权限
        direct_perms_stmt = select(RolePermission).where(
            RolePermission.role == role_name
        )
        result = await session.execute(direct_perms_stmt)
        direct_permissions = result.scalars().all()
        
        # 查询继承的权限
        inherited_permissions = []
        if inherited_role_names:
            inherited_perms_stmt = select(RolePermission).where(
                RolePermission.role.in_(inherited_role_names)
            )
            result = await session.execute(inherited_perms_stmt)
            all_inherited_perms = result.scalars().all()
            
            # 去重并按角色分组
            seen = set()
            for perm in all_inherited_perms:
                key = (perm.resource, perm.action)
                if key not in seen:
                    inherited_permissions.append({
                        "resource": perm.resource,
                        "action": perm.action,
                        "inherited_from": perm.role
                    })
                    seen.add(key)
        
        # 构建结果
        result_dict = {
            "role": role_name,
            "level": role.level,
            "inherited_from": inherited_role_names,
            "inherited_permissions": inherited_permissions,
            "direct_permissions": [
                {"resource": p.resource, "action": p.action}
                for p in direct_permissions
            ],
            "all_permissions": []  # 合并所有权限
        }
        
        # 合并所有权限（继承 + 直接）
        all_perms_set: Set[tuple] = set()
        for perm in inherited_permissions:
            all_perms_set.add((perm["resource"], perm["action"]))
        for perm in direct_permissions:
            all_perms_set.add((perm.resource, perm.action))
        
        result_dict["all_permissions"] = [
            {"resource": r, "action": a}
            for r, a in all_perms_set
        ]
        
        # 缓存结果
        _permission_cache[cache_key] = result_dict
        return result_dict
    
    @staticmethod
    async def check_permission_with_inheritance(
        role_name: str,
        resource: str,
        action: str,
        session: AsyncSession
    ) -> Dict:
        """
        检查角色是否有权限（包含继承权限）
        
        Args:
            role_name: 角色名称
            resource: 资源名称
            action: 操作类型
            session: 数据库会话
            
        Returns:
            Dict: 权限检查结果，包含权限来源
        """
        cache_key = f"check_{role_name}_{resource}_{action}"
        
        # 检查缓存
        if cache_key in _permission_cache:
            return _permission_cache[cache_key]
        
        # Admin 特殊处理
        if role_name == UserRole.ADMIN.value:
            result = {
                "has_permission": True,
                "source": "admin",
                "message": "Admin has all permissions"
            }
            _permission_cache[cache_key] = result
            return result
        
        # 查询角色
        stmt = select(Role).where(Role.name == role_name)
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            result = {
                "has_permission": False,
                "source": "none",
                "message": f"Role '{role_name}' not found"
            }
            _permission_cache[cache_key] = result
            return result
        
        # 先检查直接权限
        direct_stmt = select(RolePermission).where(
            RolePermission.role == role_name,
            RolePermission.resource == resource,
            RolePermission.action == action
        )
        result = await session.execute(direct_stmt)
        direct_perm = result.scalar_one_or_none()
        
        if direct_perm:
            result = {
                "has_permission": True,
                "source": "direct",
                "message": f"Permission granted directly to role '{role_name}'"
            }
            _permission_cache[cache_key] = result
            return result
        
        # 检查继承权限
        inherited_roles = await PermissionInheritanceService.get_inherited_roles(role, session)
        
        for inherited_role in inherited_roles:
            inherited_stmt = select(RolePermission).where(
                RolePermission.role == inherited_role.name,
                RolePermission.resource == resource,
                RolePermission.action == action
            )
            result = await session.execute(inherited_stmt)
            inherited_perm = result.scalar_one_or_none()
            
            if inherited_perm:
                result = {
                    "has_permission": True,
                    "source": "inherited",
                    "inherited_from": inherited_role.name,
                    "message": f"Permission inherited from role '{inherited_role.name}'"
                }
                _permission_cache[cache_key] = result
                return result
        
        # 无权限
        result = {
            "has_permission": False,
            "source": "none",
            "message": f"Role '{role_name}' does not have permission '{action}' on '{resource}'"
        }
        _permission_cache[cache_key] = result
        return result
    
    @staticmethod
    def clear_cache():
        """清除所有缓存"""
        global _permission_cache, _hierarchy_cache
        _permission_cache.clear()
        _hierarchy_cache = None
    
    @staticmethod
    def invalidate_role_cache(role_name: str):
        """使特定角色的缓存失效"""
        keys_to_remove = [
            k for k in _permission_cache.keys()
            if k.startswith(f"role_perms_{role_name}") or 
               k.startswith(f"check_{role_name}")
        ]
        for key in keys_to_remove:
            del _permission_cache[key]

"""
角色管理服务 - 系统角色管理
"""
from typing import Dict, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.models.roles import Role
from app.models.permission_matrix import PermissionMatrix
from app.utils.permission_cache import get_permission_cache


class RoleManagementService:
    """
    角色管理服务层
    
    提供角色查询、创建、更新、删除等功能
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_roles(self) -> List[Dict]:
        """
        获取所有角色列表
        
        Returns:
            角色列表
        """
        stmt = select(Role).order_by(Role.id)
        result = await self.session.execute(stmt)
        roles = result.scalars().all()
        
        return [role.to_dict() for role in roles]
    
    async def get_role_by_id(self, role_id: int) -> Optional[Dict]:
        """
        通过 ID 获取角色信息
        
        Args:
            role_id: 角色 ID
            
        Returns:
            角色信息字典，如果不存在则返回 None
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        
        return role.to_dict() if role else None
    
    async def get_role_by_name(self, role_name: str) -> Optional[Dict]:
        """
        通过名称获取角色信息
        
        Args:
            role_name: 角色名称
            
        Returns:
            角色信息字典，如果不存在则返回 None
        """
        stmt = select(Role).where(Role.name == role_name)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        
        return role.to_dict() if role else None
    
    async def create_role(self, role_data: Dict) -> Dict:
        """
        创建新角色
        
        Args:
            role_data: 角色数据字典，包含 name, description, status
            
        Returns:
            创建后的角色信息
        """
        role = Role(
            name=role_data["name"],
            description=role_data.get("description", ""),
            status=role_data.get("status", "active")
        )
        
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        
        return role.to_dict()
    
    async def update_role(self, role_id: int, role_data: Dict) -> Optional[Dict]:
        """
        更新角色信息
        
        Args:
            role_id: 角色 ID
            role_data: 角色数据字典
            
        Returns:
            更新后的角色信息，如果不存在则返回 None
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            return None
        
        # 更新字段
        if "name" in role_data:
            role.name = role_data["name"]
        if "description" in role_data:
            role.description = role_data["description"]
        if "status" in role_data:
            role.status = role_data["status"]
        
        await self.session.commit()
        await self.session.refresh(role)
        
        return role.to_dict()
    
    async def delete_role(self, role_id: int) -> bool:
        """
        删除角色
        
        Args:
            role_id: 角色 ID
            
        Returns:
            True 如果删除成功，False 如果角色不存在
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            return False
        
        # 检查是否为系统默认角色
        if role.name in ["admin", "manager", "specialist", "sales"]:
            raise ValueError(f"无法删除系统默认角色：{role.name}")
        
        await self.session.delete(role)
        await self.session.commit()
        
        return True
    
    async def get_role_permissions(self, role_id: int) -> Optional[Dict[str, Dict[str, bool]]]:
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色 ID
            
        Returns:
            权限字典：{module: {action: granted}}，如果角色不存在则返回 None
        """
        # 获取角色名称
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
        
        role_name = role["name"]
        
        # 从权限矩阵查询权限
        stmt = select(PermissionMatrix).where(PermissionMatrix.role == role_name)
        result = await self.session.execute(stmt)
        matrices = result.scalars().all()
        
        # 转换为嵌套字典
        permissions: Dict[str, Dict[str, bool]] = {}
        for matrix in matrices:
            if matrix.module not in permissions:
                permissions[matrix.module] = {}
            permissions[matrix.module][matrix.action] = matrix.granted
        
        return permissions
    
    async def update_role_permissions(
        self,
        role_id: int,
        permissions: Dict[str, Dict[str, bool]]
    ) -> Optional[Dict]:
        """
        更新角色的权限配置
        
        Args:
            role_id: 角色 ID
            permissions: 权限字典 {module: {action: granted}}
            
        Returns:
            更新后的角色信息，如果角色不存在则返回 None
        """
        # 获取角色名称
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
        
        role_name = role["name"]
        
        # 检查是否为系统默认角色
        if role_name == "admin":
            raise ValueError("无法修改 Admin 角色的默认权限配置")
        
        # 手动管理事务，避免 async with 的测试复杂性
        transaction = await self.session.begin()
        try:
            # 删除现有权限
            stmt = select(PermissionMatrix).where(PermissionMatrix.role == role_name)
            result = await self.session.execute(stmt)
            existing_permissions = result.scalars().all()
            
            for perm in existing_permissions:
                await self.session.delete(perm)
            
            # 创建新权限
            for module, actions in permissions.items():
                for action, granted in actions.items():
                    new_perm = PermissionMatrix(
                        role=role_name,
                        module=module,
                        action=action,
                        granted=granted
                    )
                    self.session.add(new_perm)
            
            await transaction.commit()
        except Exception:
            await transaction.rollback()
            raise
        
        # 清除权限缓存
        cache = get_permission_cache()
        await cache.clear(role_name)
        
        await self.session.refresh(role)
        
        return role
    
    async def get_default_permissions(self, role_name: str) -> Optional[Dict[str, Dict[str, bool]]]:
        """
        获取角色的默认权限配置
        
        Args:
            role_name: 角色名称
            
        Returns:
            默认权限字典，如果角色不存在则返回 None
        """
        role = await self.get_role_by_name(role_name)
        if not role:
            return None
        
        # 从权限矩阵查询默认权限
        stmt = select(PermissionMatrix).where(PermissionMatrix.role == role_name)
        result = await self.session.execute(stmt)
        matrices = result.scalars().all()
        
        # 转换为嵌套字典
        permissions: Dict[str, Dict[str, bool]] = {}
        for matrix in matrices:
            if matrix.module not in permissions:
                permissions[matrix.module] = {}
            permissions[matrix.module][matrix.action] = matrix.granted
        
        return permissions
    
    async def get_users_by_role(self, role_id: int) -> List[Dict]:
        """
        获取拥有该角色的所有用户
        
        Args:
            role_id: 角色 ID
            
        Returns:
            用户列表
        """
        from app.models.user import User
        
        role = await self.get_role_by_id(role_id)
        if not role:
            return []
        
        role_name = role["name"]
        
        stmt = select(User).where(User.role == role_name)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        
        return [user.to_dict() for user in users]
    
    async def get_role_stats(self) -> Dict:
        """
        获取角色统计信息
        
        Returns:
            统计信息字典
        """
        from app.models.user import User
        
        # 获取所有角色
        roles = await self.get_all_roles()
        
        # 统计每个角色的用户数
        stats = []
        for role in roles:
            user_count_stmt = select(func.count(User.id)).where(User.role == role["name"])
            user_count_result = await self.session.execute(user_count_stmt)
            user_count = user_count_result.scalar() or 0
            
            stats.append({
                **role,
                "user_count": user_count
            })
        
        return {
            "total_roles": len(roles),
            "active_roles": sum(1 for r in roles if r["status"] == "active"),
            "inactive_roles": sum(1 for r in roles if r["status"] == "inactive"),
            "roles": stats
        }

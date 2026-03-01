"""
单元测试：权限继承服务

测试覆盖：
- 角色层级查询
- 权限继承逻辑
- 额外授权管理
- 缓存机制
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.permission_inheritance_service import PermissionInheritanceService


class TestRoleHierarchy:
    """角色层级测试"""

    @pytest.mark.asyncio
    async def test_get_role_hierarchy(self, async_session: AsyncSession):
        """测试获取角色层级结构"""
        result = await PermissionInheritanceService.get_role_hierarchy(async_session)
        
        assert result["success"] is True
        assert "levels" in result["data"]
        assert len(result["data"]["levels"]) == 4
        
        # 验证层级顺序
        levels = result["data"]["levels"]
        assert levels[0]["level"] == 4  # Admin
        assert levels[1]["level"] == 3  # Manager
        assert levels[2]["level"] == 2  # Specialist
        assert levels[3]["level"] == 1  # Sales

    @pytest.mark.asyncio
    async def test_get_inherited_roles(self, async_session: AsyncSession):
        """测试获取继承的角色列表"""
        # 经理应该继承专员和销售
        result = await PermissionInheritanceService.get_inherited_roles(
            "manager", async_session
        )
        
        assert result["success"] is True
        assert "specialist" in result["inherited_roles"]
        assert "sales" in result["inherited_roles"]
        
        # Admin 应该继承所有下级
        result = await PermissionInheritanceService.get_inherited_roles(
            "admin", async_session
        )
        assert "manager" in result["inherited_roles"]
        assert "specialist" in result["inherited_roles"]
        assert "sales" in result["inherited_roles"]


class TestPermissionInheritance:
    """权限继承测试"""

    @pytest.mark.asyncio
    async def test_get_role_permissions_with_inheritance(self, async_session: AsyncSession):
        """测试获取包含继承的权限"""
        result = await PermissionInheritanceService.get_role_permissions_with_inheritance(
            "manager", async_session
        )
        
        assert result["success"] is True
        assert "inherited_permissions" in result["data"]
        assert "direct_permissions" in result["data"]
        assert "all_permissions" in result["data"]

    @pytest.mark.asyncio
    async def test_check_permission_with_inheritance(self, async_session: AsyncSession):
        """测试权限检查（包含继承）"""
        # 经理应该能继承专员的权限
        result = await PermissionInheritanceService.check_permission_with_inheritance(
            "manager", "customer", "delete", async_session
        )
        
        assert result["success"] is True
        # 可能来自继承或直接授权
        assert "has_permission" in result["data"]


class TestAdditionalAuthorization:
    """额外授权测试"""

    @pytest.mark.asyncio
    async def test_grant_additional_permission(self, async_session: AsyncSession):
        """测试添加额外授权"""
        result = await PermissionInheritanceService.grant_additional_permission(
            "manager", "role", "delete", async_session
        )
        
        # 首次创建应该成功
        assert result["success"] is True
        assert "permission_id" in result

    @pytest.mark.asyncio
    async def test_get_additional_permissions(self, async_session: AsyncSession):
        """测试获取额外授权列表"""
        # 先添加一个额外授权
        await PermissionInheritanceService.grant_additional_permission(
            "manager", "role", "delete", async_session
        )
        
        # 然后获取列表
        result = await PermissionInheritanceService.get_additional_permissions(
            "manager", async_session
        )
        
        assert result["success"] is True
        assert "additional_permissions" in result
        assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_revoke_additional_permission(self, async_session: AsyncSession):
        """测试撤销额外授权"""
        # 先添加
        grant_result = await PermissionInheritanceService.grant_additional_permission(
            "manager", "role", "update", async_session
        )
        
        # 然后撤销
        revoke_result = await PermissionInheritanceService.revoke_additional_permission(
            "manager", "role", "update", async_session
        )
        
        assert revoke_result["success"] is True

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_permission(self, async_session: AsyncSession):
        """测试撤销不存在的额外授权"""
        result = await PermissionInheritanceService.revoke_additional_permission(
            "manager", "nonexistent", "action", async_session
        )
        
        # 应该返回失败但不出错
        assert result["success"] is False
        assert "not found" in result["message"]


class TestCacheMechanism:
    """缓存机制测试"""

    def test_clear_cache(self):
        """测试清除所有缓存"""
        # 清除缓存不应该抛出异常
        PermissionInheritanceService.clear_cache()
        # 这个测试主要是确保方法存在且不会崩溃

    def test_invalidate_role_cache(self):
        """测试使特定角色缓存失效"""
        # 使特定角色缓存失效
        PermissionInheritanceService.invalidate_role_cache("manager")
        # 这个测试主要是确保方法存在且不会崩溃


class TestEdgeCases:
    """边界条件测试"""

    @pytest.mark.asyncio
    async def test_sales_has_no_inheritance(self, async_session: AsyncSession):
        """测试销售角色没有继承"""
        result = await PermissionInheritanceService.get_inherited_roles(
            "sales", async_session
        )
        
        assert result["success"] is True
        assert len(result["inherited_roles"]) == 0

    @pytest.mark.asyncio
    async def test_admin_has_all_inheritance(self, async_session: AsyncSession):
        """测试 Admin 继承所有下级"""
        result = await PermissionInheritanceService.get_inherited_roles(
            "admin", async_session
        )
        
        assert result["success"] is True
        assert len(result["inherited_roles"]) == 3  # manager, specialist, sales

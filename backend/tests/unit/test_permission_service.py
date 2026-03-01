"""
Permission Service Tests - 权限服务测试

测试场景:
1. Admin 角色拥有所有权限
2. 经理角色拥有业务功能权限（除角色管理外）
3. 专员角色拥有客户管理和结算处理权限
4. 销售角色仅拥有客户查看和创建权限
5. 权限缓存功能
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.permission_service import (
    check_permission,
    get_user_permissions,
    get_available_roles,
    clear_permission_cache,
)
from app.models.user import UserRole


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture(autouse=True)
def clear_cache_before_test():
    """每个测试前清除缓存"""
    clear_permission_cache()
    yield
    clear_permission_cache()


class TestCheckPermission:
    """测试 check_permission 函数"""
    
    @pytest.mark.asyncio
    async def test_admin_has_all_permissions(self, mock_db_session):
        """Admin 角色拥有所有权限"""
        # Arrange & Act
        result = await check_permission("admin", "customer", "delete", mock_db_session)
        
        # Assert
        assert result is True
        
        # 验证缓存
        assert ("admin", "customer", "delete") in check_permission.__globals__["_permission_cache"]
    
    @pytest.mark.asyncio
    async def test_admin_all_resources_all_actions(self, mock_db_session):
        """Admin 对所有资源的所有操作都有权限"""
        resources = ["customer", "settlement", "report", "user", "role"]
        actions = ["create", "read", "update", "delete", "view", "export"]
        
        for resource in resources:
            for action in actions:
                result = await check_permission("admin", resource, action, mock_db_session)
                assert result is True, f"Admin should have {action} permission on {resource}"
    
    @pytest.mark.asyncio
    async def test_manager_customer_permissions(self, mock_db_session):
        """经理角色拥有客户管理的所有权限"""
        result = await check_permission("manager", "customer", "create", mock_db_session)
        assert result is True
        
        result = await check_permission("manager", "customer", "read", mock_db_session)
        assert result is True
        
        result = await check_permission("manager", "customer", "update", mock_db_session)
        assert result is True
        
        result = await check_permission("manager", "customer", "delete", mock_db_session)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_manager_cannot_manage_roles(self, mock_db_session):
        """经理角色无法管理角色"""
        result = await check_permission("manager", "role", "create", mock_db_session)
        assert result is False
        
        result = await check_permission("manager", "role", "delete", mock_db_session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_specialist_customer_permissions(self, mock_db_session):
        """专员角色拥有客户管理权限"""
        result = await check_permission("specialist", "customer", "create", mock_db_session)
        assert result is True
        
        result = await check_permission("specialist", "customer", "delete", mock_db_session)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_specialist_settlement_read_only(self, mock_db_session):
        """专员角色对结算只有读取权限"""
        result = await check_permission("specialist", "settlement", "read", mock_db_session)
        assert result is True
        
        result = await check_permission("specialist", "settlement", "create", mock_db_session)
        assert result is False
        
        result = await check_permission("specialist", "settlement", "delete", mock_db_session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_sales_customer_read_and_create_only(self, mock_db_session):
        """销售角色只能查看和创建客户"""
        result = await check_permission("sales", "customer", "read", mock_db_session)
        assert result is True
        
        result = await check_permission("sales", "customer", "create", mock_db_session)
        assert result is True
        
        result = await check_permission("sales", "customer", "update", mock_db_session)
        assert result is False
        
        result = await check_permission("sales", "customer", "delete", mock_db_session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_sales_no_settlement_permissions(self, mock_db_session):
        """销售角色没有结算权限"""
        result = await check_permission("sales", "settlement", "read", mock_db_session)
        assert result is False
        
        result = await check_permission("sales", "settlement", "create", mock_db_session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_invalid_role(self, mock_db_session):
        """无效角色没有权限"""
        result = await check_permission("invalid_role", "customer", "read", mock_db_session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_permission_without_session(self):
        """不提供 session 时使用静态权限矩阵"""
        result = await check_permission("manager", "customer", "delete", session=None)
        assert result is True
        
        result = await check_permission("sales", "customer", "delete", session=None)
        assert result is False


class TestGetUserPermissions:
    """测试 get_user_permissions 函数"""
    
    @pytest.mark.asyncio
    async def test_get_admin_permissions(self, mock_db_session):
        """获取 Admin 角色的所有权限"""
        permissions = await get_user_permissions("admin", mock_db_session)
        
        assert "all" in permissions
        assert permissions["all"]["all"] == ["*"]
    
    @pytest.mark.asyncio
    async def test_get_manager_permissions(self, mock_db_session):
        """获取经理角色的所有权限"""
        permissions = await get_user_permissions("manager", mock_db_session)
        
        assert "customer" in permissions
        assert "settlement" in permissions
        assert "report" in permissions
        assert "user" in permissions
        assert "role" not in permissions  # 经理没有角色管理权限
    
    @pytest.mark.asyncio
    async def test_get_sales_permissions(self, mock_db_session):
        """获取销售角色的所有权限"""
        permissions = await get_user_permissions("sales", mock_db_session)
        
        assert "customer" in permissions
        assert "create" in permissions["customer"]
        assert "read" in permissions["customer"]
        assert len(permissions) == 1  # 只有 customer 权限


class TestGetAvailableRoles:
    """测试 get_available_roles 函数"""
    
    @pytest.mark.asyncio
    async def test_get_all_roles(self):
        """获取所有可用角色"""
        roles = await get_available_roles()
        
        assert len(roles) == 4
        
        role_names = [role["role"] for role in roles]
        assert UserRole.ADMIN.value in role_names
        assert UserRole.MANAGER.value in role_names
        assert UserRole.SPECIALIST.value in role_names
        assert UserRole.SALES.value in role_names
    
    @pytest.mark.asyncio
    async def test_role_hierarchy_levels(self):
        """验证角色级别"""
        roles = await get_available_roles()
        
        admin = next(r for r in roles if r["role"] == "admin")
        manager = next(r for r in roles if r["role"] == "manager")
        specialist = next(r for r in roles if r["role"] == "specialist")
        sales = next(r for r in roles if r["role"] == "sales")
        
        assert admin["level"] == 4
        assert manager["level"] == 3
        assert specialist["level"] == 2
        assert sales["level"] == 1
    
    @pytest.mark.asyncio
    async def test_role_descriptions(self):
        """验证角色描述"""
        roles = await get_available_roles()
        
        for role in roles:
            assert "description" in role
            assert len(role["description"]) > 0


class TestPermissionCache:
    """测试权限缓存功能"""
    
    @pytest.mark.asyncio
    async def test_permission_cache_cleared(self):
        """清除权限缓存"""
        # 先调用一次以填充缓存
        await check_permission("admin", "customer", "delete", session=None)
        
        # 验证缓存已填充
        assert len(check_permission.__globals__["_permission_cache"]) > 0
        
        # 清除缓存
        clear_permission_cache()
        
        # 验证缓存已清空
        assert len(check_permission.__globals__["_permission_cache"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

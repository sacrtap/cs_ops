"""
角色管理服务测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import select
from app.services.role_management_service import RoleManagementService
from app.models.roles import Role


@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    
    # 模拟异步上下文管理器支持 for session.begin()
    mock_transaction = AsyncMock()
    mock_transaction.__aenter__ = AsyncMock()
    mock_transaction.__aexit__ = AsyncMock()
    session.begin = AsyncMock(return_value=mock_transaction)
    
    return session


@pytest.fixture
def service(mock_session):
    """创建服务实例"""
    return RoleManagementService(mock_session)


class TestRoleManagementService:
    """角色管理服务测试类"""
    
    @pytest.mark.asyncio
    async def test_get_all_roles(self, service, mock_session):
        """测试获取所有角色列表"""
        # Arrange: 设置模拟数据
        mock_roles = [
            Role(id=1, name="admin", description="管理员", status="active"),
            Role(id=2, name="manager", description="经理", status="active"),
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_roles
        mock_session.execute.return_value = mock_result
        
        # Act: 获取角色列表
        result = await service.get_all_roles()
        
        # Assert: 验证结果
        assert len(result) == 2
        assert result[0]["name"] == "admin"
        assert result[1]["name"] == "manager"
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_role_by_id(self, service, mock_session):
        """测试通过 ID 获取角色"""
        # Arrange
        mock_role = Role(id=1, name="admin", description="管理员", status="active")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_role
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await service.get_role_by_id(1)
        
        # Assert
        assert result is not None
        assert result["name"] == "admin"
    
    @pytest.mark.asyncio
    async def test_get_role_by_id_not_found(self, service, mock_session):
        """测试获取不存在的角色"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await service.get_role_by_id(999)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_role_by_name(self, service, mock_session):
        """测试通过名称获取角色"""
        # Arrange
        mock_role = Role(id=1, name="admin", description="管理员", status="active")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_role
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await service.get_role_by_name("admin")
        
        # Assert
        assert result is not None
        assert result["name"] == "admin"
    
    @pytest.mark.asyncio
    async def test_create_role(self, service, mock_session):
        """测试创建角色"""
        # Arrange
        role_data = {
            "name": "test_role",
            "description": "测试角色",
            "status": "active"
        }
        new_role = Role(id=1, **role_data)
        
        # Act
        result = await service.create_role(role_data)
        
        # Assert
        assert result["name"] == "test_role"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_role(self, service, mock_session):
        """测试更新角色"""
        # Arrange
        existing_role = Role(id=1, name="test_role", description="旧描述", status="active")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_role
        mock_session.execute.return_value = mock_result
        
        update_data = {"description": "新描述"}
        
        # Act
        result = await service.update_role(1, update_data)
        
        # Assert
        assert result["description"] == "新描述"
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_role_not_found(self, service, mock_session):
        """测试更新不存在的角色"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await service.update_role(999, {"description": "新描述"})
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_role(self, service, mock_session):
        """测试删除角色"""
        # Arrange
        role = Role(id=5, name="test_role", description="测试角色", status="active")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = role
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await service.delete_role(5)
        
        # Assert
        assert result is True
        mock_session.delete.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_system_role_raises_error(self, service, mock_session):
        """测试删除系统默认角色抛出错误"""
        # Arrange
        admin_role = Role(id=1, name="admin", description="管理员", status="active")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = admin_role
        mock_session.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(ValueError, match="无法删除系统默认角色"):
            await service.delete_role(1)
    
    @pytest.mark.asyncio
    async def test_get_role_permissions(self, service, mock_session):
        """测试获取角色权限"""
        # Arrange
        mock_role = Role(id=1, name="admin", description="管理员", status="active")
        
        # 第一次查询返回角色
        role_result = MagicMock()
        role_result.scalar_one_or_none.return_value = mock_role
        
        # 第二次查询返回权限矩阵
        from app.models.permission_matrix import PermissionMatrix
        mock_permissions = [
            PermissionMatrix(role="admin", module="customer", action="read", granted=True),
            PermissionMatrix(role="admin", module="customer", action="create", granted=True),
        ]
        perm_result = MagicMock()
        perm_result.scalars().all.return_value = mock_permissions
        
        mock_session.execute.side_effect = [role_result, perm_result]
        
        # Act
        result = await service.get_role_permissions(1)
        
        # Assert
        assert result is not None
        assert "customer" in result
        assert result["customer"]["read"] is True
    
    @pytest.mark.asyncio
    async def test_update_role_permissions(self, service, mock_session):
        """测试更新角色权限"""
        # Arrange
        mock_role = Role(id=1, name="manager", description="经理", status="active")
        role_result = MagicMock()
        role_result.scalar_one_or_none.return_value = mock_role
        mock_session.execute.return_value = role_result
        
        permissions = {
            "customer": {"read": True, "create": True},
            "settlement": {"read": False}
        }
        
        # Act
        result = await service.update_role_permissions(1, permissions)
        
        # Assert
        assert result is not None
        # 验证事务被提交（通过 transaction.commit()）
        assert mock_session.begin.called
    
    @pytest.mark.asyncio
    async def test_update_admin_role_permissions_raises_error(self, service, mock_session):
        """测试修改 Admin 角色权限抛出错误"""
        # Arrange
        admin_role = Role(id=1, name="admin", description="管理员", status="active")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = admin_role
        mock_session.execute.return_value = mock_result
        
        permissions = {"customer": {"read": True}}
        
        # Act & Assert
        with pytest.raises(ValueError, match="无法修改 Admin 角色的默认权限配置"):
            await service.update_role_permissions(1, permissions)

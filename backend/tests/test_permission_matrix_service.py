"""
权限矩阵服务测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.permission_matrix_service import PermissionMatrixService
from app.models.permission_matrix import PermissionMatrix


@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    """创建服务实例"""
    service = PermissionMatrixService(mock_session)
    # 模拟缓存对象（注意 clear 需要是 AsyncMock）
    service.cache = MagicMock()
    service.cache.get = AsyncMock(return_value=None)
    service.cache.set = AsyncMock()
    service.cache.clear = AsyncMock()  # clear 需要是 AsyncMock
    service.cache.get_stats = MagicMock(return_value={})
    return service


class TestPermissionMatrixService:
    """权限矩阵服务测试类"""
    
    @pytest.mark.asyncio
    async def test_get_role_permissions_from_cache(self, service, mock_session):
        """测试从缓存获取权限"""
        # Arrange: 设置缓存
        mock_cache = {
            "customer": {"read": True, "create": False, "update": True, "delete": False},
            "settlement": {"read": True, "create": False, "update": False, "delete": False}
        }
        service.cache.get = AsyncMock(return_value=mock_cache)
        
        # Act: 获取权限
        result = await service.get_role_permissions("sales")
        
        # Assert: 验证返回缓存数据
        assert result == mock_cache
        service.cache.get.assert_called_once_with("sales")
        mock_session.execute.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_role_permissions_from_db(self, service, mock_session):
        """测试从数据库获取权限"""
        # Arrange: 设置缓存未命中
        service.cache.get = AsyncMock(return_value=None)
        
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars().all = MagicMock(return_value=[
            PermissionMatrix(role="sales", module="customer", action="read", granted=True),
            PermissionMatrix(role="sales", module="customer", action="create", granted=False),
            PermissionMatrix(role="sales", module="settlement", action="read", granted=True),
        ])
        mock_session.execute = AsyncMock(return_value=mock_result)
        service.cache.set = AsyncMock()
        
        # Act: 获取权限
        result = await service.get_role_permissions("sales")
        
        # Assert: 验证结果
        assert result == {
            "customer": {"read": True, "create": False},
            "settlement": {"read": True}
        }
        
        # 验证缓存写入
        service.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_permission_granted(self, service):
        """测试检查权限 - 有权限"""
        # Arrange
        service.get_role_permissions = AsyncMock(return_value={
            "customer": {"read": True, "create": False}
        })
        
        # Act
        result = await service.check_permission("sales", "customer", "read")
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_permission_denied(self, service):
        """测试检查权限 - 无权限"""
        # Arrange
        service.get_role_permissions = AsyncMock(return_value={
            "customer": {"read": True, "create": False}
        })
        
        # Act
        result = await service.check_permission("sales", "customer", "create")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_permission_module_not_found(self, service):
        """测试检查权限 - 模块不存在"""
        # Arrange
        service.get_role_permissions = AsyncMock(return_value={
            "customer": {"read": True}
        })
        
        # Act
        result = await service.check_permission("sales", "nonexistent", "read")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_permission_existing(self, service, mock_session):
        """测试更新现有权限"""
        # Arrange
        mock_matrix = MagicMock()
        mock_matrix.granted = False
        
        async def mock_execute_async(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=mock_matrix)
            return mock_result
        
        mock_session.execute = mock_execute_async
        mock_session.commit = AsyncMock()
        
        # Act
        result = await service.update_permission("sales", "customer", "read", True)
        
        # Assert
        assert mock_matrix.granted is True
        await mock_session.commit()  # await 模拟 commit
        service.cache.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_cache_all(self, service):
        """测试清除所有缓存"""
        # Arrange
        service.cache.clear = AsyncMock()
        
        # Act
        await service.clear_cache()
        
        # Assert
        service.cache.clear.assert_called_once_with(None)

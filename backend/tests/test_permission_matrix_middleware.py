"""
功能权限中间件测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sanic.exceptions import HTTPException
from app.middleware.permission_matrix_middleware import (
    require_permission,
    check_permission
)


@pytest.fixture
def mock_request():
    """模拟 Sanic 请求对象"""
    request = MagicMock()
    request.ctx = MagicMock()
    request.ctx.user = MagicMock()
    request.ctx.user.id = 1
    request.ctx.user.username = "test_user"
    request.ctx.user.role = "sales"
    request.app = MagicMock()
    request.app.ctx = MagicMock()
    request.app.ctx.db_session = AsyncMock()
    return request


class TestRequirePermissionDecorator:
    """权限验证装饰器测试"""
    
    @pytest.mark.asyncio
    async def test_admin_bypass_permission_check(self, mock_request):
        """测试 Admin 绕过权限检查"""
        # Arrange
        mock_request.ctx.user.role = "admin"
        
        # 创建模拟的视图函数
        mock_view = AsyncMock(return_value=MagicMock())
        decorated = require_permission(module="settlement", action="create")(mock_view)
        
        # Act
        await decorated(mock_request)
        
        # Assert
        mock_view.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_permission_granted(self, mock_request):
        """测试有权限时允许访问"""
        # Arrange
        mock_request.ctx.user.role = "manager"
        
        with patch('app.middleware.permission_matrix_middleware.get_permission_cache') as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.get = AsyncMock(return_value={
                "customer": {"read": True, "create": True}
            })
            mock_cache_fn.return_value = mock_cache
            
            mock_view = AsyncMock(return_value=MagicMock())
            decorated = require_permission(module="customer", action="read")(mock_view)
            
            # Act
            await decorated(mock_request)
            
            # Assert
            mock_view.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_permission_denied(self, mock_request):
        """测试无权限时拒绝访问"""
        # Arrange
        mock_request.ctx.user.role = "sales"
        
        with patch('app.middleware.permission_matrix_middleware.get_permission_cache') as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.get = AsyncMock(return_value={
                "customer": {"read": True, "create": False}
            })
            mock_cache_fn.return_value = mock_cache
            
            mock_view = AsyncMock()
            decorated = require_permission(module="customer", action="create")(mock_view)
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await decorated(mock_request)
            
            assert exc_info.value.status_code == 403
            assert "没有权限" in str(exc_info.value)
            mock_view.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_unauthenticated_user(self, mock_request):
        """测试未认证用户"""
        # Arrange
        mock_request.ctx.user = None
        
        mock_view = AsyncMock()
        decorated = require_permission(module="customer", action="read")(mock_view)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await decorated(mock_request)
        
        assert exc_info.value.status == 401
        assert "未认证" in exc_info.value.message
        mock_view.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_miss_falls_back_to_db(self, mock_request):
        """测试缓存未命中时从数据库查询"""
        # Arrange
        mock_request.ctx.user.role = "manager"
        
        with patch('app.middleware.permission_matrix_middleware.get_permission_cache') as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.get = AsyncMock(return_value=None)  # 缓存未命中
            mock_cache_fn.return_value = mock_cache
            
            with patch('app.middleware.permission_matrix_middleware.PermissionMatrixService') as mock_service_cls:
                mock_service = MagicMock()
                mock_service.check_permission = AsyncMock(return_value=True)
                mock_service_cls.return_value = mock_service
                mock_service.get_role_permissions = AsyncMock(return_value={
                    "customer": {"read": True}
                })
                
                mock_view = AsyncMock(return_value=MagicMock())
                decorated = require_permission(module="customer", action="read")(mock_view)
                
                # Act
                await decorated(mock_request)
                
                # Assert
                mock_service.check_permission.assert_called_once()
                mock_cache.set.assert_called_once()
                mock_view.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_permission_denied_logs_warning(self, mock_request, caplog):
        """测试权限拒绝时记录日志"""
        # Arrange
        mock_request.ctx.user.role = "sales"
        mock_request.path = "/api/v1/settlement"
        
        with patch('app.middleware.permission_matrix_middleware.get_permission_cache') as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.get = AsyncMock(return_value={
                "settlement": {"create": False}
            })
            mock_cache_fn.return_value = mock_cache
            
            mock_view = AsyncMock()
            decorated = require_permission(module="settlement", action="create")(mock_view)
            
            # Act & Assert
            with pytest.raises(HTTPException):
                with caplog.at_level("WARNING"):
                    await decorated(mock_request)
            
            # 验证日志记录
            assert "Permission denied" in caplog.text
            assert "sales" in caplog.text
            assert "settlement" in caplog.text


class TestCheckPermissionFunction:
    """check_permission 函数测试"""
    
    @pytest.mark.asyncio
    async def test_check_permission_with_cache(self, mock_request):
        """测试有缓存时的权限检查"""
        # Arrange
        with patch('app.middleware.permission_matrix_middleware.get_permission_cache') as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.get = AsyncMock(return_value={
                "customer": {"read": True, "create": False}
            })
            mock_cache_fn.return_value = mock_cache
            
            # Act
            result = await check_permission(mock_request, "customer", "read")
            
            # Assert
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_permission_without_cache(self, mock_request):
        """测试无缓存时的权限检查"""
        # Arrange
        with patch('app.middleware.permission_matrix_middleware.get_permission_cache') as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache_fn.return_value = mock_cache
            
            with patch('app.middleware.permission_matrix_middleware.PermissionMatrixService') as mock_service_cls:
                mock_service = MagicMock()
                mock_service.check_permission = AsyncMock(return_value=False)
                mock_service_cls.return_value = mock_service
                
                # Act
                result = await check_permission(mock_request, "customer", "read")
                
                # Assert
                assert result is False
                mock_service.check_permission.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_permission_unauthenticated(self, mock_request):
        """测试未认证用户"""
        # Arrange
        mock_request.ctx.user = None
        
        # Act
        result = await check_permission(mock_request, "customer", "read")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_permission_admin_always_true(self, mock_request):
        """测试 Admin 总是有权限"""
        # Arrange
        mock_request.ctx.user.role = "admin"
        
        # Act
        result = await check_permission(mock_request, "any_module", "any_action")
        
        # Assert
        assert result is True

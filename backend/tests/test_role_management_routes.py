"""
角色管理路由测试
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from sanic import Sanic
from app.routes.role_management_routes import role_management_bp


@pytest.fixture
def app():
    """创建 Sanic 应用"""
    import uuid
    app_name = f"test_role_management_{uuid.uuid4()}"
    sanic_app = Sanic(app_name)
    sanic_app.blueprint(role_management_bp)
    sanic_app.ctx.db_session = AsyncMock()
    return sanic_app


@pytest.fixture
def mock_auth_middleware():
    """模拟认证中间件"""
    with patch('app.middleware.auth_middleware.AuthMiddleware.require_auth') as mock:
        mock.return_value = lambda f: f
        yield mock


@pytest.fixture
def mock_permission_middleware():
    """模拟权限中间件"""
    with patch('app.middleware.permission_matrix_middleware.require_permission') as mock:
        mock.return_value = lambda f: f
        yield mock


class TestRoleManagementRoutes:
    """角色管理路由测试类"""
    
    @pytest.mark.asyncio
    async def test_get_roles(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试获取角色列表"""
        # Arrange
        mock_roles = [
            {"id": 1, "name": "admin", "description": "管理员", "status": "active"},
            {"id": 2, "name": "manager", "description": "经理", "status": "active"},
        ]
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_all_roles = AsyncMock(return_value=mock_roles)
            MockService.return_value = mock_service
            
            # 确保中间件被正确 mock
            mock_auth_middleware.start()
            mock_permission_middleware.start()
            
            # Act
            request, response = await app.asgi_client.get("/api/v1/roles", headers={"Authorization": "Bearer test_token"})
            
            # 停止 mock
            mock_auth_middleware.stop()
            mock_permission_middleware.stop()
            
            # Assert
            assert response.status == 200
            data = response.json
            assert "data" in data
            assert len(data["data"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_role_by_id(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试通过 ID 获取角色"""
        # Arrange
        mock_role = {"id": 1, "name": "admin", "description": "管理员", "status": "active"}
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_role_by_id = AsyncMock(return_value=mock_role)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.get("/api/v1/roles/1")
            
            # Assert
            assert response.status == 200
            data = response.json
            assert data["data"]["name"] == "admin"
    
    @pytest.mark.asyncio
    async def test_get_role_not_found(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试获取不存在的角色"""
        # Arrange
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_role_by_id = AsyncMock(return_value=None)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.get("/api/v1/roles/999")
            
            # Assert
            assert response.status == 404
            data = response.json
            assert "ROLE_NOT_FOUND" in data.get("code", "")
    
    @pytest.mark.asyncio
    async def test_create_role(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试创建角色"""
        # Arrange
        new_role = {"id": 5, "name": "test_role", "description": "测试角色", "status": "active"}
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_role_by_name = AsyncMock(return_value=None)
            mock_service.create_role = AsyncMock(return_value=new_role)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.post(
                "/api/v1/roles",
                json={"name": "test_role", "description": "测试角色"}
            )
            
            # Assert
            assert response.status == 200
            data = response.json
            assert data["data"]["name"] == "test_role"
    
    @pytest.mark.asyncio
    async def test_create_duplicate_role(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试创建重复角色"""
        # Arrange
        existing_role = {"id": 1, "name": "test_role", "description": "已存在角色"}
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_role_by_name = AsyncMock(return_value=existing_role)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.post(
                "/api/v1/roles",
                json={"name": "test_role", "description": "测试角色"}
            )
            
            # Assert
            assert response.status == 409
            data = response.json
            assert "ROLE_ALREADY_EXISTS" in data.get("code", "")
    
    @pytest.mark.asyncio
    async def test_update_role(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试更新角色"""
        # Arrange
        updated_role = {"id": 1, "name": "admin", "description": "更新后的描述", "status": "active"}
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.update_role = AsyncMock(return_value=updated_role)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.put(
                "/api/v1/roles/1",
                json={"description": "更新后的描述"}
            )
            
            # Assert
            assert response.status == 200
            data = response.json
            assert data["data"]["description"] == "更新后的描述"
    
    @pytest.mark.asyncio
    async def test_delete_role(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试删除角色"""
        # Arrange
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.delete_role = AsyncMock(return_value=True)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.delete("/api/v1/roles/5")
            
            # Assert
            assert response.status == 200
            data = response.json
            assert data["data"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_delete_system_role(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试删除系统默认角色"""
        # Arrange
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.delete_role = AsyncMock(side_effect=ValueError("无法删除系统默认角色"))
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.delete("/api/v1/roles/1")
            
            # Assert
            assert response.status == 400
            data = response.json
            assert "无法删除系统默认角色" in data.get("message", "")
    
    @pytest.mark.asyncio
    async def test_get_role_permissions(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试获取角色权限"""
        # Arrange
        mock_permissions = {
            "customer": {"read": True, "create": True},
            "settlement": {"read": False}
        }
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_role_permissions = AsyncMock(return_value=mock_permissions)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.get("/api/v1/roles/1/permissions")
            
            # Assert
            assert response.status == 200
            data = response.json
            assert "data" in data
            assert "customer" in data["data"]
    
    @pytest.mark.asyncio
    async def test_update_role_permissions(self, app, mock_auth_middleware, mock_permission_middleware):
        """测试更新角色权限"""
        # Arrange
        updated_role = {"id": 1, "name": "manager", "description": "经理", "status": "active"}
        
        with patch('app.routes.role_management_routes.RoleManagementService') as MockService:
            mock_service = AsyncMock()
            mock_service.update_role_permissions = AsyncMock(return_value=updated_role)
            MockService.return_value = mock_service
            
            # Act
            request, response = await app.asgi_client.put(
                "/api/v1/roles/1/permissions",
                json={"permissions": {"customer": {"read": True}}}
            )
            
            # Assert
            assert response.status == 200
            data = response.json
            assert data["message"] == "角色权限更新成功"

"""
示例 API 测试 - 客户管理模块

演示 pytest 测试模式：
1. 异步测试支持
2. fixture 使用
3. 参数化测试
4. Given-When-Then 结构
"""

import pytest
from httpx import AsyncClient


class TestCustomerAPI:
    """客户管理 API 测试类"""
    
    @pytest.mark.asyncio
    async def test_get_customer_list(self, authenticated_client, pagination_params):
        """
        测试获取客户列表
        
        Given: 认证客户端和分页参数
        When: 发送 GET 请求到 /api/v1/customers
        Then: 返回客户列表和分页信息
        """
        # When
        response = await authenticated_client.get(
            "/api/v1/customers",
            params=pagination_params,
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        
        assert isinstance(data["items"], list)
        assert data["page"] == pagination_params["page"]
        assert data["page_size"] == pagination_params["page_size"]
    
    @pytest.mark.asyncio
    async def test_create_customer(self, authenticated_client, customer_factory):
        """
        测试创建客户
        
        Given: 认证客户端和客户数据工厂
        When: 发送 POST 请求创建新客户
        Then: 返回创建的客户信息和状态码 201
        """
        # Given
        customer_data = customer_factory.create()
        
        # When
        response = await authenticated_client.post(
            "/api/v1/customers",
            json=customer_data,
        )
        
        # Then
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["name"] == customer_data["name"]
        assert data["email"] == customer_data["email"]
        assert data["phone"] == customer_data["phone"]
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_get_customer_by_id(
        self, authenticated_client, db_session, customer_factory
    ):
        """
        测试获取单个客户
        
        Given: 数据库中已有一个客户
        When: 发送 GET 请求获取该客户
        Then: 返回客户详细信息
        """
        # Given
        customer = await customer_factory.create_in_db(db_session)
        
        # When
        response = await authenticated_client.get(
            f"/api/v1/customers/{customer.id}"
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(customer.id)
        assert data["name"] == customer.name
        assert data["email"] == customer.email
    
    @pytest.mark.asyncio
    async def test_update_customer(
        self, authenticated_client, db_session, customer_factory
    ):
        """
        测试更新客户
        
        Given: 数据库中已有一个客户
        When: 发送 PUT 请求更新客户信息
        Then: 返回更新后的客户信息
        """
        # Given
        customer = await customer_factory.create_in_db(db_session)
        update_data = {"email": "updated@example.com"}
        
        # When
        response = await authenticated_client.put(
            f"/api/v1/customers/{customer.id}",
            json=update_data,
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == update_data["email"]
    
    @pytest.mark.asyncio
    async def test_delete_customer(
        self, authenticated_client, db_session, customer_factory
    ):
        """
        测试删除客户
        
        Given: 数据库中已有一个客户
        When: 发送 DELETE 请求删除该客户
        Then: 返回状态码 204，客户不再存在
        """
        # Given
        customer = await customer_factory.create_in_db(db_session)
        
        # When
        response = await authenticated_client.delete(
            f"/api/v1/customers/{customer.id}"
        )
        
        # Then
        assert response.status_code == 204
        
        # Verify customer is deleted
        get_response = await authenticated_client.get(
            f"/api/v1/customers/{customer.id}"
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_data,expected_error",
        [
            ({"name": "", "email": "test@example.com"}, "name 不能为空"),
            ({"name": "Test", "email": "invalid-email"}, "邮箱格式无效"),
            ({"name": "Test", "email": "test@example.com", "phone": "invalid"}, "电话格式无效"),
        ],
    )
    async def test_create_customer_validation_errors(
        self, authenticated_client, invalid_data, expected_error
    ):
        """
        测试客户创建验证错误
        
        Given: 无效的客戶数据
        When: 发送 POST 请求创建客户
        Then: 返回 422 验证错误
        """
        # When
        response = await authenticated_client.post(
            "/api/v1/customers",
            json=invalid_data,
        )
        
        # Then
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        assert expected_error in str(data["detail"])
    
    @pytest.mark.asyncio
    async def test_bulk_import_customers(
        self, authenticated_client, tmp_path
    ):
        """
        测试批量导入客户
        
        Given: Excel 文件包含客户数据
        When: 发送 POST 请求上传文件
        Then: 返回导入结果摘要
        """
        # Given: 创建测试 Excel 文件
        import pandas as pd
        
        test_data = {
            "name": ["客户 A", "客户 B", "客户 C"],
            "email": ["a@example.com", "b@example.com", "c@example.com"],
            "phone": ["13800138001", "13800138002", "13800138003"],
        }
        df = pd.DataFrame(test_data)
        
        excel_file = tmp_path / "customers.xlsx"
        df.to_excel(excel_file, index=False)
        
        # When
        with open(excel_file, "rb") as f:
            response = await authenticated_client.post(
                "/api/v1/customers/bulk-import",
                files={"file": f},
            )
        
        # Then
        assert response.status_code == 202  # 异步任务
        data = response.json()
        
        assert "task_id" in data
        assert "status" in data


class TestCustomerHealthAPI:
    """客户健康度监控 API 测试"""
    
    @pytest.mark.asyncio
    async def test_get_customer_health_status(
        self, authenticated_client, db_session, customer_factory
    ):
        """
        测试获取客户健康状态
        
        Given: 数据库中已有一个客户
        When: 发送 GET 请求获取健康状态
        Then: 返回健康度评分和预警信息
        """
        # Given
        customer = await customer_factory.create_in_db(db_session)
        
        # When
        response = await authenticated_client.get(
            f"/api/v1/customers/{customer.id}/health"
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        
        assert "health_score" in data
        assert "risk_level" in data
        assert "warnings" in data
        assert isinstance(data["warnings"], list)


# ===========================================
# 集成测试示例
# ===========================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_customer_billing_integration(
    authenticated_client, db_session, customer_factory
):
    """
    客户 - 结算集成测试
    
    Given: 数据库中已有客户和结算记录
    When: 获取客户结算汇总
    Then: 返回正确的汇总数据
    """
    # Given
    customer = await customer_factory.create_in_db(db_session)
    
    # When
    response = await authenticated_client.get(
        f"/api/v1/customers/{customer.id}/billing-summary"
    )
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert "customer_id" in data
    assert "total_amount" in data
    assert "paid_amount" in data
    assert "outstanding_amount" in data

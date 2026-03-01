"""
数据权限 E2E 测试 - Story 1.4

测试数据权限的端到端用户流程

TDD Phase: RED (所有测试初始为跳过状态)
生成日期：2026-03-01

网络优先模式 (Network-First): 路由拦截在导航之前
"""

import pytest
from playwright.sync_api import Page, expect, APIResponse
from typing import Dict, Any


# ============================================================================
# AC1: 销售用户数据隔离 - E2E 测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_sales_user_sees_only_own_customers_in_ui(page: Page, login_as_sales: Dict[str, Any]):
    """
    AC1: 销售用户登录后查看自己的客户
    
    Given 销售用户已登录 (role='sales', org_id=5, sales_rep_id=1)
    When 导航到客户列表页面
    Then 仅显示自己负责的客户
    And 看不到其他销售的客户
    """
    # Arrange: 使用夹具登录销售用户
    user = login_as_sales  # {id: 1, role: 'sales', org_id: 5}
    
    # Act: 拦截客户列表 API 请求（网络优先模式）
    page.route("**/api/v1/customers", lambda route: route.continue_())
    page.goto("/customers")
    
    # Assert: 验证页面仅显示自己的客户
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).to_have_count(3)  # 假设销售用户有 3 个客户
    
    # 验证每个客户的销售代表都是自己
    for i in range(3):
        sales_rep = page.locator(f"[data-testid='customer-row-{i}-sales-rep']")
        expect(sales_rep).to_contain_text("销售用户 1")


@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_sales_user_cannot_view_other_customer_detail(page: Page, login_as_sales: Dict[str, Any]):
    """
    AC1: 销售用户尝试访问其他销售的客户详情
    
    Given 销售用户已登录
    When 尝试访问其他销售的客户详情页（通过 URL）
    Then 显示权限错误提示
    And 无法查看客户详情
    """
    # Arrange
    user = login_as_sales
    
    # Act: 尝试访问其他销售的客户（ID=999）
    page.route(
        "**/api/v1/customers/999",
        lambda route: route.fulfill(
            status=403,
            json={
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": "您没有权限查看此客户"
                }
            }
        )
    )
    page.goto("/customers/999")
    
    # Assert: 显示权限错误
    error_message = page.locator("[data-testid='permission-error']")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("您没有权限查看此客户")
    
    # 客户详情不应该显示
    customer_detail = page.locator("[data-testid='customer-detail']")
    expect(customer_detail).not_to_be_visible()


# ============================================================================
# AC2: 经理查看本组织数据 - E2E 测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_manager_sees_all_org_customers(page: Page, login_as_manager: Dict[str, Any]):
    """
    AC2: 经理查看本组织所有客户
    
    Given 经理用户已登录 (role='manager', org_id=5)
    When 导航到客户列表页面
    Then 显示本组织所有客户（包括下属销售的客户）
    And 可以看到客户负责人信息
    """
    # Arrange
    user = login_as_manager  # {id: 10, role: 'manager', org_id: 5}
    
    # Act
    page.route("**/api/v1/customers", lambda route: route.continue_())
    page.goto("/customers")
    
    # Assert
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).to_have_count(15)  # 假设本组织有 15 个客户
    
    # 验证可以看到客户负责人
    for i in range(15):
        sales_rep = page.locator(f"[data-testid='customer-row-{i}-sales-rep']")
        expect(sales_rep).to_be_visible()  # 应该显示负责人信息


@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_manager_cannot_access_other_org(page: Page, login_as_manager: Dict[str, Any]):
    """
    AC2: 经理无法访问其他组织数据
    
    Given 经理用户已登录 (org_id=5)
    When 尝试访问 org_id=6 的客户
    Then 看不到其他组织的客户
    """
    # Arrange
    user = login_as_manager
    
    # Act
    page.route("**/api/v1/customers", lambda route: route.continue_())
    page.goto("/customers")
    
    # Assert: 不应该出现其他组织的客户
    all_org_ids = page.locator("[data-testid='customer-org-id']")
    for org_id_element in all_org_ids.all():
        org_id = org_id_element.inner_text()
        assert org_id == "5", f"不应该显示其他组织的客户，发现 org_id={org_id}"


# ============================================================================
# AC3: Admin 全系统数据访问 - E2E 测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_admin_sees_all_system_customers(page: Page, login_as_admin: Dict[str, Any]):
    """
    AC3: Admin 查看全系统所有客户
    
    Given Admin 用户已登录
    When 导航到客户列表页面
    Then 显示全系统所有客户
    And 可以看到所有组织和负责人信息
    """
    # Arrange
    user = login_as_admin  # {id: 999, role: 'admin'}
    
    # Act
    page.route("**/api/v1/customers", lambda route: route.continue_())
    page.goto("/customers")
    
    # Assert
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).to_have_count(50)  # 假设全系统有 50 个客户
    
    # 验证可以看到所有组织
    org_filter = page.locator("[data-testid='org-filter']")
    expect(org_filter).to_be_visible()  # Admin 应该能看到组织筛选器


@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_admin_can_filter_by_any_org_or_sales(page: Page, login_as_admin: Dict[str, Any]):
    """
    AC3: Admin 可以筛选任意销售或组织的客户
    
    Given Admin 用户已登录
    When 使用组织或销售筛选器
    Then 可以查看任意筛选结果
    """
    # Arrange
    user = login_as_admin
    
    # Act: 筛选特定组织
    page.route("**/api/v1/customers*", lambda route: route.continue_())
    page.goto("/customers")
    
    org_select = page.locator("[data-testid='org-select']")
    org_select.select_option("6")  # 选择组织 6
    
    # Assert
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).to_have_count(10)  # 组织 6 有 10 个客户


# ============================================================================
# AC4: 数据权限自动过滤 - E2E 测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_data_permission_filter_applied_automatically(page: Page, login_as_sales: Dict[str, Any]):
    """
    AC4: 数据权限自动过滤
    
    Given 销售用户已登录
    When 访问任何客户相关页面
    Then 数据权限自动应用（用户无需手动筛选）
    """
    # Arrange
    user = login_as_sales
    
    # Act: 直接访问客户列表，无需任何筛选操作
    page.route("**/api/v1/customers", lambda route: route.continue_())
    page.goto("/customers")
    
    # Assert: 自动显示过滤后的数据
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).to_have_count(3)  # 自动显示自己的客户
    
    # 验证没有"筛选"提示 - 因为过滤是自动的
    filter_notice = page.locator("[data-testid='filter-notice']")
    expect(filter_notice).not_to_be_visible()


@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_data_permission_works_across_all_pages(page: Page, login_as_sales: Dict[str, Any]):
    """
    AC4: 数据权限在所有页面一致应用
    
    Given 销售用户已登录
    When 访问不同页面（列表、详情、报表）
    Then 数据权限一致应用
    """
    # Arrange
    user = login_as_sales
    
    # Act & Assert: 客户列表页
    page.route("**/api/v1/customers", lambda route: route.continue_())
    page.goto("/customers")
    expect(page.locator("[data-testid='customer-row']")).to_have_count(3)
    
    # 客户统计报表页
    page.route("**/api/v1/customers/stats", lambda route: route.continue_())
    page.goto("/customers/stats")
    stats_customer_count = page.locator("[data-testid='total-customers']")
    expect(stats_customer_count).to_contain_text("3")  # 统计也应该只包含自己的客户


# ============================================================================
# AC5: 越权访问阻止 - E2E 测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_unauthorized_access_shows_friendly_error(page: Page, login_as_sales: Dict[str, Any]):
    """
    AC5: 越权访问显示友好错误
    
    Given 销售用户已登录
    When 尝试访问其他销售的客户详情
    Then 显示友好的错误消息
    And 提供返回按钮
    """
    # Arrange
    user = login_as_sales
    
    # Act
    page.route(
        "**/api/v1/customers/999",
        lambda route: route.fulfill(
            status=403,
            json={
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": "您没有权限查看此客户"
                }
            }
        )
    )
    page.goto("/customers/999")
    
    # Assert: 错误消息友好
    error_title = page.locator("[data-testid='error-title']")
    expect(error_title).to_contain_text("权限不足")
    
    error_message = page.locator("[data-testid='error-message']")
    expect(error_message).to_contain_text("您没有权限查看此客户")
    
    # 提供返回按钮
    back_button = page.locator("[data-testid='back-button']")
    expect(back_button).to_be_visible()


@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_unauthorized_access_logged_to_audit(page: Page, login_as_sales: Dict[str, Any]):
    """
    AC5: 越权访问记录审计日志
    
    Given 销售用户已登录
    When 尝试越权访问
    Then 后端记录审计日志
    And 用户看到错误提示
    """
    # Arrange
    user = login_as_sales
    
    # Act: 监听审计日志 API 调用
    audit_request = []
    page.route("**/api/v1/audit-logs", lambda route: audit_request.append(route.request))
    
    page.route(
        "**/api/v1/customers/999",
        lambda route: route.fulfill(status=403)
    )
    page.goto("/customers/999")
    
    # Assert: 应该触发审计日志记录
    # TODO: 验证审计日志 API 被调用
    # assert len(audit_request) > 0, "应该记录审计日志"


# ============================================================================
# 边缘情况测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_data_permission_with_no_customers(page: Page, login_as_sales: Dict[str, Any]):
    """
    边缘情况：销售用户没有任何客户
    
    Given 销售用户已登录但没有分配客户
    When 访问客户列表
    Then 显示空状态提示
    """
    # Arrange
    user = login_as_sales  # 该销售没有客户
    
    # Act
    page.route(
        "**/api/v1/customers",
        lambda route: route.fulfill(
            status=200,
            json={"data": [], "meta": {"total": 0}}
        )
    )
    page.goto("/customers")
    
    # Assert: 显示空状态
    empty_state = page.locator("[data-testid='empty-state']")
    expect(empty_state).to_be_visible()
    expect(empty_state).to_contain_text("暂无客户")


@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_data_permission_with_network_error(page: Page, login_as_sales: Dict[str, Any]):
    """
    边缘情况：网络错误时的数据权限
    
    Given 销售用户已登录
    When 客户列表 API 请求失败
    Then 显示错误提示
    And 不显示任何客户数据
    """
    # Arrange
    user = login_as_sales
    
    # Act: 模拟网络错误
    page.route("**/api/v1/customers", lambda route: route.abort())
    page.goto("/customers")
    
    # Assert: 显示网络错误
    error_message = page.locator("[data-testid='network-error']")
    expect(error_message).to_be_visible()
    
    # 不显示客户数据
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).to_have_count(0)


# ============================================================================
# 性能测试
# ============================================================================

@pytest.mark.skip(reason="RED phase: 等待数据权限实现")
def test_data_permission_filter_performance(page: Page, login_as_sales: Dict[str, Any]):
    """
    性能测试：大数据集下的过滤性能
    
    Given 销售用户有大量客户数据
    When 加载客户列表
    Then 页面加载时间可接受（< 2 秒）
    """
    # Arrange
    user = login_as_sales
    
    # Act: 记录加载时间
    page.route("**/api/v1/customers", lambda route: route.continue_())
    
    start_time = page.evaluate("Date.now()")
    page.goto("/customers")
    page.wait_for_load_state("networkidle")
    end_time = page.evaluate("Date.now()")
    
    load_time = end_time - start_time
    
    # Assert
    customer_rows = page.locator("[data-testid='customer-row']")
    expect(customer_rows).not_to_have_count(0)
    assert load_time < 2000, f"加载时间应该< 2 秒，实际{load_time}ms"

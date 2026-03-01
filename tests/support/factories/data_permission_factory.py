"""
数据权限测试数据工厂

使用 Faker 生成随机但真实的测试数据

生成日期：2026-03-01
"""

from typing import Dict, Any, List, Optional
from faker import Faker
import random

fake = Faker('zh_CN')  # 使用中文数据


# ============================================================================
# 用户工厂
# ============================================================================

def create_user(
    role: str = "sales",
    org_id: Optional[int] = None,
    **overrides
) -> Dict[str, Any]:
    """
    创建用户数据
    
    Args:
        role: 用户角色 (admin, manager, specialist, sales)
        org_id: 组织 ID
        **overrides: 自定义覆盖字段
        
    Returns:
        用户数据字典
    """
    base_user = {
        "id": fake.unique_id(),
        "username": fake.user_name(),
        "email": fake.email(),
        "role": role,
        "org_id": org_id if org_id is not None else fake.random_int(min=1, max=100),
        "created_at": fake.iso8601(),
    }
    
    # 应用覆盖
    base_user.update(overrides)
    
    return base_user


def create_sales_user(org_id: int = 5, **overrides) -> Dict[str, Any]:
    """创建销售用户"""
    return create_user(role="sales", org_id=org_id, **overrides)


def create_manager_user(org_id: int = 5, **overrides) -> Dict[str, Any]:
    """创建经理用户"""
    return create_user(role="manager", org_id=org_id, **overrides)


def create_admin_user(**overrides) -> Dict[str, Any]:
    """创建 Admin 用户"""
    return create_user(role="admin", org_id=None, **overrides)


def create_users(count: int = 5, **overrides) -> List[Dict[str, Any]]:
    """创建多个用户"""
    return [create_user(**overrides) for _ in range(count)]


# ============================================================================
# 组织工厂
# ============================================================================

def create_organization(
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
    **overrides
) -> Dict[str, Any]:
    """
    创建组织数据
    
    Args:
        name: 组织名称
        parent_id: 父组织 ID
        **overrides: 自定义覆盖字段
        
    Returns:
        组织数据字典
    """
    base_org = {
        "id": fake.unique_id(),
        "name": name if name else fake.company(),
        "parent_id": parent_id,
        "created_at": fake.iso8601(),
    }
    
    base_org.update(overrides)
    
    return base_org


def create_organizations(count: int = 5, **overrides) -> List[Dict[str, Any]]:
    """创建多个组织"""
    return [create_organization(**overrides) for _ in range(count)]


# ============================================================================
# 客户工厂
# ============================================================================

def create_customer(
    sales_rep_id: Optional[int] = None,
    org_id: Optional[int] = None,
    **overrides
) -> Dict[str, Any]:
    """
    创建客户数据
    
    Args:
        sales_rep_id: 销售代表 ID
        org_id: 组织 ID
        **overrides: 自定义覆盖字段
        
    Returns:
        客户数据字典
    """
    base_customer = {
        "id": fake.unique_id(),
        "name": fake.company(),
        "contact_name": fake.name(),
        "contact_email": fake.email(),
        "contact_phone": fake.phone_number(),
        "address": fake.address(),
        "sales_rep_id": sales_rep_id if sales_rep_id is not None else fake.random_int(min=1, max=100),
        "org_id": org_id if org_id is not None else fake.random_int(min=1, max=100),
        "status": random.choice(["active", "inactive", "lead"]),
        "created_at": fake.iso8601(),
        "updated_at": fake.iso8601(),
    }
    
    base_customer.update(overrides)
    
    return base_customer


def create_customers(count: int = 10, **overrides) -> List[Dict[str, Any]]:
    """创建多个客户"""
    return [create_customer(**overrides) for _ in range(count)]


def create_customer_for_sales(sales_rep_id: int, **overrides) -> Dict[str, Any]:
    """创建指定销售代表的客户"""
    return create_customer(sales_rep_id=sales_rep_id, **overrides)


def create_customer_for_org(org_id: int, **overrides) -> Dict[str, Any]:
    """创建指定组织的客户"""
    return create_customer(org_id=org_id, **overrides)


# ============================================================================
# 测试场景工厂
# ============================================================================

def create_test_scenario_sales_with_customers(
    customer_count: int = 3
) -> Dict[str, Any]:
    """
    创建销售用户及其客户的测试场景
    
    Returns:
        包含用户和客户的场景数据
    """
    sales_user = create_sales_user()
    customers = [
        create_customer_for_sales(sales_rep_id=sales_user["id"])
        for _ in range(customer_count)
    ]
    
    return {
        "user": sales_user,
        "customers": customers,
        "expected_count": customer_count,
    }


def create_test_scenario_manager_with_org(
    sales_count: int = 3,
    customers_per_sales: int = 5
) -> Dict[str, Any]:
    """
    创建经理及其组织下销售的测试场景
    
    Returns:
        包含经理、销售和客户的场景数据
    """
    org_id = 5
    manager_user = create_manager_user(org_id=org_id)
    
    sales_users = [
        create_sales_user(org_id=org_id)
        for _ in range(sales_count)
    ]
    
    customers = []
    for sales_user in sales_users:
        customers.extend([
            create_customer_for_sales(
                sales_rep_id=sales_user["id"],
                org_id=org_id
            )
            for _ in range(customers_per_sales)
        ])
    
    return {
        "user": manager_user,
        "sales_users": sales_users,
        "customers": customers,
        "expected_count": sales_count * customers_per_sales,
    }


def create_test_scenario_admin_full_access(
    org_count: int = 3,
    customers_per_org: int = 5
) -> Dict[str, Any]:
    """
    创建 Admin 全系统访问的测试场景
    
    Returns:
        包含 Admin 和全系统客户的场景数据
    """
    admin_user = create_admin_user()
    
    organizations = create_organizations(org_count)
    
    customers = []
    for org in organizations:
        customers.extend([
            create_customer_for_org(org_id=org["id"])
            for _ in range(customers_per_org)
        ])
    
    return {
        "user": admin_user,
        "organizations": organizations,
        "customers": customers,
        "expected_count": org_count * customers_per_org,
    }


# ============================================================================
# 数据生成示例
# ============================================================================

if __name__ == "__main__":
    # 示例：创建一个销售用户及其客户
    scenario = create_test_scenario_sales_with_customers(3)
    print(f"销售用户：{scenario['user']['username']}")
    print(f"客户数量：{len(scenario['customers'])}")
    
    # 示例：创建经理场景
    manager_scenario = create_test_scenario_manager_with_org(3, 5)
    print(f"\n经理用户：{manager_scenario['user']['username']}")
    print(f"组织客户总数：{len(manager_scenario['customers'])}")

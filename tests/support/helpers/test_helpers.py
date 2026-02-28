"""
测试辅助函数 - 内部运营中台客户信息管理与运营系统

包含：
1. API 测试辅助
2. 数据生成辅助
3. 断言辅助
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from faker import Faker

fake = Faker('zh_CN')


# ===========================================
# 数据生成辅助函数
# ===========================================

def generate_customer_data(count: int = 1, overrides: Optional[Dict] = None) -> List[Dict]:
    """
    生成批量客户测试数据
    
    Args:
        count: 生成客户数量
        overrides: 覆盖默认值的字段
    
    Returns:
        客户数据列表
    """
    customers = []
    
    for _ in range(count):
        customer = {
            "name": fake.company(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "contact_person": fake.name(),
            "status": fake.random_element(["active", "inactive", "suspended"]),
            "credit_limit": fake.random_int(10000, 1000000),
            "created_at": fake.date_time_this_year().isoformat(),
        }
        
        if overrides:
            customer.update(overrides)
        
        customers.append(customer)
    
    return customers


def generate_billing_data(
    customer_id: str,
    amount: float,
    billing_type: str = "service",
) -> Dict[str, Any]:
    """
    生成结算测试数据
    
    Args:
        customer_id: 客户 ID
        amount: 结算金额
        billing_type: 结算类型
    
    Returns:
        结算数据字典
    """
    return {
        "customer_id": customer_id,
        "amount": amount,
        "type": billing_type,
        "status": "pending",
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "items": [
            {
                "description": f"服务项目 {_}",
                "quantity": 1,
                "unit_price": amount,
                "total": amount,
            }
            for _ in range(fake.random_int(1, 5))
        ],
    }


def generate_date_range(
    days: int = 30,
    start_date: Optional[datetime] = None,
) -> Dict[str, str]:
    """
    生成日期范围
    
    Args:
        days: 天数
        start_date: 起始日期
    
    Returns:
        包含 start_date 和 end_date 的字典
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=days // 2)
    
    end_date = start_date + timedelta(days=days)
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


# ===========================================
# 断言辅助函数
# ===========================================

def assert_response_structure(
    response_data: Dict,
    required_fields: List[str],
    optional_fields: Optional[List[str]] = None,
) -> None:
    """
    断言响应数据结构
    
    Args:
        response_data: 响应数据
        required_fields: 必需字段列表
        optional_fields: 可选字段列表
    """
    for field in required_fields:
        assert field in response_data, f"缺少必需字段：{field}"
    
    if optional_fields:
        # 可选字段不强制检查
        pass


def assert_pagination_structure(
    response_data: Dict,
    expected_page: int = 1,
    expected_page_size: int = 20,
) -> None:
    """
    断言分页响应结构
    
    Args:
        response_data: 响应数据
        expected_page: 期望页码
        expected_page_size: 期望每页大小
    """
    assert "items" in response_data
    assert "total" in response_data
    assert "page" in response_data
    assert "page_size" in response_data
    assert "total_pages" in response_data
    
    assert isinstance(response_data["items"], list)
    assert response_data["page"] == expected_page
    assert response_data["page_size"] == expected_page_size
    assert response_data["total"] >= 0


def assert_error_response(
    response_data: Dict,
    expected_status: int,
    expected_error_contains: Optional[str] = None,
) -> None:
    """
    断言错误响应
    
    Args:
        response_data: 响应数据
        expected_status: 期望状态码
        expected_error_contains: 错误消息应包含的内容
    """
    assert "error" in response_data or "detail" in response_data
    assert response_data.get("status") == expected_status
    
    if expected_error_contains:
        error_msg = response_data.get("error", "") or response_data.get("detail", "")
        assert expected_error_contains in error_msg


# ===========================================
# 异步测试辅助
# ===========================================

async def wait_for_condition(
    condition_func,
    timeout: float = 5.0,
    poll_interval: float = 0.1,
) -> bool:
    """
    等待条件满足
    
    Args:
        condition_func: 条件函数（返回 bool）
        timeout: 超时时间（秒）
        poll_interval: 轮询间隔（秒）
    
    Returns:
        条件是否满足
    """
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        if condition_func():
            return True
        await asyncio.sleep(poll_interval)
    
    return False


async def retry_async(
    func,
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
):
    """
    重试异步函数
    
    Args:
        func: 异步函数
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
        exceptions: 要捕获的异常类型
    
    Returns:
        函数执行结果
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
    
    raise last_exception


# ===========================================
# 测试数据清理
# ===========================================

class TestDataCleanup:
    """测试数据清理管理类"""
    
    _cleanup_callbacks: List[callable] = []
    
    @classmethod
    def register(cls, callback: callable) -> None:
        """注册清理回调"""
        cls._cleanup_callbacks.append(callback)
    
    @classmethod
    async def cleanup_all(cls) -> None:
        """执行所有清理回调"""
        for callback in cls._cleanup_callbacks:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                callback()
        
        cls._cleanup_callbacks.clear()
    
    @classmethod
    def reset(cls) -> None:
        """重置清理列表"""
        cls._cleanup_callbacks.clear()

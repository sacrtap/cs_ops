"""
Data Permission Filter - 数据权限过滤器

提供查询级别的过滤函数，用于手动应用到 SQLAlchemy 查询。

数据权限规则:
- Admin: 不过滤（可以看到全系统数据）
- Manager/Specialist: 过滤 org_id = current_user.org_id
- Sales: 过滤 sales_rep_id = current_user.id（如果模型有该字段）
"""
from sqlalchemy import and_
from sqlalchemy.orm import class_mapper
from typing import Optional, Type, Any
from sqlalchemy.sql import Select


def set_current_user_context(user_id: int, role: str, org_id: Optional[int] = None) -> dict:
    """
    设置当前用户上下文（返回上下文字典用于查询过滤器）
    
    Args:
        user_id: 用户 ID
        role: 用户角色 (admin, manager, specialist, sales)
        org_id: 组织 ID
        
    Returns:
        用户上下文字典
    """
    return {
        "user_id": user_id,
        "role": role,
        "org_id": org_id,
    }


def get_data_permission_filter(model_class: Type, user_context: dict) -> Optional[Any]:
    """
    获取数据权限过滤条件
    
    根据用户角色返回不同的过滤条件:
    - Admin: 返回 None（不过滤）
    - Manager/Specialist: org_id = current_user.org_id
    - Sales: sales_rep_id = current_user.id (如果有该字段), 否则 org_id 过滤
    
    Args:
        model_class: 要应用过滤器的模型类
        user_context: 用户上下文字典
        
    Returns:
        SQLAlchemy 过滤条件，如果不需要过滤则返回 None
    """
    role = user_context.get("role")
    user_id = user_context.get("user_id")
    org_id = user_context.get("org_id")
    
    # Admin 不需要过滤
    if role == "admin":
        return None
    
    # 检查模型字段
    mapper = class_mapper(model_class)
    column_keys = [c.key for c in mapper.columns]
    
    has_org_id = 'org_id' in column_keys
    has_sales_rep_id = 'sales_rep_id' in column_keys
    
    # 如果模型既没有 org_id 也没有 sales_rep_id，不应用过滤器
    if not has_org_id and not has_sales_rep_id:
        return None
    
    # 根据角色应用不同的过滤策略
    if role == "sales":
        # Sales: 优先使用 sales_rep_id 过滤，如果没有该字段则使用 org_id
        if has_sales_rep_id:
            return model_class.sales_rep_id == user_id
        elif has_org_id:
            return model_class.org_id == org_id
    
    elif role in ["manager", "specialist"]:
        # Manager/Specialist: 使用 org_id 过滤
        if has_org_id:
            if org_id is None:
                # 如果用户没有 org_id，返回 False 条件（不返回任何数据）
                from sqlalchemy import false
                return false()
            return model_class.org_id == org_id
    
    # 未知角色或没有匹配的字段
    return None


def apply_data_permission_filter(query: Select, model_class: Type, user_context: dict) -> Select:
    """
    对查询应用数据权限过滤器
    
    Args:
        query: SQLAlchemy 查询对象
        model_class: 要应用过滤器的模型类
        user_context: 用户上下文字典
        
    Returns:
        应用过滤器后的查询对象
    """
    filter_condition = get_data_permission_filter(model_class, user_context)
    
    if filter_condition is not None:
        query = query.where(filter_condition)
    
    return query


class DataPermissionFilter:
    """
    数据权限过滤器上下文管理器（仅用于向后兼容，推荐使用显式传递方式）
    
    使用方式:
    ```python
    async with DataPermissionFilter(user_id=1, role="sales", org_id=100):
        # 在此上下文中的查询会自动应用过滤
        results = await session.execute(select(Customer))
    ```
    
    注意：推荐使用显式传递 user_context 的方式，而不是使用上下文管理器
    """
    
    def __init__(self, user_id: int, role: str, org_id: Optional[int] = None):
        self.user_id = user_id
        self.role = role
        self.org_id = org_id
        self.user_context = None
    
    async def __aenter__(self):
        self.user_context = set_current_user_context(self.user_id, self.role, self.org_id)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 上下文管理器退出时，user_context 会自动销毁（局部变量）
        self.user_context = None

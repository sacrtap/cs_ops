"""
权限矩阵 Pydantic Schema - 请求/响应验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime


class PermissionUpdateRequest(BaseModel):
    """单个权限更新请求"""
    role: str = Field(..., description="角色名称", min_length=1, max_length=50)
    module: str = Field(..., description="功能模块", min_length=1, max_length=100)
    action: str = Field(..., description="操作类型", min_length=1, max_length=20)
    granted: bool = Field(..., description="是否授权")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = ['admin', 'manager', 'specialist', 'sales']
        if v not in valid_roles:
            raise ValueError(f'无效的角色：{v}。必须是 {valid_roles} 之一')
        return v
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        valid_actions = ['read', 'create', 'update', 'delete']
        if v not in valid_actions:
            raise ValueError(f'无效的操作：{v}。必须是 {valid_actions} 之一')
        return v.lower()


class PermissionBulkUpdateRequest(BaseModel):
    """批量权限更新请求"""
    permissions: List[PermissionUpdateRequest] = Field(..., description="权限列表")


class PermissionMatrixResponse(BaseModel):
    """权限矩阵响应"""
    role: str
    module: str
    action: str
    granted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AllPermissionsResponse(BaseModel):
    """所有角色权限响应"""
    admin: Dict[str, Dict[str, bool]]
    manager: Dict[str, Dict[str, bool]]
    specialist: Dict[str, Dict[str, bool]]
    sales: Dict[str, Dict[str, bool]]


class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    module: str = Field(..., description="功能模块")
    action: str = Field(..., description="操作类型")


class PermissionCheckResponse(BaseModel):
    """权限检查响应"""
    granted: bool
    role: str
    module: str
    action: str


class CacheStatsResponse(BaseModel):
    """缓存统计响应"""
    size: int
    max_size: int
    hits: int
    misses: int
    hit_rate: float
    ttl_seconds: int

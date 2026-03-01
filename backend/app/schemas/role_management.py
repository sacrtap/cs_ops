"""
角色管理 Pydantic Schema - 请求/响应验证
"""
import re
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime


class RoleCreateRequest(BaseModel):
    """角色创建请求"""
    name: str = Field(..., description="角色名称", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="角色描述", max_length=500)
    status: Optional[str] = Field("active", description="状态", pattern="^(active|inactive)$")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        # 检查名称格式：以小写字母开头，只能包含字母、数字和下划线
        if not re.match(r'^[a-z][a-z0-9_]{2,49}$', v):
            raise ValueError('角色名称必须以小写字母开头，只能包含字母、数字和下划线，长度 3-50 个字符')
        
        # 检查是否为系统默认角色
        valid_names = ['admin', 'manager', 'specialist', 'sales']
        if v.lower() in valid_names:
            raise ValueError(f'无法创建系统默认角色：{v.lower()}。系统默认角色已存在')
        
        return v


class RoleUpdateRequest(BaseModel):
    """角色更新请求"""
    name: Optional[str] = Field(None, description="角色名称", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="角色描述", max_length=500)
    status: Optional[str] = Field(None, description="状态", pattern="^(active|inactive)$")


class RolePermissionsUpdateRequest(BaseModel):
    """角色权限更新请求"""
    permissions: Dict[str, Dict[str, bool]] = Field(
        ...,
        description="权限字典 {module: {action: granted}}"
    )


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleWithPermissionsResponse(BaseModel):
    """带权限的角色响应"""
    id: int
    name: str
    description: Optional[str] = None
    status: str
    permissions: Dict[str, Dict[str, bool]]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleListResponse(BaseModel):
    """角色列表响应"""
    data: List[RoleResponse]
    meta: Dict[str, int]


class RoleStatsResponse(BaseModel):
    """角色统计响应"""
    total_roles: int
    active_roles: int
    inactive_roles: int
    roles: List[Dict]

"""
Permission Schemas - Pydantic 模式用于权限管理 API 请求/响应验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class UserRoleEnum(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MANAGER = "manager"
    SPECIALIST = "specialist"
    SALES = "sales"


class RoleResponse(BaseModel):
    """角色响应模型"""
    role: str = Field(..., description="角色名称")
    name: str = Field(..., description="角色显示名称")
    level: int = Field(..., description="角色级别（1-4）")
    description: str = Field(..., description="角色描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "manager",
                "name": "经理",
                "level": 3,
                "description": "运营经理，拥有除系统配置外的所有业务功能权限"
            }
        }


class RoleListResponse(BaseModel):
    """角色列表响应模型"""
    data: List[RoleResponse]
    meta: Dict
    error: Optional[Dict] = None


class PermissionMatrixResponse(BaseModel):
    """权限矩阵响应模型"""
    data: Dict[str, Dict[str, List[str]]]
    meta: Dict
    error: Optional[Dict] = None


class PermissionCheckRequest(BaseModel):
    """权限检查请求模型"""
    resource: str = Field(..., description="资源名称（customer, settlement, report, user, role）")
    action: str = Field(..., description="操作类型（create, read, update, delete, view）")
    
    @field_validator('resource')
    @classmethod
    def validate_resource(cls, v: str) -> str:
        valid_resources = {'customer', 'settlement', 'report', 'user', 'role'}
        if v.lower() not in valid_resources:
            raise ValueError(f"无效的资源名称：{v}。有效值：{valid_resources}")
        return v.lower()
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        valid_actions = {'create', 'read', 'update', 'delete', 'view', 'export'}
        if v.lower() not in valid_actions:
            raise ValueError(f"无效的操作类型：{v}。有效值：{valid_actions}")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "resource": "customer",
                "action": "delete"
            }
        }


class PermissionCheckResponse(BaseModel):
    """权限检查响应模型"""
    data: Dict
    meta: Dict
    error: Optional[Dict] = None


class PermissionMatrixUpdateRequest(BaseModel):
    """权限矩阵更新请求模型"""
    role: str = Field(..., description="角色名称")
    resource: str = Field(..., description="资源名称")
    action: str = Field(..., description="操作类型")
    enabled: bool = Field(default=True, description="true=添加权限，false=移除权限")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = {'admin', 'manager', 'specialist', 'sales'}
        if v.lower() not in valid_roles:
            raise ValueError(f"无效的角色名称：{v}。有效值：{valid_roles}")
        return v.lower()
    
    @field_validator('resource')
    @classmethod
    def validate_resource(cls, v: str) -> str:
        valid_resources = {'customer', 'settlement', 'report', 'user', 'role'}
        if v.lower() not in valid_resources:
            raise ValueError(f"无效的资源名称：{v}。有效值：{valid_resources}")
        return v.lower()
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        valid_actions = {'create', 'read', 'update', 'delete', 'view', 'export'}
        if v.lower() not in valid_actions:
            raise ValueError(f"无效的操作类型：{v}。有效值：{valid_actions}")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "manager",
                "resource": "customer",
                "action": "delete",
                "enabled": True
            }
        }


class PermissionMatrixUpdateResponse(BaseModel):
    """权限矩阵更新响应模型"""
    data: Dict
    meta: Dict
    error: Optional[Dict] = None

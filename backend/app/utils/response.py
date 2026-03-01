"""
统一响应工具函数
"""
from sanic.response import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def generate_meta(**kwargs) -> Dict:
    """生成响应元数据"""
    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": kwargs.get("request_id", "unknown"),
    }
    
    # 添加额外的元数据
    if "total" in kwargs:
        meta["total"] = kwargs["total"]
    
    return meta


def success_response(
    data: Any,
    meta: Optional[Dict] = None,
    status_code: int = 200
):
    """
    成功响应
    
    Args:
        data: 响应数据
        meta: 可选的元数据
        status_code: HTTP 状态码
    
    Returns:
        Sanic JSON 响应
    """
    response = {
        "data": data,
        "meta": meta or generate_meta()
    }
    
    return json(response, status=status_code)


def error_response(
    message: str,
    status_code: int = 400,
    code: str = "ERROR",
    details: Optional[Dict] = None
):
    """
    错误响应
    
    Args:
        message: 错误消息
        status_code: HTTP 状态码
        code: 错误代码
        details: 可选的详细信息
    
    Returns:
        Sanic JSON 响应
    """
    response = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }
    
    return json(response, status=status_code)

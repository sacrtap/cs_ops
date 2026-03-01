"""
Customer Routes - 客户管理 API 路由（集成数据权限过滤）

示例：如何在查询中应用数据权限过滤器
"""
from sanic import Blueprint, Request, json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.customer import Customer
from ..models.user import User, UserRole
from ..middleware.auth_middleware import AuthMiddleware
from ..middleware.permission_middleware import PermissionMiddleware
from ..utils.data_permission_filter import apply_data_permission_filter
from datetime import datetime, timezone

# 创建 Blueprint
customer_bp = Blueprint("Customer", url_prefix="/api/v1/customers")


@customer_bp.route("/", methods=["GET"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("customer", "read")
async def list_customers(request: Request):
    """
    获取客户列表（自动应用数据权限过滤）
    
    销售角色仅能看到自己负责的客户（org_id 匹配）
    经理及以上角色可以看到所有客户
    
    Query Parameters:
        page: 页码（默认 1）
        page_size: 每页数量（默认 20）
    
    Returns:
        {
            "data": [...],
            "meta": {
                "total": 100,
                "page": 1,
                "page_size": 20
            }
        }
    """
    db: AsyncSession = request.ctx.db
    user: User = request.ctx.current_user
    
    # 获取分页参数
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    
    # 应用数据权限过滤器（仅对 sales 角色生效）
    # 注意：这里需要在 query 执行前调用 apply_data_permission_filter
    apply_data_permission_filter(db, Customer)
    
    # 构建查询
    stmt = select(Customer)
    
    # 执行查询（会自动应用 org_id 过滤）
    result = await db.execute(stmt)
    customers = result.scalars().all()
    
    return json({
        "data": [c.to_dict() for c in customers],
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": len(customers),
            "page": page,
            "page_size": page_size
        }
    })

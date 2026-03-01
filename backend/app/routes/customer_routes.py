"""
Customer Routes - 客户管理 API 路由（集成数据权限过滤）

数据权限规则:
- Admin: 可以看到全系统所有客户
- Manager/Specialist: 只能看到本组织 (org_id) 的客户
- Sales: 只能看到自己负责 (sales_rep_id) 的客户
"""
from sanic import Blueprint, Request, json
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from ..models.customer import Customer
from ..models.user import User
from ..models.organization import Organization
from ..middleware.auth_middleware import AuthMiddleware
from ..middleware.permission_middleware import PermissionMiddleware
from ..utils.data_permission_filter import (
    apply_data_permission_filter,
    set_current_user_context,
)

# 创建 Blueprint
customer_bp = Blueprint("Customer", url_prefix="/api/v1/customers")


@customer_bp.route("/", methods=["GET"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("customer", "read")
async def list_customers(request: Request):
    """
    获取客户列表（自动应用数据权限过滤）
    
    数据权限规则:
    - Admin: 可以看到全系统所有客户
    - Manager/Specialist: 只能看到本组织 (org_id) 的客户
    - Sales: 只能看到自己负责 (sales_rep_id) 的客户
    
    Query Parameters:
        page: 页码（默认 1）
        page_size: 每页数量（默认 20）
        org_id: 组织 ID 筛选（仅 Admin 可用）
        sales_rep_id: 销售代表 ID 筛选（仅 Admin/Manager 可用）
        status: 客户状态筛选（active/inactive/lead）
    
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
    current_user: User = request.ctx.current_user
    
    # 设置当前用户上下文（用于数据权限过滤）
    user_context = set_current_user_context(
        user_id=current_user.id,
        role=current_user.role.value,
        org_id=current_user.org_id
    )
    
    try:
        # 获取分页参数
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 获取筛选参数
        filter_org_id = request.args.get("org_id", type=int)
        filter_sales_rep_id = request.args.get("sales_rep_id", type=int)
        filter_status = request.args.get("status", type=str)
        
        # 构建查询
        stmt = select(Customer)
        
        # Admin 可以使用额外的筛选器
        if current_user.role.value == "admin":
            if filter_org_id:
                stmt = stmt.where(Customer.org_id == filter_org_id)
            if filter_sales_rep_id:
                stmt = stmt.where(Customer.sales_rep_id == filter_sales_rep_id)
        
        # Manager 可以按销售代表筛选
        elif current_user.role.value in ["manager", "specialist"]:
            if filter_sales_rep_id:
                stmt = stmt.where(Customer.sales_rep_id == filter_sales_rep_id)
        
        # 状态筛选（所有角色都可用）
        if filter_status:
            stmt = stmt.where(Customer.status == filter_status)
        
        # 应用数据权限过滤器（手动应用过滤条件）
        stmt = apply_data_permission_filter(stmt, Customer, user_context)
        
        # 计算分页
        offset = (page - 1) * page_size
        
        # 获取总数（在应用过滤器后）
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # 执行查询
        stmt = stmt.offset(offset).limit(page_size)
        result = await db.execute(stmt)
        customers = result.scalars().all()
        
        return json({
            "data": [c.to_dict() for c in customers],
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        })
    
    finally:
        # 注意：不需要清除上下文，因为使用显式传递方式
        # user_context 是局部变量，函数结束后自动销毁
        pass


@customer_bp.route("/<customer_id:int>", methods=["GET"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("customer", "read")
async def get_customer(request: Request, customer_id: int):
    """
    获取客户详情（检查数据权限）
    
    数据权限规则:
    - Admin: 可以查看所有客户
    - Manager/Specialist: 只能查看本组织客户
    - Sales: 只能查看自己负责的客户
    
    Returns:
        客户详情对象
        
    Raises:
        403: 如果没有权限查看该客户
        404: 如果客户不存在
    """
    db: AsyncSession = request.ctx.db
    current_user: User = request.ctx.current_user
    
    # 查询客户
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    
    if not customer:
        return json(
            {"error": {"code": "NOT_FOUND", "message": "客户不存在"}},
            status=404
        )
    
    # 检查数据权限
    if current_user.role.value == "admin":
        # Admin 可以查看所有客户
        pass
    
    elif current_user.role.value in ["manager", "specialist"]:
        # Manager/Specialist 只能查看本组织客户
        if customer.org_id != current_user.org_id:
            return json(
                {"error": {"code": "PERMISSION_DENIED", "message": "您没有权限查看此客户"}},
                status=403
            )
    
    elif current_user.role.value == "sales":
        # Sales 只能查看自己负责的客户
        if customer.sales_rep_id != current_user.id:
            return json(
                {"error": {"code": "PERMISSION_DENIED", "message": "您没有权限查看此客户"}},
                status=403
            )
    
    return json({
        "data": customer.to_dict(),
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })


@customer_bp.route("/", methods=["POST"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("customer", "create")
async def create_customer(request: Request):
    """
    创建客户
    
    数据权限规则:
    - Admin/Manager: 可以创建本组织客户
    - Sales: 可以创建客户（自动关联为自己负责）
    
    Request Body:
        {
            "name": "客户名称",
            "contact_name": "联系人姓名",
            "contact_email": "联系人邮箱",
            "contact_phone": "联系人电话",
            "address": "客户地址",
            "status": "active"
        }
    
    Returns:
        创建的客户对象
    """
    db: AsyncSession = request.ctx.db
    current_user: User = request.ctx.current_user
    
    # 获取请求数据
    data = request.json
    
    # 验证必填字段
    required_fields = ["name", "contact_name"]
    for field in required_fields:
        if not data.get(field):
            return json(
                {"error": {"code": "VALIDATION_ERROR", "message": f"缺少必填字段：{field}"}},
                status=400
            )
    
    # 创建客户对象
    customer = Customer(
        name=data["name"],
        contact_name=data.get("contact_name"),
        contact_email=data.get("contact_email"),
        contact_phone=data.get("contact_phone"),
        address=data.get("address"),
        status=data.get("status", "active"),
        notes=data.get("notes"),
        # 数据权限字段
        org_id=current_user.org_id if current_user.role.value != "admin" else data.get("org_id"),
        sales_rep_id=data.get("sales_rep_id", current_user.id)  # 默认关联为创建者
    )
    
    # Sales 只能创建自己负责的客户
    if current_user.role.value == "sales":
        customer.sales_rep_id = current_user.id
    
    # Admin 可以指定销售代表
    if current_user.role.value == "admin" and data.get("sales_rep_id"):
        customer.sales_rep_id = data["sales_rep_id"]
    
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    
    return json(
        {"data": customer.to_dict()},
        status=201
    )


@customer_bp.route("/<customer_id:int>", methods=["PUT"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("customer", "update")
async def update_customer(request: Request, customer_id: int):
    """
    更新客户
    
    数据权限规则:
    - Admin/Manager: 可以更新本组织客户
    - Sales: 只能更新自己负责的客户
    
    Request Body:
        {
            "name": "客户名称",
            "contact_name": "联系人姓名",
            ...
        }
    
    Returns:
        更新后的客户对象
        
    Raises:
        403: 如果没有权限更新该客户
    """
    db: AsyncSession = request.ctx.db
    current_user: User = request.ctx.current_user
    
    # 查询客户
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    
    if not customer:
        return json(
            {"error": {"code": "NOT_FOUND", "message": "客户不存在"}},
            status=404
        )
    
    # 检查数据权限
    if current_user.role.value == "admin":
        # Admin 可以更新所有客户
        pass
    
    elif current_user.role.value in ["manager", "specialist"]:
        # Manager/Specialist 只能更新本组织客户
        if customer.org_id != current_user.org_id:
            return json(
                {"error": {"code": "PERMISSION_DENIED", "message": "您没有权限更新此客户"}},
                status=403
            )
    
    elif current_user.role.value == "sales":
        # Sales 只能更新自己负责的客户
        if customer.sales_rep_id != current_user.id:
            return json(
                {"error": {"code": "PERMISSION_DENIED", "message": "您没有权限更新此客户"}},
                status=403
            )
    
    # 更新字段
    data = request.json
    updatable_fields = [
        "name", "contact_name", "contact_email", "contact_phone",
        "address", "status", "notes"
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(customer, field, data[field])
    
    # Sales 不能修改 sales_rep_id
    # Admin/Manager 可以重新分配客户
    if current_user.role.value in ["admin", "manager"] and "sales_rep_id" in data:
        customer.sales_rep_id = data["sales_rep_id"]
    
    await db.commit()
    await db.refresh(customer)
    
    return json({
        "data": customer.to_dict(),
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })


@customer_bp.route("/<customer_id:int>", methods=["DELETE"])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("customer", "delete")
async def delete_customer(request: Request, customer_id: int):
    """
    删除客户
    
    数据权限规则:
    - Admin/Manager: 可以删除本组织客户
    - Sales: 只能删除自己负责的客户
    
    Returns:
        删除成功消息
        
    Raises:
        403: 如果没有权限删除该客户
    """
    db: AsyncSession = request.ctx.db
    current_user: User = request.ctx.current_user
    
    # 查询客户
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    
    if not customer:
        return json(
            {"error": {"code": "NOT_FOUND", "message": "客户不存在"}},
            status=404
        )
    
    # 检查数据权限
    if current_user.role.value == "admin":
        # Admin 可以删除所有客户
        pass
    
    elif current_user.role.value in ["manager", "specialist"]:
        # Manager/Specialist 只能删除本组织客户
        if customer.org_id != current_user.org_id:
            return json(
                {"error": {"code": "PERMISSION_DENIED", "message": "您没有权限删除此客户"}},
                status=403
            )
    
    elif current_user.role.value == "sales":
        # Sales 只能删除自己负责的客户
        if customer.sales_rep_id != current_user.id:
            return json(
                {"error": {"code": "PERMISSION_DENIED", "message": "您没有权限删除此客户"}},
                status=403
            )
    
    # 删除客户
    await db.delete(customer)
    await db.commit()
    
    return json({
        "message": "客户已成功删除",
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })

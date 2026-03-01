"""
Permission Audit Routes - 权限审计路由

提供权限审计相关的 API 接口：
- GET /api/v1/permissions/audit - 查询权限审计记录
- GET /api/v1/permissions/audit/statistics - 获取权限审计统计信息
- GET /api/v1/permissions/audit/export - 导出权限审计记录
"""
from sanic import Blueprint
from sanic.response import json, text
from ..services.permission_audit_service import PermissionAuditService
from ..middleware.auth_middleware import AuthMiddleware
from ..middleware.permission_middleware import PermissionMiddleware

permission_audit_bp = Blueprint('permission_audit', url_prefix='/api/v1')


@permission_audit_bp.route('/permissions/audit', methods=['GET'])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("audit", "read")
async def query_audit_logs(request):
    """
    查询权限审计记录
    
    Query Parameters:
        user_id: 用户 ID（可选）
        start_date: 开始日期（可选，格式：YYYY-MM-DD）
        end_date: 结束日期（可选，格式：YYYY-MM-DD）
        anomaly_type: 异常类型（可选）
        page: 页码（默认 1）
        page_size: 每页数量（默认 20）
        sort_by: 排序字段（默认 timestamp）
        sort_order: 排序顺序 asc/desc（默认 desc）
    
    Returns:
        JSON: 权限审计记录列表和分页信息
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        anomaly_type = request.args.get('anomaly_type')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        
        session = request.ctx.db
        result = await PermissionAuditService.query_audit_logs(
            session=session,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            anomaly_type=anomaly_type,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return json({
            "success": True,
            "data": result
        }, status=200)
    except ValueError as e:
        return json({
            "success": False,
            "message": f"Invalid parameter: {str(e)}"
        }, status=400)
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_audit_bp.route('/permissions/audit/statistics', methods=['GET'])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("audit", "read")
async def get_audit_statistics(request):
    """
    获取权限审计统计信息
    
    Query Parameters:
        start_date: 开始日期（可选，格式：YYYY-MM-DD）
        end_date: 结束日期（可选，格式：YYYY-MM-DD）
    
    Returns:
        JSON: 统计信息（总记录数、异常记录数、异常率）
    """
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        session = request.ctx.db
        statistics = await PermissionAuditService.get_audit_statistics(
            session=session,
            start_date=start_date,
            end_date=end_date
        )
        
        return json({
            "success": True,
            "data": statistics
        }, status=200)
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)


@permission_audit_bp.route('/permissions/audit/export', methods=['GET'])
@AuthMiddleware.require_auth
@PermissionMiddleware.require_permission("audit", "read")
async def export_audit_logs(request):
    """
    导出权限审计记录
    
    Query Parameters:
        user_id: 用户 ID（可选）
        start_date: 开始日期（可选，格式：YYYY-MM-DD）
        end_date: 结束日期（可选，格式：YYYY-MM-DD）
        format: 导出格式 csv/json（默认 csv）
    
    Returns:
        File: 导出的文件（CSV 或 JSON 格式）
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'csv').lower()
        
        session = request.ctx.db
        content = await PermissionAuditService.export_audit_logs(
            session=session,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            format=format_type
        )
        
        # 设置响应头
        if format_type == 'csv':
            content_type = 'text/csv'
            filename = 'permission_audit_logs.csv'
        else:
            content_type = 'application/json'
            filename = 'permission_audit_logs.json'
        
        response = text(content)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    except Exception as e:
        return json({
            "success": False,
            "error": str(e)
        }, status=500)

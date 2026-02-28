"""
Sanic 应用主入口
"""
import logging
from sanic import Sanic, response
from sanic.exceptions import NotFound, ServerError
from app.config.settings import settings
from app.database import init_db, close_db
from app.routes.auth_routes import auth_bp

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("cs_ops")


def create_app() -> Sanic:
    """
    创建并配置 Sanic 应用
    
    Returns:
        Sanic: 配置好的应用实例
    """
    # 创建应用
    app = Sanic("cs_ops")

    # 配置 CORS
    app.config.CORS_ORIGINS = settings.CORS_ORIGINS
    app.config.CORS_SUPPORTS_CREDENTIALS = True

    # 注册 Blueprint
    app.blueprint(auth_bp)

    # 注册事件处理器
    register_events(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 注册健康检查端点
    @app.get("/health")
    async def health_check(request):
        return response.json({"status": "healthy", "version": settings.APP_VERSION})

    @app.get("/")
    async def root(request):
        return response.json({
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs"  # TODO: 添加 API 文档
        })

    return app


def register_events(app: Sanic) -> None:
    """注册应用事件处理器"""

    @app.before_server_start
    async def before_server_start(app: Sanic, loop):
        """服务器启动前初始化数据库"""
        logger.info("初始化数据库连接...")
        await init_db()
        logger.info("数据库初始化完成")

    @app.after_server_stop
    async def after_server_stop(app: Sanic, loop):
        """服务器停止后关闭数据库连接"""
        logger.info("关闭数据库连接...")
        await close_db()
        logger.info("数据库连接已关闭")

    @app.on_request
    async def before_request(request):
        """请求前处理"""
        # 记录请求日志
        logger.debug(f"{request.method} {request.path}")

    @app.on_response
    async def after_response(request, response):
        """响应后处理"""
        # 可以在这里添加统一的响应处理逻辑
        pass


def register_error_handlers(app: Sanic) -> None:
    """注册错误处理器"""

    @app.exception(NotFound)
    async def handle_404(request, exception):
        return response.json(
            {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "资源不存在",
                    "details": [{"field": "path", "message": f"{request.path} 未找到"}]
                }
            },
            status=404
        )

    @app.exception(ServerError)
    async def handle_500(request, exception):
        logger.error(f"服务器错误：{exception}", exc_info=True)
        return response.json(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                }
            },
            status=500
        )

    @app.exception(Exception)
    async def handle_generic_exception(request, exception):
        logger.error(f"未处理异常：{exception}", exc_info=True)
        return response.json(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                }
            },
            status=500
        )


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    # 开发模式运行
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=settings.DEBUG,
        auto_reload=settings.DEBUG,
        workers=1
    )

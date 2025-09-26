"""
FastAPI应用主入口
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from typing import Dict, Any

from config.settings import settings
from app.utils.logger import get_logger
from app.api import health, projects, tasks, risks, issues, auto_task_capture, intelligent_progress_summary, risk_monitoring, report_generator, intelligent_chat, ai_analysis, cache_management, monitoring
from app.models.base import APIResponse, HealthCheckResponse

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")
    logger.info(f"应用名称: {settings.app_name}")
    logger.info(f"应用版本: {settings.app_version}")
    logger.info(f"调试模式: {settings.debug}")
    
    # 初始化数据库等资源
    # TODO: 在这里添加数据库初始化等逻辑
    
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭中...")
    # TODO: 在这里添加清理逻辑
    logger.info("应用关闭完成")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="通过AI技术解决项目管理中的低价值、高频事务，实现信息自动收集、智能汇总与任务流转减负",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# 添加受信任主机中间件
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.company.com"]
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url}")
    logger.debug(f"请求头: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(f"请求完成: {request.method} {request.url} - 状态码: {response.status_code} - 耗时: {process_time:.3f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"请求失败: {request.method} {request.url} - 错误: {str(e)} - 耗时: {process_time:.3f}s")
        raise


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error_response(
            message=exc.detail,
            error_code=str(exc.status_code)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIResponse.error_response(
            message="内部服务器错误",
            error_code="INTERNAL_SERVER_ERROR"
        ).dict()
    )


# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(projects.router, prefix="/api/v1", tags=["项目管理"])
app.include_router(tasks.router, prefix="/api/v1", tags=["任务管理"])
app.include_router(risks.router, prefix="/api/v1", tags=["风险管理"])
app.include_router(issues.router, prefix="/api/v1", tags=["问题管理"])

# 第二阶段：核心功能API
app.include_router(auto_task_capture.router, prefix="/api/v1", tags=["自动任务捕捉"])
app.include_router(intelligent_progress_summary.router, prefix="/api/v1", tags=["智能进度汇总"])
app.include_router(risk_monitoring.router, prefix="/api/v1", tags=["风险监控"])
app.include_router(report_generator.router, prefix="/api/v1", tags=["报表生成"])

# 第三阶段：AI集成与优化API
app.include_router(intelligent_chat.router, prefix="/api/v1", tags=["智能对话"])
app.include_router(ai_analysis.router, prefix="/api/v1", tags=["智能分析"])

# 第四阶段：测试与部署API
app.include_router(cache_management.router, prefix="/api/v1", tags=["缓存管理"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["系统监控"])


@app.get("/", response_model=APIResponse)
async def root():
    """根路径"""
    return APIResponse.success_response(
        data={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "description": "通过AI技术解决项目管理中的低价值、高频事务",
            "docs_url": "/docs" if settings.debug else None,
            "health_check": "/api/v1/health"
        },
        message="欢迎使用自动减负AI应用架构"
    )


@app.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查接口"""
    try:
        # TODO: 检查数据库连接状态
        database_status = "healthy"
        
        # TODO: 检查依赖服务状态
        dependencies = {
            "database": "healthy",
            "qwen_api": "healthy" if settings.qwen_api_key else "not_configured"
        }
        
        return HealthCheckResponse(
            status="healthy",
            version=settings.app_version,
            database_status=database_status,
            dependencies=dependencies
        )
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            version=settings.app_version,
            database_status="unhealthy",
            dependencies={}
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

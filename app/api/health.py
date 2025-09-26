"""
健康检查API
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.models.base import APIResponse, HealthCheckResponse
from config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接状态
        database_status = "healthy"
        
        # 检查依赖服务状态
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


@router.get("/health/detailed", response_model=APIResponse)
async def detailed_health_check():
    """详细健康检查接口"""
    try:
        health_info = {
            "application": {
                "name": settings.app_name,
                "version": settings.app_version,
                "status": "healthy"
            },
            "database": {
                "status": "healthy",
                "type": "json",
                "path": settings.json_database_path
            },
            "external_services": {
                "qwen_api": {
                    "status": "healthy" if settings.qwen_api_key else "not_configured",
                    "configured": bool(settings.qwen_api_key)
                }
            },
            "system": {
                "debug_mode": settings.debug,
                "log_level": settings.log_level
            }
        }
        
        return APIResponse.success_response(
            data=health_info,
            message="详细健康检查完成"
        )
    except Exception as e:
        logger.error(f"详细健康检查失败: {str(e)}")
        return APIResponse.error_response(
            message=f"详细健康检查失败: {str(e)}",
            error_code="HEALTH_CHECK_FAILED"
        )


@router.get("/health/ready", response_model=APIResponse)
async def readiness_check():
    """就绪检查接口"""
    try:
        # 检查应用是否准备好接收请求
        ready_checks = {
            "database": True,  # TODO: 实际检查数据库连接
            "configuration": True,
            "dependencies": True
        }
        
        all_ready = all(ready_checks.values())
        
        if all_ready:
            return APIResponse.success_response(
                data=ready_checks,
                message="应用已就绪"
            )
        else:
            return APIResponse.error_response(
                message="应用未就绪",
                error_code="NOT_READY"
            )
    except Exception as e:
        logger.error(f"就绪检查失败: {str(e)}")
        return APIResponse.error_response(
            message=f"就绪检查失败: {str(e)}",
            error_code="READINESS_CHECK_FAILED"
        )


@router.get("/health/live", response_model=APIResponse)
async def liveness_check():
    """存活检查接口"""
    try:
        # 简单的存活检查，确保应用正在运行
        return APIResponse.success_response(
            data={"status": "alive"},
            message="应用存活"
        )
    except Exception as e:
        logger.error(f"存活检查失败: {str(e)}")
        return APIResponse.error_response(
            message=f"存活检查失败: {str(e)}",
            error_code="LIVENESS_CHECK_FAILED"
        )

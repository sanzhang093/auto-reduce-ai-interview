"""
缓存管理API
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, Any, List
from app.models.base import APIResponse
from app.services.cache_service import cache_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/auto-reduce/cache/stats", response_model=APIResponse)
async def get_cache_statistics():
    """获取缓存统计信息"""
    try:
        stats = cache_service.get_stats()
        
        return APIResponse.success_response(
            data=stats,
            message="获取缓存统计信息成功"
        )
    except Exception as e:
        logger.error(f"获取缓存统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计信息失败: {str(e)}")


@router.get("/auto-reduce/cache/info", response_model=APIResponse)
async def get_cache_info():
    """获取缓存信息"""
    try:
        cache_info = cache_service.get_cache_info()
        
        return APIResponse.success_response(
            data={
                "cache_items": cache_info,
                "total_items": len(cache_info)
            },
            message="获取缓存信息成功"
        )
    except Exception as e:
        logger.error(f"获取缓存信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取缓存信息失败: {str(e)}")


@router.delete("/auto-reduce/cache/clear", response_model=APIResponse)
async def clear_cache():
    """清空缓存"""
    try:
        cache_service.clear()
        
        return APIResponse.success_response(
            data={"cleared": True},
            message="缓存已清空"
        )
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")


@router.delete("/auto-reduce/cache/cleanup", response_model=APIResponse)
async def cleanup_expired_cache():
    """清理过期缓存"""
    try:
        cache_service.cleanup_expired()
        
        return APIResponse.success_response(
            data={"cleanup_completed": True},
            message="过期缓存清理完成"
        )
    except Exception as e:
        logger.error(f"清理过期缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理过期缓存失败: {str(e)}")


@router.delete("/auto-reduce/cache/project/{project_id}", response_model=APIResponse)
async def invalidate_project_cache(project_id: str = Path(..., description="项目ID")):
    """使项目缓存失效"""
    try:
        from app.services.cache_service import invalidate_project_cache
        
        invalidate_project_cache(project_id)
        
        return APIResponse.success_response(
            data={"project_id": project_id, "invalidated": True},
            message=f"项目 {project_id} 的缓存已失效"
        )
    except Exception as e:
        logger.error(f"使项目缓存失效失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"使项目缓存失效失败: {str(e)}")


@router.delete("/auto-reduce/cache/user/{user_id}", response_model=APIResponse)
async def invalidate_user_cache(user_id: str = Path(..., description="用户ID")):
    """使用户缓存失效"""
    try:
        from app.services.cache_service import invalidate_user_cache
        
        invalidate_user_cache(user_id)
        
        return APIResponse.success_response(
            data={"user_id": user_id, "invalidated": True},
            message=f"用户 {user_id} 的缓存已失效"
        )
    except Exception as e:
        logger.error(f"使用户缓存失效失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"使用户缓存失效失败: {str(e)}")


@router.get("/auto-reduce/cache/performance", response_model=APIResponse)
async def get_cache_performance():
    """获取缓存性能指标"""
    try:
        stats = cache_service.get_stats()
        
        # 计算性能指标
        performance_metrics = {
            "hit_rate": stats["hit_rate"],
            "cache_efficiency": "优秀" if stats["hit_rate"] > 80 else "良好" if stats["hit_rate"] > 60 else "一般",
            "cache_utilization": (stats["cache_size"] / stats["max_size"]) * 100,
            "total_requests": stats["total_requests"],
            "cache_size": stats["cache_size"],
            "max_size": stats["max_size"]
        }
        
        return APIResponse.success_response(
            data=performance_metrics,
            message="获取缓存性能指标成功"
        )
    except Exception as e:
        logger.error(f"获取缓存性能指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取缓存性能指标失败: {str(e)}")

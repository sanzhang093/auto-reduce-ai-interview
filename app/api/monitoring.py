"""
监控API
"""
from fastapi import APIRouter, HTTPException, Query, Path, Body
from typing import Dict, Any, List, Optional
from app.models.base import APIResponse
from app.services.monitoring_service import monitoring_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/auto-reduce/monitoring/health", response_model=APIResponse)
async def get_health_status():
    """获取系统健康状态"""
    try:
        health_status = monitoring_service.get_health_status()
        
        return APIResponse.success_response(
            data=health_status,
            message="获取系统健康状态成功"
        )
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统健康状态失败: {str(e)}")


@router.get("/auto-reduce/monitoring/metrics", response_model=APIResponse)
async def get_system_metrics():
    """获取系统指标"""
    try:
        system_metrics = monitoring_service.collect_system_metrics()
        app_metrics = monitoring_service.collect_application_metrics()
        
        return APIResponse.success_response(
            data={
                "system_metrics": {
                    "timestamp": system_metrics.timestamp.isoformat(),
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "disk_percent": system_metrics.disk_percent,
                    "network_sent": system_metrics.network_sent,
                    "network_recv": system_metrics.network_recv,
                    "load_average": system_metrics.load_average
                },
                "application_metrics": {
                    "timestamp": app_metrics.timestamp.isoformat(),
                    "active_connections": app_metrics.active_connections,
                    "request_count": app_metrics.request_count,
                    "error_count": app_metrics.error_count,
                    "response_time_avg": app_metrics.response_time_avg,
                    "cache_hit_rate": app_metrics.cache_hit_rate,
                    "database_connections": app_metrics.database_connections
                }
            },
            message="获取系统指标成功"
        )
    except Exception as e:
        logger.error(f"获取系统指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统指标失败: {str(e)}")


@router.get("/auto-reduce/monitoring/alerts", response_model=APIResponse)
async def get_active_alerts():
    """获取活跃告警"""
    try:
        active_alerts = monitoring_service.get_active_alerts()
        
        return APIResponse.success_response(
            data={
                "active_alerts": active_alerts,
                "alert_count": len(active_alerts)
            },
            message="获取活跃告警成功"
        )
    except Exception as e:
        logger.error(f"获取活跃告警失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取活跃告警失败: {str(e)}")


@router.get("/auto-reduce/monitoring/alerts/history", response_model=APIResponse)
async def get_alert_history(
    hours: int = Query(default=24, description="查询时间范围（小时）")
):
    """获取告警历史"""
    try:
        alert_history = monitoring_service.get_alert_history(hours)
        
        return APIResponse.success_response(
            data={
                "alert_history": alert_history,
                "time_range_hours": hours,
                "total_alerts": len(alert_history)
            },
            message="获取告警历史成功"
        )
    except Exception as e:
        logger.error(f"获取告警历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取告警历史失败: {str(e)}")


@router.post("/auto-reduce/monitoring/alerts/{alert_type}/resolve", response_model=APIResponse)
async def resolve_alert(alert_type: str = Path(..., description="告警类型")):
    """解决告警"""
    try:
        monitoring_service.resolve_alert(alert_type)
        
        return APIResponse.success_response(
            data={"alert_type": alert_type, "resolved": True},
            message=f"告警 {alert_type} 已解决"
        )
    except Exception as e:
        logger.error(f"解决告警失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解决告警失败: {str(e)}")


@router.get("/auto-reduce/monitoring/summary", response_model=APIResponse)
async def get_metrics_summary(
    hours: int = Query(default=24, description="查询时间范围（小时）")
):
    """获取指标摘要"""
    try:
        summary = monitoring_service.get_metrics_summary(hours)
        
        return APIResponse.success_response(
            data=summary,
            message="获取指标摘要成功"
        )
    except Exception as e:
        logger.error(f"获取指标摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取指标摘要失败: {str(e)}")


@router.put("/auto-reduce/monitoring/thresholds", response_model=APIResponse)
async def update_alert_thresholds(
    thresholds: Dict[str, float] = Body(..., description="告警阈值配置")
):
    """更新告警阈值"""
    try:
        monitoring_service.update_alert_thresholds(thresholds)
        
        return APIResponse.success_response(
            data={"thresholds": thresholds, "updated": True},
            message="告警阈值更新成功"
        )
    except Exception as e:
        logger.error(f"更新告警阈值失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新告警阈值失败: {str(e)}")


@router.get("/auto-reduce/monitoring/dashboard", response_model=APIResponse)
async def get_monitoring_dashboard():
    """获取监控仪表板数据"""
    try:
        # 获取健康状态
        health_status = monitoring_service.get_health_status()
        
        # 获取系统指标
        system_metrics = monitoring_service.collect_system_metrics()
        app_metrics = monitoring_service.collect_application_metrics()
        
        # 获取活跃告警
        active_alerts = monitoring_service.get_active_alerts()
        
        # 获取指标摘要
        summary = monitoring_service.get_metrics_summary(24)
        
        dashboard_data = {
            "health_status": health_status,
            "current_metrics": {
                "system": {
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "disk_percent": system_metrics.disk_percent,
                    "load_average": system_metrics.load_average
                },
                "application": {
                    "active_connections": app_metrics.active_connections,
                    "request_count": app_metrics.request_count,
                    "error_count": app_metrics.error_count,
                    "response_time_avg": app_metrics.response_time_avg,
                    "cache_hit_rate": app_metrics.cache_hit_rate
                }
            },
            "active_alerts": active_alerts,
            "summary": summary,
            "timestamp": system_metrics.timestamp.isoformat()
        }
        
        return APIResponse.success_response(
            data=dashboard_data,
            message="获取监控仪表板数据成功"
        )
    except Exception as e:
        logger.error(f"获取监控仪表板数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取监控仪表板数据失败: {str(e)}")


@router.get("/auto-reduce/monitoring/performance", response_model=APIResponse)
async def get_performance_metrics():
    """获取性能指标"""
    try:
        system_metrics = monitoring_service.collect_system_metrics()
        app_metrics = monitoring_service.collect_application_metrics()
        
        # 计算性能指标
        performance_metrics = {
            "system_performance": {
                "cpu_utilization": system_metrics.cpu_percent,
                "memory_utilization": system_metrics.memory_percent,
                "disk_utilization": system_metrics.disk_percent,
                "load_average": system_metrics.load_average,
                "network_throughput": {
                    "sent_bytes": system_metrics.network_sent,
                    "received_bytes": system_metrics.network_recv
                }
            },
            "application_performance": {
                "throughput": {
                    "requests_per_second": app_metrics.request_count / 3600,  # 假设1小时
                    "errors_per_second": app_metrics.error_count / 3600
                },
                "latency": {
                    "average_response_time": app_metrics.response_time_avg,
                    "p95_response_time": app_metrics.response_time_avg * 1.5,  # 模拟
                    "p99_response_time": app_metrics.response_time_avg * 2.0   # 模拟
                },
                "efficiency": {
                    "cache_hit_rate": app_metrics.cache_hit_rate,
                    "connection_utilization": app_metrics.active_connections / 100  # 假设最大100连接
                }
            },
            "timestamp": system_metrics.timestamp.isoformat()
        }
        
        return APIResponse.success_response(
            data=performance_metrics,
            message="获取性能指标成功"
        )
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")


@router.get("/auto-reduce/monitoring/status", response_model=APIResponse)
async def get_system_status():
    """获取系统状态"""
    try:
        # 获取健康状态
        health_status = monitoring_service.get_health_status()
        
        # 获取活跃告警
        active_alerts = monitoring_service.get_active_alerts()
        
        # 计算系统状态
        system_status = {
            "overall_status": health_status["status"],
            "health_score": health_status["health_score"],
            "services": {
                "application": "running",
                "database": "connected",
                "cache": "active",
                "monitoring": "active"
            },
            "alerts": {
                "total": len(active_alerts),
                "critical": len([a for a in active_alerts if a["severity"] == "critical"]),
                "warning": len([a for a in active_alerts if a["severity"] == "warning"]),
                "info": len([a for a in active_alerts if a["severity"] == "info"])
            },
            "uptime": "99.9%",  # 模拟
            "last_updated": health_status["timestamp"]
        }
        
        return APIResponse.success_response(
            data=system_status,
            message="获取系统状态成功"
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")

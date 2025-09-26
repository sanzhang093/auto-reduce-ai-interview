"""
风险监控API
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any
from app.models.base import APIResponse
from app.services.risk_monitoring import risk_monitoring_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/auto-reduce/risk-monitoring/scan/{project_id}", response_model=APIResponse)
async def scan_project_risks(project_id: str = Path(..., description="项目ID")):
    """扫描项目风险"""
    try:
        logger.info(f"扫描项目 {project_id} 的风险")
        
        alerts = risk_monitoring_service.scan_project_risks(project_id)
        
        # 转换为字典格式
        alerts_data = [
            {
                "risk_id": alert.risk_id,
                "project_id": alert.project_id,
                "risk_title": alert.risk_title,
                "risk_level": alert.risk_level.value,
                "alert_type": alert.alert_type,
                "alert_message": alert.alert_message,
                "alert_time": alert.alert_time.isoformat(),
                "mitigation_suggestion": alert.mitigation_suggestion,
                "urgency_score": alert.urgency_score
            }
            for alert in alerts
        ]
        
        # 统计信息
        summary = {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.risk_level.value == "严重"]),
            "high_alerts": len([a for a in alerts if a.risk_level.value == "高"]),
            "medium_alerts": len([a for a in alerts if a.risk_level.value == "中"]),
            "low_alerts": len([a for a in alerts if a.risk_level.value == "低"])
        }
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "alerts": alerts_data,
                "summary": summary,
                "scan_time": alerts[0].alert_time.isoformat() if alerts else None
            },
            message=f"项目 {project_id} 风险扫描完成，发现 {len(alerts)} 个风险预警"
        )
    except Exception as e:
        logger.error(f"扫描项目风险失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"扫描项目风险失败: {str(e)}")


@router.get("/auto-reduce/risk-monitoring/analysis/{project_id}", response_model=APIResponse)
async def analyze_project_risks(project_id: str = Path(..., description="项目ID")):
    """分析项目风险"""
    try:
        logger.info(f"分析项目 {project_id} 的风险")
        
        analysis = risk_monitoring_service.analyze_project_risks(project_id)
        
        analysis_data = {
            "project_id": analysis.project_id,
            "total_risks": analysis.total_risks,
            "high_risks": analysis.high_risks,
            "medium_risks": analysis.medium_risks,
            "low_risks": analysis.low_risks,
            "risk_trend": analysis.risk_trend,
            "top_risk_categories": analysis.top_risk_categories,
            "risk_impact_assessment": analysis.risk_impact_assessment,
            "mitigation_recommendations": analysis.mitigation_recommendations
        }
        
        return APIResponse.success_response(
            data=analysis_data,
            message=f"项目 {project_id} 风险分析完成"
        )
    except Exception as e:
        logger.error(f"分析项目风险失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目风险失败: {str(e)}")


@router.get("/auto-reduce/risk-monitoring/report/{project_id}", response_model=APIResponse)
async def generate_risk_report(project_id: str = Path(..., description="项目ID")):
    """生成风险报告"""
    try:
        logger.info(f"生成项目 {project_id} 的风险报告")
        
        report = risk_monitoring_service.generate_risk_report(project_id)
        
        return APIResponse.success_response(
            data=report,
            message=f"项目 {project_id} 风险报告生成成功"
        )
    except ValueError as e:
        logger.warning(f"生成风险报告失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成风险报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成风险报告失败: {str(e)}")


@router.get("/auto-reduce/risk-monitoring/alerts/{project_id}", response_model=APIResponse)
async def get_risk_alerts(project_id: str = Path(..., description="项目ID")):
    """获取风险预警列表"""
    try:
        logger.info(f"获取项目 {project_id} 的风险预警")
        
        alerts = risk_monitoring_service.scan_project_risks(project_id)
        
        # 按紧急程度排序
        alerts.sort(key=lambda x: x.urgency_score, reverse=True)
        
        alerts_data = [
            {
                "risk_id": alert.risk_id,
                "project_id": alert.project_id,
                "risk_title": alert.risk_title,
                "risk_level": alert.risk_level.value,
                "alert_type": alert.alert_type,
                "alert_message": alert.alert_message,
                "alert_time": alert.alert_time.isoformat(),
                "mitigation_suggestion": alert.mitigation_suggestion,
                "urgency_score": alert.urgency_score
            }
            for alert in alerts
        ]
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "alerts": alerts_data,
                "total_count": len(alerts),
                "urgent_count": len([a for a in alerts if a.urgency_score >= 8])
            },
            message=f"获取项目 {project_id} 的风险预警成功"
        )
    except Exception as e:
        logger.error(f"获取风险预警失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取风险预警失败: {str(e)}")


@router.get("/auto-reduce/risk-monitoring/dashboard/{project_id}", response_model=APIResponse)
async def get_risk_dashboard(project_id: str = Path(..., description="项目ID")):
    """获取风险监控仪表板数据"""
    try:
        logger.info(f"获取项目 {project_id} 的风险监控仪表板")
        
        # 扫描风险
        alerts = risk_monitoring_service.scan_project_risks(project_id)
        
        # 分析风险
        analysis = risk_monitoring_service.analyze_project_risks(project_id)
        
        # 构建仪表板数据
        dashboard_data = {
            "project_id": project_id,
            "overview": {
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.risk_level.value == "严重"]),
                "high_alerts": len([a for a in alerts if a.risk_level.value == "高"]),
                "medium_alerts": len([a for a in alerts if a.risk_level.value == "中"]),
                "low_alerts": len([a for a in alerts if a.risk_level.value == "低"])
            },
            "risk_distribution": {
                "total_risks": analysis.total_risks,
                "high_risks": analysis.high_risks,
                "medium_risks": analysis.medium_risks,
                "low_risks": analysis.low_risks
            },
            "risk_trend": analysis.risk_trend,
            "top_categories": analysis.top_risk_categories,
            "recent_alerts": [
                {
                    "risk_title": alert.risk_title,
                    "risk_level": alert.risk_level.value,
                    "alert_type": alert.alert_type,
                    "alert_time": alert.alert_time.isoformat(),
                    "urgency_score": alert.urgency_score
                }
                for alert in sorted(alerts, key=lambda x: x.alert_time, reverse=True)[:5]
            ],
            "recommendations": analysis.mitigation_recommendations[:3]
        }
        
        return APIResponse.success_response(
            data=dashboard_data,
            message=f"获取项目 {project_id} 的风险监控仪表板成功"
        )
    except Exception as e:
        logger.error(f"获取风险监控仪表板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取风险监控仪表板失败: {str(e)}")


@router.get("/auto-reduce/risk-monitoring/thresholds", response_model=APIResponse)
async def get_risk_thresholds():
    """获取风险阈值配置"""
    try:
        thresholds = risk_monitoring_service.risk_thresholds
        
        return APIResponse.success_response(
            data=thresholds,
            message="获取风险阈值配置成功"
        )
    except Exception as e:
        logger.error(f"获取风险阈值配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取风险阈值配置失败: {str(e)}")


@router.get("/auto-reduce/risk-monitoring/statistics", response_model=APIResponse)
async def get_risk_statistics():
    """获取风险统计信息"""
    try:
        # 获取所有项目
        projects = risk_monitoring_service.db.read("projects")
        
        total_projects = len(projects)
        total_risks = 0
        total_alerts = 0
        high_risk_projects = 0
        
        for project in projects:
            project_id = project["project_id"]
            try:
                # 获取项目风险
                risks = risk_monitoring_service.db.get_by_field("risks", "project_id", project_id)
                total_risks += len(risks)
                
                # 扫描风险预警
                alerts = risk_monitoring_service.scan_project_risks(project_id)
                total_alerts += len(alerts)
                
                # 检查是否有高风险
                high_risks = [r for r in risks if r.get("risk_level") in ["高", "严重"]]
                if len(high_risks) > 0:
                    high_risk_projects += 1
            except:
                continue
        
        statistics = {
            "total_projects": total_projects,
            "total_risks": total_risks,
            "total_alerts": total_alerts,
            "high_risk_projects": high_risk_projects,
            "average_risks_per_project": total_risks / total_projects if total_projects > 0 else 0,
            "average_alerts_per_project": total_alerts / total_projects if total_projects > 0 else 0,
            "high_risk_project_ratio": high_risk_projects / total_projects if total_projects > 0 else 0
        }
        
        return APIResponse.success_response(
            data=statistics,
            message="获取风险统计信息成功"
        )
    except Exception as e:
        logger.error(f"获取风险统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取风险统计信息失败: {str(e)}")

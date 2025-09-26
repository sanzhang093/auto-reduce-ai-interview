"""
智能分析API
"""
from fastapi import APIRouter, HTTPException, Query, Path, Body
from typing import List, Dict, Any, Optional
from app.models.base import APIResponse
from app.services.ai_analysis import ai_analysis_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/auto-reduce/ai-analysis/trends/{project_id}", response_model=APIResponse)
async def analyze_project_trends(
    project_id: str = Path(..., description="项目ID"),
    days: int = Query(default=30, description="分析天数")
):
    """分析项目趋势"""
    try:
        logger.info(f"分析项目 {project_id} 的趋势")
        
        trends = await ai_analysis_service.analyze_project_trends(project_id, days)
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "analysis_days": days,
                "trends": [
                    {
                        "metric_name": trend.metric_name,
                        "current_value": trend.current_value,
                        "previous_value": trend.previous_value,
                        "trend_direction": trend.trend_direction,
                        "trend_percentage": trend.trend_percentage,
                        "trend_description": trend.trend_description,
                        "prediction": trend.prediction
                    }
                    for trend in trends
                ],
                "trend_count": len(trends)
            },
            message=f"项目 {project_id} 趋势分析完成"
        )
    except Exception as e:
        logger.error(f"分析项目趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目趋势失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/insights/{project_id}", response_model=APIResponse)
async def generate_project_insights(project_id: str = Path(..., description="项目ID")):
    """生成项目洞察"""
    try:
        logger.info(f"生成项目 {project_id} 的洞察")
        
        insights = await ai_analysis_service.generate_project_insights(project_id)
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "insights": [
                    {
                        "insight_type": insight.insight_type,
                        "title": insight.title,
                        "description": insight.description,
                        "impact_level": insight.impact_level,
                        "confidence": insight.confidence,
                        "recommendations": insight.recommendations,
                        "data_support": insight.data_support
                    }
                    for insight in insights
                ],
                "insight_count": len(insights)
            },
            message=f"项目 {project_id} 洞察生成完成"
        )
    except Exception as e:
        logger.error(f"生成项目洞察失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成项目洞察失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/recommendations/{project_id}", response_model=APIResponse)
async def generate_ai_recommendations(project_id: str = Path(..., description="项目ID")):
    """生成AI建议"""
    try:
        logger.info(f"生成项目 {project_id} 的AI建议")
        
        recommendations = await ai_analysis_service.generate_ai_recommendations(project_id)
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "recommendations": [
                    {
                        "recommendation_type": rec.recommendation_type,
                        "title": rec.title,
                        "description": rec.description,
                        "priority": rec.priority,
                        "action_items": rec.action_items,
                        "expected_impact": rec.expected_impact,
                        "implementation_difficulty": rec.implementation_difficulty
                    }
                    for rec in recommendations
                ],
                "recommendation_count": len(recommendations)
            },
            message=f"项目 {project_id} AI建议生成完成"
        )
    except Exception as e:
        logger.error(f"生成AI建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成AI建议失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/comprehensive/{project_id}", response_model=APIResponse)
async def generate_comprehensive_analysis(project_id: str = Path(..., description="项目ID")):
    """生成综合分析报告"""
    try:
        logger.info(f"生成项目 {project_id} 的综合分析报告")
        
        analysis = await ai_analysis_service.generate_comprehensive_analysis(project_id)
        
        return APIResponse.success_response(
            data=analysis,
            message=f"项目 {project_id} 综合分析报告生成完成"
        )
    except Exception as e:
        logger.error(f"生成综合分析报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成综合分析报告失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/performance/{project_id}", response_model=APIResponse)
async def analyze_project_performance(project_id: str = Path(..., description="项目ID")):
    """分析项目性能"""
    try:
        logger.info(f"分析项目 {project_id} 的性能")
        
        # 获取性能洞察
        insights = await ai_analysis_service.generate_project_insights(project_id)
        performance_insight = next((insight for insight in insights if insight.insight_type == "performance"), None)
        
        if performance_insight:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "performance_analysis": {
                        "title": performance_insight.title,
                        "description": performance_insight.description,
                        "impact_level": performance_insight.impact_level,
                        "confidence": performance_insight.confidence,
                        "recommendations": performance_insight.recommendations,
                        "data_support": performance_insight.data_support
                    }
                },
                message=f"项目 {project_id} 性能分析完成"
            )
        else:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "performance_analysis": None
                },
                message="项目性能数据不足，无法生成分析"
            )
    except Exception as e:
        logger.error(f"分析项目性能失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目性能失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/risk/{project_id}", response_model=APIResponse)
async def analyze_project_risk(project_id: str = Path(..., description="项目ID")):
    """分析项目风险"""
    try:
        logger.info(f"分析项目 {project_id} 的风险")
        
        # 获取风险洞察
        insights = await ai_analysis_service.generate_project_insights(project_id)
        risk_insight = next((insight for insight in insights if insight.insight_type == "risk"), None)
        
        if risk_insight:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "risk_analysis": {
                        "title": risk_insight.title,
                        "description": risk_insight.description,
                        "impact_level": risk_insight.impact_level,
                        "confidence": risk_insight.confidence,
                        "recommendations": risk_insight.recommendations,
                        "data_support": risk_insight.data_support
                    }
                },
                message=f"项目 {project_id} 风险分析完成"
            )
        else:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "risk_analysis": None
                },
                message="项目风险数据不足，无法生成分析"
            )
    except Exception as e:
        logger.error(f"分析项目风险失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目风险失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/efficiency/{project_id}", response_model=APIResponse)
async def analyze_project_efficiency(project_id: str = Path(..., description="项目ID")):
    """分析项目效率"""
    try:
        logger.info(f"分析项目 {project_id} 的效率")
        
        # 获取效率洞察
        insights = await ai_analysis_service.generate_project_insights(project_id)
        efficiency_insight = next((insight for insight in insights if insight.insight_type == "efficiency"), None)
        
        if efficiency_insight:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "efficiency_analysis": {
                        "title": efficiency_insight.title,
                        "description": efficiency_insight.description,
                        "impact_level": efficiency_insight.impact_level,
                        "confidence": efficiency_insight.confidence,
                        "recommendations": efficiency_insight.recommendations,
                        "data_support": efficiency_insight.data_support
                    }
                },
                message=f"项目 {project_id} 效率分析完成"
            )
        else:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "efficiency_analysis": None
                },
                message="项目效率数据不足，无法生成分析"
            )
    except Exception as e:
        logger.error(f"分析项目效率失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目效率失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/quality/{project_id}", response_model=APIResponse)
async def analyze_project_quality(project_id: str = Path(..., description="项目ID")):
    """分析项目质量"""
    try:
        logger.info(f"分析项目 {project_id} 的质量")
        
        # 获取质量洞察
        insights = await ai_analysis_service.generate_project_insights(project_id)
        quality_insight = next((insight for insight in insights if insight.insight_type == "quality"), None)
        
        if quality_insight:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "quality_analysis": {
                        "title": quality_insight.title,
                        "description": quality_insight.description,
                        "impact_level": quality_insight.impact_level,
                        "confidence": quality_insight.confidence,
                        "recommendations": quality_insight.recommendations,
                        "data_support": quality_insight.data_support
                    }
                },
                message=f"项目 {project_id} 质量分析完成"
            )
        else:
            return APIResponse.success_response(
                data={
                    "project_id": project_id,
                    "quality_analysis": None
                },
                message="项目质量数据不足，无法生成分析"
            )
    except Exception as e:
        logger.error(f"分析项目质量失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目质量失败: {str(e)}")


@router.post("/auto-reduce/ai-analysis/custom", response_model=APIResponse)
async def custom_analysis(
    project_id: str = Body(..., description="项目ID"),
    analysis_type: str = Body(..., description="分析类型"),
    parameters: Dict[str, Any] = Body(default={}, description="分析参数")
):
    """自定义分析"""
    try:
        logger.info(f"执行项目 {project_id} 的自定义分析: {analysis_type}")
        
        # 根据分析类型执行不同的分析
        if analysis_type == "trends":
            days = parameters.get("days", 30)
            trends = await ai_analysis_service.analyze_project_trends(project_id, days)
            result = {
                "analysis_type": "trends",
                "trends": [asdict(trend) for trend in trends]
            }
        elif analysis_type == "insights":
            insights = await ai_analysis_service.generate_project_insights(project_id)
            result = {
                "analysis_type": "insights",
                "insights": [asdict(insight) for insight in insights]
            }
        elif analysis_type == "recommendations":
            recommendations = await ai_analysis_service.generate_ai_recommendations(project_id)
            result = {
                "analysis_type": "recommendations",
                "recommendations": [asdict(rec) for rec in recommendations]
            }
        elif analysis_type == "comprehensive":
            analysis = await ai_analysis_service.generate_comprehensive_analysis(project_id)
            result = {
                "analysis_type": "comprehensive",
                "analysis": analysis
            }
        else:
            raise HTTPException(status_code=400, detail=f"不支持的分析类型: {analysis_type}")
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "analysis_type": analysis_type,
                "parameters": parameters,
                "result": result
            },
            message=f"项目 {project_id} 自定义分析完成"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"执行自定义分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"执行自定义分析失败: {str(e)}")


@router.get("/auto-reduce/ai-analysis/dashboard/{project_id}", response_model=APIResponse)
async def get_ai_analysis_dashboard(project_id: str = Path(..., description="项目ID")):
    """获取AI分析仪表板"""
    try:
        logger.info(f"获取项目 {project_id} 的AI分析仪表板")
        
        # 获取各种分析结果
        trends = await ai_analysis_service.analyze_project_trends(project_id)
        insights = await ai_analysis_service.generate_project_insights(project_id)
        recommendations = await ai_analysis_service.generate_ai_recommendations(project_id)
        
        # 计算综合评分
        overall_score = ai_analysis_service._calculate_overall_score(trends, insights, recommendations)
        
        # 构建仪表板数据
        dashboard_data = {
            "project_id": project_id,
            "overall_score": overall_score,
            "trends_summary": {
                "total_trends": len(trends),
                "positive_trends": len([t for t in trends if t.trend_direction == "上升"]),
                "negative_trends": len([t for t in trends if t.trend_direction == "下降"]),
                "stable_trends": len([t for t in trends if t.trend_direction == "稳定"])
            },
            "insights_summary": {
                "total_insights": len(insights),
                "high_impact": len([i for i in insights if i.impact_level == "高"]),
                "medium_impact": len([i for i in insights if i.impact_level == "中"]),
                "low_impact": len([i for i in insights if i.impact_level == "低"])
            },
            "recommendations_summary": {
                "total_recommendations": len(recommendations),
                "high_priority": len([r for r in recommendations if r.priority == "高"]),
                "medium_priority": len([r for r in recommendations if r.priority == "中"]),
                "low_priority": len([r for r in recommendations if r.priority == "低"])
            },
            "recent_trends": [asdict(trend) for trend in trends[:3]],
            "key_insights": [asdict(insight) for insight in insights[:3]],
            "top_recommendations": [asdict(rec) for rec in recommendations[:3]]
        }
        
        return APIResponse.success_response(
            data=dashboard_data,
            message=f"项目 {project_id} AI分析仪表板获取成功"
        )
    except Exception as e:
        logger.error(f"获取AI分析仪表板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取AI分析仪表板失败: {str(e)}")


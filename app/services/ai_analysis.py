"""
智能分析服务
"""
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from app.models.enums import TaskStatus, RiskLevel, IssueCategory
from app.utils.logger import get_logger
from app.services.database_service import database_service
from app.services.qwen_agent import qwen_agent_service

logger = get_logger(__name__)


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    metric_name: str
    current_value: float
    previous_value: float
    trend_direction: str  # "上升", "下降", "稳定"
    trend_percentage: float
    trend_description: str
    prediction: Optional[str] = None


@dataclass
class ProjectInsight:
    """项目洞察"""
    insight_type: str  # "performance", "risk", "efficiency", "quality"
    title: str
    description: str
    impact_level: str  # "高", "中", "低"
    confidence: float
    recommendations: List[str]
    data_support: Dict[str, Any]


@dataclass
class AIRecommendation:
    """AI建议"""
    recommendation_type: str  # "task", "risk", "resource", "schedule"
    title: str
    description: str
    priority: str  # "高", "中", "低"
    action_items: List[str]
    expected_impact: str
    implementation_difficulty: str  # "简单", "中等", "复杂"


class AIAnalysisService:
    """智能分析服务"""
    
    def __init__(self):
        """初始化服务"""
        self.db = database_service.get_database()
        logger.info("智能分析服务初始化完成")
    
    async def analyze_project_trends(self, project_id: str, days: int = 30) -> List[TrendAnalysis]:
        """分析项目趋势"""
        try:
            logger.info(f"分析项目 {project_id} 的趋势")
            
            trends = []
            
            # 分析任务完成趋势
            task_trend = await self._analyze_task_completion_trend(project_id, days)
            if task_trend:
                trends.append(task_trend)
            
            # 分析进度趋势
            progress_trend = await self._analyze_progress_trend(project_id, days)
            if progress_trend:
                trends.append(progress_trend)
            
            # 分析风险趋势
            risk_trend = await self._analyze_risk_trend(project_id, days)
            if risk_trend:
                trends.append(risk_trend)
            
            # 分析问题解决趋势
            issue_trend = await self._analyze_issue_resolution_trend(project_id, days)
            if issue_trend:
                trends.append(issue_trend)
            
            logger.info(f"项目 {project_id} 趋势分析完成，共分析 {len(trends)} 个趋势")
            return trends
        except Exception as e:
            logger.error(f"分析项目趋势失败: {str(e)}")
            raise
    
    async def _analyze_task_completion_trend(self, project_id: str, days: int) -> Optional[TrendAnalysis]:
        """分析任务完成趋势"""
        try:
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            if not tasks:
                return None
            
            # 计算当前完成率
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
            current_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # 模拟历史数据（实际项目中应该从历史记录获取）
            previous_completion_rate = max(0, current_completion_rate - 10)
            
            # 计算趋势
            trend_direction = "上升" if current_completion_rate > previous_completion_rate else "下降" if current_completion_rate < previous_completion_rate else "稳定"
            trend_percentage = abs(current_completion_rate - previous_completion_rate)
            
            # 生成趋势描述
            trend_description = f"任务完成率从 {previous_completion_rate:.1f}% {trend_direction}到 {current_completion_rate:.1f}%"
            
            # 使用AI生成预测
            prediction_prompt = f"""
            基于以下任务完成趋势数据，预测未来趋势：
            当前完成率: {current_completion_rate:.1f}%
            历史完成率: {previous_completion_rate:.1f}%
            趋势方向: {trend_direction}
            
            请生成简洁的趋势预测。
            """
            
            ai_response = await qwen_agent_service._call_qwen_api("", prediction_prompt)
            prediction = ai_response.get("content", "趋势预测需要更多数据")
            
            return TrendAnalysis(
                metric_name="任务完成率",
                current_value=current_completion_rate,
                previous_value=previous_completion_rate,
                trend_direction=trend_direction,
                trend_percentage=trend_percentage,
                trend_description=trend_description,
                prediction=prediction
            )
        except Exception as e:
            logger.error(f"分析任务完成趋势失败: {str(e)}")
            return None
    
    async def _analyze_progress_trend(self, project_id: str, days: int) -> Optional[TrendAnalysis]:
        """分析进度趋势"""
        try:
            # 获取项目数据
            project = self.db.read("projects", project_id)
            if not project:
                return None
            
            current_progress = project.get("progress_percentage", 0)
            
            # 模拟历史进度（实际项目中应该从历史记录获取）
            previous_progress = max(0, current_progress - 5)
            
            # 计算趋势
            trend_direction = "上升" if current_progress > previous_progress else "下降" if current_progress < previous_progress else "稳定"
            trend_percentage = abs(current_progress - previous_progress)
            
            trend_description = f"项目进度从 {previous_progress:.1f}% {trend_direction}到 {current_progress:.1f}%"
            
            return TrendAnalysis(
                metric_name="项目进度",
                current_value=current_progress,
                previous_value=previous_progress,
                trend_direction=trend_direction,
                trend_percentage=trend_percentage,
                trend_description=trend_description
            )
        except Exception as e:
            logger.error(f"分析进度趋势失败: {str(e)}")
            return None
    
    async def _analyze_risk_trend(self, project_id: str, days: int) -> Optional[TrendAnalysis]:
        """分析风险趋势"""
        try:
            # 获取风险数据
            risks = self.db.get_by_field("risks", "project_id", project_id)
            
            if not risks:
                return None
            
            # 计算当前高风险数量
            current_high_risks = len([r for r in risks if r.get("risk_level") in ["高", "严重"]])
            
            # 模拟历史数据
            previous_high_risks = max(0, current_high_risks - 1)
            
            # 计算趋势
            trend_direction = "上升" if current_high_risks > previous_high_risks else "下降" if current_high_risks < previous_high_risks else "稳定"
            trend_percentage = abs(current_high_risks - previous_high_risks)
            
            trend_description = f"高风险数量从 {previous_high_risks} 个 {trend_direction}到 {current_high_risks} 个"
            
            return TrendAnalysis(
                metric_name="高风险数量",
                current_value=current_high_risks,
                previous_value=previous_high_risks,
                trend_direction=trend_direction,
                trend_percentage=trend_percentage,
                trend_description=trend_description
            )
        except Exception as e:
            logger.error(f"分析风险趋势失败: {str(e)}")
            return None
    
    async def _analyze_issue_resolution_trend(self, project_id: str, days: int) -> Optional[TrendAnalysis]:
        """分析问题解决趋势"""
        try:
            # 获取问题数据
            issues = self.db.get_by_field("issues", "project_id", project_id)
            
            if not issues:
                return None
            
            # 计算当前未解决问题数量
            current_open_issues = len([i for i in issues if i.get("status") not in ["已解决", "已关闭"]])
            
            # 模拟历史数据
            previous_open_issues = max(0, current_open_issues + 2)
            
            # 计算趋势
            trend_direction = "下降" if current_open_issues < previous_open_issues else "上升" if current_open_issues > previous_open_issues else "稳定"
            trend_percentage = abs(current_open_issues - previous_open_issues)
            
            trend_description = f"未解决问题从 {previous_open_issues} 个 {trend_direction}到 {current_open_issues} 个"
            
            return TrendAnalysis(
                metric_name="未解决问题数量",
                current_value=current_open_issues,
                previous_value=previous_open_issues,
                trend_direction=trend_direction,
                trend_percentage=trend_percentage,
                trend_description=trend_description
            )
        except Exception as e:
            logger.error(f"分析问题解决趋势失败: {str(e)}")
            return None
    
    async def generate_project_insights(self, project_id: str) -> List[ProjectInsight]:
        """生成项目洞察"""
        try:
            logger.info(f"生成项目 {project_id} 的洞察")
            
            insights = []
            
            # 性能洞察
            performance_insight = await self._generate_performance_insight(project_id)
            if performance_insight:
                insights.append(performance_insight)
            
            # 风险洞察
            risk_insight = await self._generate_risk_insight(project_id)
            if risk_insight:
                insights.append(risk_insight)
            
            # 效率洞察
            efficiency_insight = await self._generate_efficiency_insight(project_id)
            if efficiency_insight:
                insights.append(efficiency_insight)
            
            # 质量洞察
            quality_insight = await self._generate_quality_insight(project_id)
            if quality_insight:
                insights.append(quality_insight)
            
            logger.info(f"项目 {project_id} 洞察生成完成，共生成 {len(insights)} 个洞察")
            return insights
        except Exception as e:
            logger.error(f"生成项目洞察失败: {str(e)}")
            raise
    
    async def _generate_performance_insight(self, project_id: str) -> Optional[ProjectInsight]:
        """生成性能洞察"""
        try:
            # 获取项目数据
            project = self.db.read("projects", project_id)
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            if not project or not tasks:
                return None
            
            # 计算性能指标
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # 使用AI生成洞察
            insight_prompt = f"""
            基于以下项目性能数据，生成性能洞察：
            项目名称: {project.get('project_name', '')}
            总任务数: {total_tasks}
            已完成任务: {completed_tasks}
            完成率: {completion_rate:.1f}%
            
            请生成简洁的性能洞察，包括标题、描述、影响级别和建议。
            """
            
            ai_response = await qwen_agent_service._call_qwen_api("", insight_prompt)
            ai_content = ai_response.get("content", "")
            
            # 解析AI返回的内容（简化版）
            title = "项目性能分析"
            description = f"项目完成率为 {completion_rate:.1f}%，共 {total_tasks} 个任务，已完成 {completed_tasks} 个"
            impact_level = "高" if completion_rate < 50 else "中" if completion_rate < 80 else "低"
            
            recommendations = [
                "优化任务分配和优先级",
                "加强团队协作和沟通",
                "定期检查项目进度"
            ]
            
            return ProjectInsight(
                insight_type="performance",
                title=title,
                description=description,
                impact_level=impact_level,
                confidence=0.8,
                recommendations=recommendations,
                data_support={
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_rate": completion_rate
                }
            )
        except Exception as e:
            logger.error(f"生成性能洞察失败: {str(e)}")
            return None
    
    async def _generate_risk_insight(self, project_id: str) -> Optional[ProjectInsight]:
        """生成风险洞察"""
        try:
            # 获取风险数据
            risks = self.db.get_by_field("risks", "project_id", project_id)
            
            if not risks:
                return None
            
            # 计算风险指标
            total_risks = len(risks)
            high_risks = len([r for r in risks if r.get("risk_level") in ["高", "严重"]])
            risk_ratio = (high_risks / total_risks * 100) if total_risks > 0 else 0
            
            title = "项目风险分析"
            description = f"项目共有 {total_risks} 个风险，其中 {high_risks} 个高风险，高风险比例 {risk_ratio:.1f}%"
            impact_level = "高" if risk_ratio > 30 else "中" if risk_ratio > 10 else "低"
            
            recommendations = [
                "制定高风险缓解计划",
                "加强风险监控和预警",
                "定期评估风险状态"
            ]
            
            return ProjectInsight(
                insight_type="risk",
                title=title,
                description=description,
                impact_level=impact_level,
                confidence=0.9,
                recommendations=recommendations,
                data_support={
                    "total_risks": total_risks,
                    "high_risks": high_risks,
                    "risk_ratio": risk_ratio
                }
            )
        except Exception as e:
            logger.error(f"生成风险洞察失败: {str(e)}")
            return None
    
    async def _generate_efficiency_insight(self, project_id: str) -> Optional[ProjectInsight]:
        """生成效率洞察"""
        try:
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            if not tasks:
                return None
            
            # 计算效率指标
            overdue_tasks = len([t for t in tasks if self._is_task_overdue(t)])
            efficiency_rate = ((len(tasks) - overdue_tasks) / len(tasks) * 100) if tasks else 0
            
            title = "项目效率分析"
            description = f"项目效率率为 {efficiency_rate:.1f}%，共有 {overdue_tasks} 个逾期任务"
            impact_level = "高" if efficiency_rate < 70 else "中" if efficiency_rate < 90 else "低"
            
            recommendations = [
                "优化任务时间估算",
                "加强进度监控",
                "及时调整资源分配"
            ]
            
            return ProjectInsight(
                insight_type="efficiency",
                title=title,
                description=description,
                impact_level=impact_level,
                confidence=0.7,
                recommendations=recommendations,
                data_support={
                    "total_tasks": len(tasks),
                    "overdue_tasks": overdue_tasks,
                    "efficiency_rate": efficiency_rate
                }
            )
        except Exception as e:
            logger.error(f"生成效率洞察失败: {str(e)}")
            return None
    
    async def _generate_quality_insight(self, project_id: str) -> Optional[ProjectInsight]:
        """生成质量洞察"""
        try:
            # 获取问题数据
            issues = self.db.get_by_field("issues", "project_id", project_id)
            
            if not issues:
                return None
            
            # 计算质量指标
            total_issues = len(issues)
            resolved_issues = len([i for i in issues if i.get("status") in ["已解决", "已关闭"]])
            quality_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0
            
            title = "项目质量分析"
            description = f"项目质量率为 {quality_rate:.1f}%，共 {total_issues} 个问题，已解决 {resolved_issues} 个"
            impact_level = "高" if quality_rate < 60 else "中" if quality_rate < 80 else "低"
            
            recommendations = [
                "加强质量检查流程",
                "提升问题解决效率",
                "建立质量监控机制"
            ]
            
            return ProjectInsight(
                insight_type="quality",
                title=title,
                description=description,
                impact_level=impact_level,
                confidence=0.8,
                recommendations=recommendations,
                data_support={
                    "total_issues": total_issues,
                    "resolved_issues": resolved_issues,
                    "quality_rate": quality_rate
                }
            )
        except Exception as e:
            logger.error(f"生成质量洞察失败: {str(e)}")
            return None
    
    def _is_task_overdue(self, task: Dict[str, Any]) -> bool:
        """判断任务是否逾期"""
        due_date = task.get("due_date")
        if not due_date:
            return False
        
        status = task.get("status", "")
        if status in ["已完成", "已取消"]:
            return False
        
        # 简化日期比较
        try:
            if isinstance(due_date, str):
                due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            else:
                due_dt = due_date
            
            return due_dt < datetime.now()
        except:
            return False
    
    async def generate_ai_recommendations(self, project_id: str) -> List[AIRecommendation]:
        """生成AI建议"""
        try:
            logger.info(f"生成项目 {project_id} 的AI建议")
            
            recommendations = []
            
            # 任务建议
            task_recommendation = await self._generate_task_recommendation(project_id)
            if task_recommendation:
                recommendations.append(task_recommendation)
            
            # 风险建议
            risk_recommendation = await self._generate_risk_recommendation(project_id)
            if risk_recommendation:
                recommendations.append(risk_recommendation)
            
            # 资源建议
            resource_recommendation = await self._generate_resource_recommendation(project_id)
            if resource_recommendation:
                recommendations.append(resource_recommendation)
            
            # 进度建议
            schedule_recommendation = await self._generate_schedule_recommendation(project_id)
            if schedule_recommendation:
                recommendations.append(schedule_recommendation)
            
            logger.info(f"项目 {project_id} AI建议生成完成，共生成 {len(recommendations)} 个建议")
            return recommendations
        except Exception as e:
            logger.error(f"生成AI建议失败: {str(e)}")
            raise
    
    async def _generate_task_recommendation(self, project_id: str) -> Optional[AIRecommendation]:
        """生成任务建议"""
        try:
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            if not tasks:
                return None
            
            # 分析任务状态
            pending_tasks = len([t for t in tasks if t.get("status") == "待开始"])
            overdue_tasks = len([t for t in tasks if self._is_task_overdue(t)])
            
            # 使用AI生成建议
            recommendation_prompt = f"""
            基于以下任务数据，生成任务管理建议：
            总任务数: {len(tasks)}
            待开始任务: {pending_tasks}
            逾期任务: {overdue_tasks}
            
            请生成任务管理建议，包括标题、描述、优先级、行动项和预期影响。
            """
            
            ai_response = await qwen_agent_service._call_qwen_api("", recommendation_prompt)
            ai_content = ai_response.get("content", "")
            
            # 解析AI返回的内容（简化版）
            title = "任务管理优化建议"
            description = f"项目有 {pending_tasks} 个待开始任务和 {overdue_tasks} 个逾期任务，需要优化任务管理"
            priority = "高" if overdue_tasks > 3 else "中" if overdue_tasks > 0 else "低"
            
            action_items = [
                "重新评估任务优先级",
                "分配更多资源给逾期任务",
                "优化任务依赖关系"
            ]
            
            expected_impact = "提高任务完成效率，减少逾期风险"
            implementation_difficulty = "中等"
            
            return AIRecommendation(
                recommendation_type="task",
                title=title,
                description=description,
                priority=priority,
                action_items=action_items,
                expected_impact=expected_impact,
                implementation_difficulty=implementation_difficulty
            )
        except Exception as e:
            logger.error(f"生成任务建议失败: {str(e)}")
            return None
    
    async def _generate_risk_recommendation(self, project_id: str) -> Optional[AIRecommendation]:
        """生成风险建议"""
        try:
            # 获取风险数据
            risks = self.db.get_by_field("risks", "project_id", project_id)
            
            if not risks:
                return None
            
            # 分析风险状态
            high_risks = len([r for r in risks if r.get("risk_level") in ["高", "严重"]])
            unmitigated_risks = len([r for r in risks if r.get("status") == "Open"])
            
            title = "风险管理优化建议"
            description = f"项目有 {high_risks} 个高风险和 {unmitigated_risks} 个未缓解风险，需要加强风险管理"
            priority = "高" if high_risks > 2 else "中" if high_risks > 0 else "低"
            
            action_items = [
                "制定高风险缓解计划",
                "建立风险监控机制",
                "定期评估风险状态"
            ]
            
            expected_impact = "降低项目风险，提高项目成功率"
            implementation_difficulty = "中等"
            
            return AIRecommendation(
                recommendation_type="risk",
                title=title,
                description=description,
                priority=priority,
                action_items=action_items,
                expected_impact=expected_impact,
                implementation_difficulty=implementation_difficulty
            )
        except Exception as e:
            logger.error(f"生成风险建议失败: {str(e)}")
            return None
    
    async def _generate_resource_recommendation(self, project_id: str) -> Optional[AIRecommendation]:
        """生成资源建议"""
        try:
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            if not tasks:
                return None
            
            # 分析资源分配
            user_tasks = {}
            for task in tasks:
                assigned_to = task.get("assigned_to")
                if assigned_to:
                    user_tasks[assigned_to] = user_tasks.get(assigned_to, 0) + 1
            
            max_tasks = max(user_tasks.values()) if user_tasks else 0
            min_tasks = min(user_tasks.values()) if user_tasks else 0
            workload_imbalance = max_tasks - min_tasks
            
            title = "资源分配优化建议"
            description = f"团队成员任务分配不均衡，最大差异为 {workload_imbalance} 个任务"
            priority = "高" if workload_imbalance > 5 else "中" if workload_imbalance > 2 else "低"
            
            action_items = [
                "重新平衡任务分配",
                "考虑增加团队成员",
                "优化工作流程"
            ]
            
            expected_impact = "提高团队效率，减少工作负载不均衡"
            implementation_difficulty = "简单"
            
            return AIRecommendation(
                recommendation_type="resource",
                title=title,
                description=description,
                priority=priority,
                action_items=action_items,
                expected_impact=expected_impact,
                implementation_difficulty=implementation_difficulty
            )
        except Exception as e:
            logger.error(f"生成资源建议失败: {str(e)}")
            return None
    
    async def _generate_schedule_recommendation(self, project_id: str) -> Optional[AIRecommendation]:
        """生成进度建议"""
        try:
            # 获取项目数据
            project = self.db.read("projects", project_id)
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            if not project or not tasks:
                return None
            
            # 分析进度状态
            current_progress = project.get("progress_percentage", 0)
            overdue_tasks = len([t for t in tasks if self._is_task_overdue(t)])
            
            title = "项目进度优化建议"
            description = f"项目进度为 {current_progress:.1f}%，有 {overdue_tasks} 个逾期任务，需要优化进度管理"
            priority = "高" if current_progress < 50 or overdue_tasks > 3 else "中" if current_progress < 80 or overdue_tasks > 0 else "低"
            
            action_items = [
                "重新评估项目时间线",
                "优化任务优先级",
                "加强进度监控"
            ]
            
            expected_impact = "提高项目进度，确保按时交付"
            implementation_difficulty = "中等"
            
            return AIRecommendation(
                recommendation_type="schedule",
                title=title,
                description=description,
                priority=priority,
                action_items=action_items,
                expected_impact=expected_impact,
                implementation_difficulty=implementation_difficulty
            )
        except Exception as e:
            logger.error(f"生成进度建议失败: {str(e)}")
            return None
    
    async def generate_comprehensive_analysis(self, project_id: str) -> Dict[str, Any]:
        """生成综合分析报告"""
        try:
            logger.info(f"生成项目 {project_id} 的综合分析报告")
            
            # 获取各种分析结果
            trends = await self.analyze_project_trends(project_id)
            insights = await self.generate_project_insights(project_id)
            recommendations = await self.generate_ai_recommendations(project_id)
            
            # 生成综合评分
            overall_score = self._calculate_overall_score(trends, insights, recommendations)
            
            # 生成总结
            summary = await self._generate_analysis_summary(project_id, trends, insights, recommendations)
            
            return {
                "project_id": project_id,
                "analysis_date": datetime.now().isoformat(),
                "overall_score": overall_score,
                "summary": summary,
                "trends": [asdict(trend) for trend in trends],
                "insights": [asdict(insight) for insight in insights],
                "recommendations": [asdict(rec) for rec in recommendations],
                "analysis_metadata": {
                    "trend_count": len(trends),
                    "insight_count": len(insights),
                    "recommendation_count": len(recommendations)
                }
            }
        except Exception as e:
            logger.error(f"生成综合分析报告失败: {str(e)}")
            raise
    
    def _calculate_overall_score(self, trends: List[TrendAnalysis], 
                                insights: List[ProjectInsight], 
                                recommendations: List[AIRecommendation]) -> float:
        """计算综合评分"""
        try:
            score = 0.0
            total_weight = 0.0
            
            # 趋势评分
            for trend in trends:
                if trend.trend_direction == "上升":
                    score += 0.8
                elif trend.trend_direction == "稳定":
                    score += 0.6
                else:
                    score += 0.4
                total_weight += 1.0
            
            # 洞察评分
            for insight in insights:
                if insight.impact_level == "低":
                    score += 0.8
                elif insight.impact_level == "中":
                    score += 0.6
                else:
                    score += 0.4
                total_weight += 1.0
            
            # 建议评分
            for rec in recommendations:
                if rec.priority == "低":
                    score += 0.8
                elif rec.priority == "中":
                    score += 0.6
                else:
                    score += 0.4
                total_weight += 1.0
            
            return (score / total_weight * 100) if total_weight > 0 else 0.0
        except Exception as e:
            logger.error(f"计算综合评分失败: {str(e)}")
            return 0.0
    
    async def _generate_analysis_summary(self, project_id: str, trends: List[TrendAnalysis], 
                                       insights: List[ProjectInsight], 
                                       recommendations: List[AIRecommendation]) -> str:
        """生成分析总结"""
        try:
            summary_prompt = f"""
            基于以下项目分析结果，生成综合分析总结：
            
            趋势分析:
            {[trend.trend_description for trend in trends]}
            
            项目洞察:
            {[insight.description for insight in insights]}
            
            AI建议:
            {[rec.description for rec in recommendations]}
            
            请生成简洁的项目分析总结。
            """
            
            ai_response = await qwen_agent_service._call_qwen_api("", summary_prompt)
            return ai_response.get("content", "项目分析总结生成中...")
        except Exception as e:
            logger.error(f"生成分析总结失败: {str(e)}")
            return "项目分析总结生成失败"


# 创建全局服务实例
ai_analysis_service = AIAnalysisService()


"""
风险监控服务
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.models.risk import RiskCreate, RiskCategory, RiskLevel
from app.models.enums import TaskStatus, IssueCategory
from app.utils.logger import get_logger
from app.utils.helpers import generate_id
from app.services.database_service import database_service

logger = get_logger(__name__)


@dataclass
class RiskAlert:
    """风险预警"""
    risk_id: str
    project_id: str
    risk_title: str
    risk_level: RiskLevel
    alert_type: str
    alert_message: str
    alert_time: datetime
    mitigation_suggestion: str
    urgency_score: int


@dataclass
class RiskAnalysis:
    """风险分析结果"""
    project_id: str
    total_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int
    risk_trend: str  # "上升", "下降", "稳定"
    top_risk_categories: List[Tuple[str, int]]
    risk_impact_assessment: Dict[str, Any]
    mitigation_recommendations: List[str]


class RiskMonitoringService:
    """风险监控服务"""
    
    def __init__(self):
        """初始化服务"""
        self.db = database_service.get_database()
        self.risk_thresholds = {
            'schedule_delay_days': 3,      # 进度延期天数阈值
            'completion_rate_low': 0.6,    # 完成率低阈值
            'blocked_task_ratio': 0.2,     # 阻塞任务比例阈值
            'overdue_task_ratio': 0.15,    # 逾期任务比例阈值
            'high_risk_count': 3,          # 高风险数量阈值
            'issue_escalation_days': 7     # 问题升级天数阈值
        }
        logger.info("风险监控服务初始化完成")
    
    def scan_project_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描项目风险"""
        try:
            logger.info(f"开始扫描项目 {project_id} 的风险")
            
            alerts = []
            
            # 1. 扫描进度延期风险
            schedule_alerts = self._scan_schedule_risks(project_id)
            alerts.extend(schedule_alerts)
            
            # 2. 扫描资源不足风险
            resource_alerts = self._scan_resource_risks(project_id)
            alerts.extend(resource_alerts)
            
            # 3. 扫描质量问题风险
            quality_alerts = self._scan_quality_risks(project_id)
            alerts.extend(quality_alerts)
            
            # 4. 扫描依赖阻塞风险
            dependency_alerts = self._scan_dependency_risks(project_id)
            alerts.extend(dependency_alerts)
            
            # 5. 扫描范围蔓延风险
            scope_alerts = self._scan_scope_risks(project_id)
            alerts.extend(scope_alerts)
            
            # 6. 扫描技术风险
            technical_alerts = self._scan_technical_risks(project_id)
            alerts.extend(technical_alerts)
            
            logger.info(f"项目 {project_id} 风险扫描完成，发现 {len(alerts)} 个风险预警")
            return alerts
        except Exception as e:
            logger.error(f"扫描项目风险失败: {str(e)}")
            raise
    
    def _scan_schedule_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描进度延期风险"""
        alerts = []
        try:
            # 获取项目任务
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 检查逾期任务
            overdue_tasks = []
            for task in tasks:
                if self._is_task_overdue(task):
                    overdue_tasks.append(task)
            
            # 计算逾期比例
            total_tasks = len(tasks)
            overdue_ratio = len(overdue_tasks) / total_tasks if total_tasks > 0 else 0
            
            if overdue_ratio > self.risk_thresholds['overdue_task_ratio']:
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="项目进度延期风险",
                    risk_level=RiskLevel.HIGH,
                    alert_type="SCHEDULE_DELAY",
                    alert_message=f"项目逾期任务比例过高 ({overdue_ratio:.1%})，需要关注进度控制",
                    alert_time=datetime.now(),
                    mitigation_suggestion="重新评估任务优先级，增加资源投入，优化工作流程",
                    urgency_score=8
                )
                alerts.append(alert)
            
            # 检查关键任务延期
            critical_overdue = [t for t in overdue_tasks if t.get("priority") in ["高", "紧急"]]
            if len(critical_overdue) > 0:
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="关键任务延期风险",
                    risk_level=RiskLevel.CRITICAL,
                    alert_type="CRITICAL_DELAY",
                    alert_message=f"发现 {len(critical_overdue)} 个高优先级任务逾期",
                    alert_time=datetime.now(),
                    mitigation_suggestion="立即处理高优先级逾期任务，重新分配资源",
                    urgency_score=9
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"扫描进度风险失败: {str(e)}")
        
        return alerts
    
    def _scan_resource_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描资源不足风险"""
        alerts = []
        try:
            # 获取项目任务和资源信息
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            resources = self.db.get_by_field("resources", "project_id", project_id)
            
            # 检查工作负载
            workload_analysis = self._analyze_workload(tasks)
            
            if workload_analysis["overloaded_users"]:
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="团队工作负载过高风险",
                    risk_level=RiskLevel.MEDIUM,
                    alert_type="RESOURCE_SHORTAGE",
                    alert_message=f"发现 {len(workload_analysis['overloaded_users'])} 个用户工作负载过高",
                    alert_time=datetime.now(),
                    mitigation_suggestion="重新分配任务，引入临时支援，优化工作流程",
                    urgency_score=6
                )
                alerts.append(alert)
            
            # 检查资源可用性
            low_availability_resources = [r for r in resources if r.get("availability", 1.0) < 0.5]
            if low_availability_resources:
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="资源可用性不足风险",
                    risk_level=RiskLevel.MEDIUM,
                    alert_type="RESOURCE_AVAILABILITY",
                    alert_message=f"发现 {len(low_availability_resources)} 个资源可用性不足",
                    alert_time=datetime.now(),
                    mitigation_suggestion="寻找替代资源，调整项目计划，优化资源分配",
                    urgency_score=5
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"扫描资源风险失败: {str(e)}")
        
        return alerts
    
    def _scan_quality_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描质量问题风险"""
        alerts = []
        try:
            # 获取项目问题
            issues = self.db.get_by_field("issues", "project_id", project_id)
            
            # 检查质量问题数量
            quality_issues = [i for i in issues if i.get("category") == "质量问题"]
            if len(quality_issues) > 5:  # 质量问题阈值
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="质量问题频发风险",
                    risk_level=RiskLevel.HIGH,
                    alert_type="QUALITY_ISSUE",
                    alert_message=f"发现 {len(quality_issues)} 个质量问题，需要关注质量管控",
                    alert_time=datetime.now(),
                    mitigation_suggestion="加强质量检查，完善测试流程，提升开发规范",
                    urgency_score=7
                )
                alerts.append(alert)
            
            # 检查严重问题
            critical_issues = [i for i in issues if i.get("severity") in ["高", "严重"]]
            if len(critical_issues) > 2:
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="严重问题风险",
                    risk_level=RiskLevel.CRITICAL,
                    alert_type="CRITICAL_QUALITY",
                    alert_message=f"发现 {len(critical_issues)} 个严重问题，需要立即处理",
                    alert_time=datetime.now(),
                    mitigation_suggestion="立即处理严重问题，加强质量监控，暂停相关功能发布",
                    urgency_score=9
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"扫描质量风险失败: {str(e)}")
        
        return alerts
    
    def _scan_dependency_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描依赖阻塞风险"""
        alerts = []
        try:
            # 获取项目任务
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 检查阻塞任务
            blocked_tasks = []
            for task in tasks:
                if self._is_task_blocked(task, tasks):
                    blocked_tasks.append(task)
            
            blocked_ratio = len(blocked_tasks) / len(tasks) if tasks else 0
            
            if blocked_ratio > self.risk_thresholds['blocked_task_ratio']:
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="任务依赖阻塞风险",
                    risk_level=RiskLevel.MEDIUM,
                    alert_type="DEPENDENCY_BLOCK",
                    alert_message=f"发现 {len(blocked_tasks)} 个任务被阻塞，阻塞比例 {blocked_ratio:.1%}",
                    alert_time=datetime.now(),
                    mitigation_suggestion="分析依赖关系，优化任务顺序，解决阻塞问题",
                    urgency_score=6
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"扫描依赖风险失败: {str(e)}")
        
        return alerts
    
    def _scan_scope_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描范围蔓延风险"""
        alerts = []
        try:
            # 获取变更请求
            change_requests = self.db.get_by_field("change_requests", "project_id", project_id)
            
            # 检查范围变更数量
            scope_changes = [cr for cr in change_requests if cr.get("change_type") == "范围变更"]
            if len(scope_changes) > 3:  # 范围变更阈值
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="项目范围蔓延风险",
                    risk_level=RiskLevel.MEDIUM,
                    alert_type="SCOPE_CREEP",
                    alert_message=f"发现 {len(scope_changes)} 个范围变更请求，需要控制范围蔓延",
                    alert_time=datetime.now(),
                    mitigation_suggestion="严格控制范围变更，评估变更影响，更新项目计划",
                    urgency_score=5
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"扫描范围风险失败: {str(e)}")
        
        return alerts
    
    def _scan_technical_risks(self, project_id: str) -> List[RiskAlert]:
        """扫描技术风险"""
        alerts = []
        try:
            # 获取技术问题
            issues = self.db.get_by_field("issues", "project_id", project_id)
            technical_issues = [i for i in issues if i.get("category") == "技术问题"]
            
            if len(technical_issues) > 3:  # 技术问题阈值
                alert = RiskAlert(
                    risk_id=f"RISK-{generate_id()[:8].upper()}",
                    project_id=project_id,
                    risk_title="技术实现风险",
                    risk_level=RiskLevel.HIGH,
                    alert_type="TECHNICAL_RISK",
                    alert_message=f"发现 {len(technical_issues)} 个技术问题，可能存在技术实现风险",
                    alert_time=datetime.now(),
                    mitigation_suggestion="加强技术评审，寻求技术专家支持，考虑技术方案调整",
                    urgency_score=7
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"扫描技术风险失败: {str(e)}")
        
        return alerts
    
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
    
    def _is_task_blocked(self, task: Dict[str, Any], all_tasks: List[Dict[str, Any]]) -> bool:
        """判断任务是否被阻塞"""
        dependencies = task.get("dependencies", [])
        if not dependencies:
            return False
        
        # 检查依赖任务是否完成
        for dep_id in dependencies:
            dep_task = next((t for t in all_tasks if t.get("task_id") == dep_id), None)
            if not dep_task or dep_task.get("status") != "已完成":
                return True
        
        return False
    
    def _analyze_workload(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析工作负载"""
        user_tasks = {}
        for task in tasks:
            assigned_to = task.get("assigned_to")
            if assigned_to:
                if assigned_to not in user_tasks:
                    user_tasks[assigned_to] = []
                user_tasks[assigned_to].append(task)
        
        overloaded_users = []
        for user, user_task_list in user_tasks.items():
            # 简化负载计算：任务数量超过5个认为过载
            if len(user_task_list) > 5:
                overloaded_users.append(user)
        
        return {
            "user_tasks": user_tasks,
            "overloaded_users": overloaded_users
        }
    
    def analyze_project_risks(self, project_id: str) -> RiskAnalysis:
        """分析项目风险"""
        try:
            logger.info(f"分析项目 {project_id} 的风险")
            
            # 获取项目风险
            risks = self.db.get_by_field("risks", "project_id", project_id)
            
            # 统计风险等级
            total_risks = len(risks)
            high_risks = len([r for r in risks if r.get("risk_level") in ["高", "严重"]])
            medium_risks = len([r for r in risks if r.get("risk_level") == "中"])
            low_risks = len([r for r in risks if r.get("risk_level") == "低"])
            
            # 分析风险趋势（简化版）
            risk_trend = "稳定"  # 实际应该基于历史数据计算
            
            # 统计风险类别
            category_count = {}
            for risk in risks:
                category = risk.get("category", "其他")
                category_count[category] = category_count.get(category, 0) + 1
            
            top_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # 影响评估
            impact_assessment = {
                "schedule_impact": "中等",
                "cost_impact": "低",
                "quality_impact": "中等",
                "resource_impact": "低"
            }
            
            # 缓解建议
            mitigation_recommendations = [
                "建立定期风险评审机制",
                "加强项目监控和预警",
                "完善风险应对计划",
                "提升团队风险意识"
            ]
            
            analysis = RiskAnalysis(
                project_id=project_id,
                total_risks=total_risks,
                high_risks=high_risks,
                medium_risks=medium_risks,
                low_risks=low_risks,
                risk_trend=risk_trend,
                top_risk_categories=top_categories,
                risk_impact_assessment=impact_assessment,
                mitigation_recommendations=mitigation_recommendations
            )
            
            logger.info(f"项目 {project_id} 风险分析完成")
            return analysis
        except Exception as e:
            logger.error(f"分析项目风险失败: {str(e)}")
            raise
    
    def generate_risk_report(self, project_id: str) -> Dict[str, Any]:
        """生成风险报告"""
        try:
            logger.info(f"生成项目 {project_id} 的风险报告")
            
            # 扫描风险
            alerts = self.scan_project_risks(project_id)
            
            # 分析风险
            analysis = self.analyze_project_risks(project_id)
            
            # 获取项目信息
            project = self.db.read("projects", project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")
            
            # 生成报告
            report = {
                "project_info": {
                    "project_id": project_id,
                    "project_name": project["project_name"],
                    "report_date": datetime.now().isoformat()
                },
                "risk_summary": {
                    "total_alerts": len(alerts),
                    "critical_alerts": len([a for a in alerts if a.risk_level == RiskLevel.CRITICAL]),
                    "high_alerts": len([a for a in alerts if a.risk_level == RiskLevel.HIGH]),
                    "medium_alerts": len([a for a in alerts if a.risk_level == RiskLevel.MEDIUM]),
                    "low_alerts": len([a for a in alerts if a.risk_level == RiskLevel.LOW])
                },
                "risk_analysis": {
                    "total_risks": analysis.total_risks,
                    "high_risks": analysis.high_risks,
                    "medium_risks": analysis.medium_risks,
                    "low_risks": analysis.low_risks,
                    "risk_trend": analysis.risk_trend,
                    "top_categories": analysis.top_risk_categories
                },
                "alerts": [
                    {
                        "risk_id": alert.risk_id,
                        "risk_title": alert.risk_title,
                        "risk_level": alert.risk_level.value,
                        "alert_type": alert.alert_type,
                        "alert_message": alert.alert_message,
                        "alert_time": alert.alert_time.isoformat(),
                        "mitigation_suggestion": alert.mitigation_suggestion,
                        "urgency_score": alert.urgency_score
                    }
                    for alert in alerts
                ],
                "recommendations": analysis.mitigation_recommendations,
                "impact_assessment": analysis.risk_impact_assessment
            }
            
            logger.info(f"项目 {project_id} 风险报告生成完成")
            return report
        except Exception as e:
            logger.error(f"生成风险报告失败: {str(e)}")
            raise


# 创建全局服务实例
risk_monitoring_service = RiskMonitoringService()

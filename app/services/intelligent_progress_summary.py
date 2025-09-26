"""
智能进度汇总服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.models.base import BaseModel
from app.models.enums import TaskStatus, RiskLevel, IssueCategory
from app.utils.logger import get_logger
from app.services.database_service import database_service

logger = get_logger(__name__)


@dataclass
class ProgressSummary:
    """进度汇总数据"""
    project_id: str
    project_name: str
    period: str  # daily, weekly, monthly
    start_date: datetime
    end_date: datetime
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    overdue_tasks: int
    completion_rate: float
    progress_percentage: float
    achievements: List[str]
    challenges: List[str]
    next_week_plan: List[str]
    risks: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    team_performance: Dict[str, Any]


@dataclass
class DailySummary(ProgressSummary):
    """日报汇总"""
    today_tasks: List[Dict[str, Any]]
    tomorrow_plan: List[str]


@dataclass
class WeeklySummary(ProgressSummary):
    """周报汇总"""
    week_highlights: List[str]
    week_challenges: List[str]
    next_week_focus: List[str]


@dataclass
class MonthlySummary(ProgressSummary):
    """月报汇总"""
    month_achievements: List[str]
    month_lessons: List[str]
    next_month_goals: List[str]


class IntelligentProgressSummaryService:
    """智能进度汇总服务"""
    
    def __init__(self):
        """初始化服务"""
        self.db = database_service.get_database()
        logger.info("智能进度汇总服务初始化完成")
    
    def generate_daily_summary(self, project_id: str, date: Optional[datetime] = None) -> DailySummary:
        """生成日报"""
        try:
            if date is None:
                date = datetime.now()
            
            # 获取项目信息
            project = self.db.read("projects", project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")
            
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 计算任务统计
            task_stats = self._calculate_task_statistics(tasks, date)
            
            # 获取今日任务
            today_tasks = self._get_today_tasks(tasks, date)
            
            # 获取明日计划
            tomorrow_plan = self._get_tomorrow_plan(tasks, date)
            
            # 获取成就和挑战
            achievements = self._get_daily_achievements(tasks, date)
            challenges = self._get_daily_challenges(tasks, date)
            
            # 获取风险和问题
            risks = self._get_project_risks(project_id)
            issues = self._get_project_issues(project_id)
            
            # 计算团队绩效
            team_performance = self._calculate_team_performance(tasks, date)
            
            summary = DailySummary(
                project_id=project_id,
                project_name=project["project_name"],
                period="daily",
                start_date=date,
                end_date=date,
                total_tasks=task_stats["total"],
                completed_tasks=task_stats["completed"],
                in_progress_tasks=task_stats["in_progress"],
                pending_tasks=task_stats["pending"],
                overdue_tasks=task_stats["overdue"],
                completion_rate=task_stats["completion_rate"],
                progress_percentage=task_stats["progress_percentage"],
                achievements=achievements,
                challenges=challenges,
                next_week_plan=tomorrow_plan,
                risks=risks,
                issues=issues,
                team_performance=team_performance,
                today_tasks=today_tasks,
                tomorrow_plan=tomorrow_plan
            )
            
            logger.info(f"生成项目 {project_id} 的日报成功")
            return summary
        except Exception as e:
            logger.error(f"生成日报失败: {str(e)}")
            raise
    
    def generate_weekly_summary(self, project_id: str, week_start: Optional[datetime] = None) -> WeeklySummary:
        """生成周报"""
        try:
            if week_start is None:
                # 获取本周一
                today = datetime.now()
                week_start = today - timedelta(days=today.weekday())
            
            week_end = week_start + timedelta(days=6)
            
            # 获取项目信息
            project = self.db.read("projects", project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")
            
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 计算任务统计
            task_stats = self._calculate_task_statistics(tasks, week_end)
            
            # 获取周亮点和挑战
            week_highlights = self._get_weekly_highlights(tasks, week_start, week_end)
            week_challenges = self._get_weekly_challenges(tasks, week_start, week_end)
            
            # 获取下周重点
            next_week_focus = self._get_next_week_focus(tasks, week_end)
            
            # 获取风险和问题
            risks = self._get_project_risks(project_id)
            issues = self._get_project_issues(project_id)
            
            # 计算团队绩效
            team_performance = self._calculate_team_performance(tasks, week_end)
            
            summary = WeeklySummary(
                project_id=project_id,
                project_name=project["project_name"],
                period="weekly",
                start_date=week_start,
                end_date=week_end,
                total_tasks=task_stats["total"],
                completed_tasks=task_stats["completed"],
                in_progress_tasks=task_stats["in_progress"],
                pending_tasks=task_stats["pending"],
                overdue_tasks=task_stats["overdue"],
                completion_rate=task_stats["completion_rate"],
                progress_percentage=task_stats["progress_percentage"],
                achievements=week_highlights,
                challenges=week_challenges,
                next_week_plan=next_week_focus,
                risks=risks,
                issues=issues,
                team_performance=team_performance,
                week_highlights=week_highlights,
                week_challenges=week_challenges,
                next_week_focus=next_week_focus
            )
            
            logger.info(f"生成项目 {project_id} 的周报成功")
            return summary
        except Exception as e:
            logger.error(f"生成周报失败: {str(e)}")
            raise
    
    def generate_monthly_summary(self, project_id: str, month_start: Optional[datetime] = None) -> MonthlySummary:
        """生成月报"""
        try:
            if month_start is None:
                # 获取本月第一天
                today = datetime.now()
                month_start = today.replace(day=1)
            
            # 计算月末
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            # 获取项目信息
            project = self.db.read("projects", project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")
            
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 计算任务统计
            task_stats = self._calculate_task_statistics(tasks, month_end)
            
            # 获取月成就和经验教训
            month_achievements = self._get_monthly_achievements(tasks, month_start, month_end)
            month_lessons = self._get_monthly_lessons(tasks, month_start, month_end)
            
            # 获取下月目标
            next_month_goals = self._get_next_month_goals(tasks, month_end)
            
            # 获取风险和问题
            risks = self._get_project_risks(project_id)
            issues = self._get_project_issues(project_id)
            
            # 计算团队绩效
            team_performance = self._calculate_team_performance(tasks, month_end)
            
            summary = MonthlySummary(
                project_id=project_id,
                project_name=project["project_name"],
                period="monthly",
                start_date=month_start,
                end_date=month_end,
                total_tasks=task_stats["total"],
                completed_tasks=task_stats["completed"],
                in_progress_tasks=task_stats["in_progress"],
                pending_tasks=task_stats["pending"],
                overdue_tasks=task_stats["overdue"],
                completion_rate=task_stats["completion_rate"],
                progress_percentage=task_stats["progress_percentage"],
                achievements=month_achievements,
                challenges=month_lessons,
                next_week_plan=next_month_goals,
                risks=risks,
                issues=issues,
                team_performance=team_performance,
                month_achievements=month_achievements,
                month_lessons=month_lessons,
                next_month_goals=next_month_goals
            )
            
            logger.info(f"生成项目 {project_id} 的月报成功")
            return summary
        except Exception as e:
            logger.error(f"生成月报失败: {str(e)}")
            raise
    
    def _calculate_task_statistics(self, tasks: List[Dict[str, Any]], end_date: datetime) -> Dict[str, Any]:
        """计算任务统计信息"""
        total = len(tasks)
        completed = len([t for t in tasks if t.get("status") == "已完成"])
        in_progress = len([t for t in tasks if t.get("status") == "进行中"])
        pending = len([t for t in tasks if t.get("status") == "待开始"])
        overdue = len([t for t in tasks if self._is_task_overdue(t, end_date)])
        
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        # 计算平均进度
        total_progress = sum(t.get("progress_percentage", 0) for t in tasks)
        progress_percentage = (total_progress / total) if total > 0 else 0.0
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": completion_rate,
            "progress_percentage": progress_percentage
        }
    
    def _is_task_overdue(self, task: Dict[str, Any], end_date: datetime) -> bool:
        """判断任务是否逾期"""
        due_date = task.get("due_date")
        if not due_date:
            return False
        
        # 简化日期比较，实际应该解析日期字符串
        status = task.get("status", "")
        return status not in ["已完成", "已取消"] and due_date < end_date.isoformat()
    
    def _get_today_tasks(self, tasks: List[Dict[str, Any]], date: datetime) -> List[Dict[str, Any]]:
        """获取今日任务"""
        # 简化实现，返回进行中的任务
        return [t for t in tasks if t.get("status") == "进行中"][:5]
    
    def _get_tomorrow_plan(self, tasks: List[Dict[str, Any]], date: datetime) -> List[str]:
        """获取明日计划"""
        # 简化实现，返回待开始的任务
        pending_tasks = [t for t in tasks if t.get("status") == "待开始"][:3]
        return [f"完成 {t.get('task_name', '')}" for t in pending_tasks]
    
    def _get_daily_achievements(self, tasks: List[Dict[str, Any]], date: datetime) -> List[str]:
        """获取今日成就"""
        # 简化实现
        completed_today = [t for t in tasks if t.get("status") == "已完成"]
        return [f"完成 {t.get('task_name', '')}" for t in completed_today[:3]]
    
    def _get_daily_challenges(self, tasks: List[Dict[str, Any]], date: datetime) -> List[str]:
        """获取今日挑战"""
        # 简化实现
        overdue_tasks = [t for t in tasks if self._is_task_overdue(t, date)]
        return [f"{t.get('task_name', '')} 逾期" for t in overdue_tasks[:3]]
    
    def _get_weekly_highlights(self, tasks: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> List[str]:
        """获取周亮点"""
        # 简化实现
        completed_this_week = [t for t in tasks if t.get("status") == "已完成"]
        return [f"本周完成 {t.get('task_name', '')}" for t in completed_this_week[:5]]
    
    def _get_weekly_challenges(self, tasks: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> List[str]:
        """获取周挑战"""
        # 简化实现
        overdue_tasks = [t for t in tasks if self._is_task_overdue(t, end_date)]
        return [f"{t.get('task_name', '')} 需要关注" for t in overdue_tasks[:3]]
    
    def _get_next_week_focus(self, tasks: List[Dict[str, Any]], end_date: datetime) -> List[str]:
        """获取下周重点"""
        # 简化实现
        high_priority_tasks = [t for t in tasks if t.get("priority") == "高" and t.get("status") != "已完成"]
        return [f"重点推进 {t.get('task_name', '')}" for t in high_priority_tasks[:3]]
    
    def _get_monthly_achievements(self, tasks: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> List[str]:
        """获取月成就"""
        # 简化实现
        completed_this_month = [t for t in tasks if t.get("status") == "已完成"]
        return [f"本月完成 {t.get('task_name', '')}" for t in completed_this_month[:10]]
    
    def _get_monthly_lessons(self, tasks: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> List[str]:
        """获取月经验教训"""
        # 简化实现
        return [
            "任务估算需要更准确",
            "需要加强团队沟通",
            "风险识别需要提前"
        ]
    
    def _get_next_month_goals(self, tasks: List[Dict[str, Any]], end_date: datetime) -> List[str]:
        """获取下月目标"""
        # 简化实现
        pending_tasks = [t for t in tasks if t.get("status") == "待开始"]
        return [f"完成 {t.get('task_name', '')}" for t in pending_tasks[:5]]
    
    def _get_project_risks(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目风险"""
        try:
            risks = self.db.get_by_field("risks", "project_id", project_id)
            # 只返回高风险
            high_risks = [r for r in risks if r.get("risk_level") in ["高", "严重"]]
            return high_risks[:5]
        except Exception as e:
            logger.error(f"获取项目风险失败: {str(e)}")
            return []
    
    def _get_project_issues(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目问题"""
        try:
            issues = self.db.get_by_field("issues", "project_id", project_id)
            # 只返回未解决的问题
            open_issues = [i for i in issues if i.get("status") not in ["已解决", "已关闭"]]
            return open_issues[:5]
        except Exception as e:
            logger.error(f"获取项目问题失败: {str(e)}")
            return []
    
    def _calculate_team_performance(self, tasks: List[Dict[str, Any]], end_date: datetime) -> Dict[str, Any]:
        """计算团队绩效"""
        # 简化实现
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0,
            "team_efficiency": "良好",
            "workload_distribution": "均衡"
        }
    
    def get_summary_statistics(self, project_id: str) -> Dict[str, Any]:
        """获取汇总统计信息"""
        try:
            # 获取项目信息
            project = self.db.read("projects", project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")
            
            # 获取任务数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 计算各种统计
            task_stats = self._calculate_task_statistics(tasks, datetime.now())
            
            # 获取风险和问题统计
            risks = self.db.get_by_field("risks", "project_id", project_id)
            issues = self.db.get_by_field("issues", "project_id", project_id)
            
            risk_stats = {
                "total": len(risks),
                "high": len([r for r in risks if r.get("risk_level") in ["高", "严重"]]),
                "medium": len([r for r in risks if r.get("risk_level") == "中"]),
                "low": len([r for r in risks if r.get("risk_level") == "低"])
            }
            
            issue_stats = {
                "total": len(issues),
                "open": len([i for i in issues if i.get("status") not in ["已解决", "已关闭"]]),
                "resolved": len([i for i in issues if i.get("status") in ["已解决", "已关闭"]])
            }
            
            return {
                "project_info": {
                    "project_id": project_id,
                    "project_name": project["project_name"],
                    "status": project["status"],
                    "progress_percentage": project.get("progress_percentage", 0)
                },
                "task_statistics": task_stats,
                "risk_statistics": risk_stats,
                "issue_statistics": issue_stats,
                "summary_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取汇总统计信息失败: {str(e)}")
            raise


# 创建全局服务实例
intelligent_progress_summary_service = IntelligentProgressSummaryService()

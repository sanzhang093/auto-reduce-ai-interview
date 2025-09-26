"""
报表生成服务
"""
import json
import csv
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from app.models.enums import ReportType, ReportFormat
from app.utils.logger import get_logger
from app.services.database_service import database_service
from app.services.project_service import project_service
from app.services.task_service import task_service
from app.services.risk_service import risk_service
from app.services.issue_service import issue_service

logger = get_logger(__name__)


@dataclass
class ReportData:
    """报表数据"""
    report_type: ReportType
    report_format: ReportFormat
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    generated_at: datetime


class ReportGeneratorService:
    """报表生成服务"""
    
    def __init__(self):
        """初始化服务"""
        self.db = database_service.get_database()
        self.output_dir = Path("./reports")
        self.output_dir.mkdir(exist_ok=True)
        logger.info("报表生成服务初始化完成")
    
    def generate_report(self, report_type: ReportType, report_format: ReportFormat, 
                       project_ids: List[str], **kwargs) -> ReportData:
        """生成报表"""
        try:
            logger.info(f"生成报表: {report_type.value} - {report_format.value}")
            
            # 根据报表类型生成数据
            if report_type == ReportType.PROJECT_SUMMARY:
                data = self._generate_project_summary_data(project_ids)
            elif report_type == ReportType.TASK_PROGRESS:
                data = self._generate_task_progress_data(project_ids)
            elif report_type == ReportType.RISK_ANALYSIS:
                data = self._generate_risk_analysis_data(project_ids)
            elif report_type == ReportType.TEAM_PERFORMANCE:
                data = self._generate_team_performance_data(project_ids)
            elif report_type == ReportType.EXECUTIVE_DASHBOARD:
                data = self._generate_executive_dashboard_data(project_ids)
            else:
                raise ValueError(f"不支持的报表类型: {report_type}")
            
            # 生成元数据
            metadata = {
                "report_type": report_type.value,
                "report_format": report_format.value,
                "project_ids": project_ids,
                "generated_by": "系统自动生成",
                "generation_time": datetime.now().isoformat(),
                "data_count": len(data.get("items", []))
            }
            
            # 根据格式生成报表
            if report_format == ReportFormat.JSON:
                output_data = self._generate_json_report(data, metadata)
            elif report_format == ReportFormat.CSV:
                output_data = self._generate_csv_report(data, metadata)
            elif report_format == ReportFormat.HTML:
                output_data = self._generate_html_report(data, metadata)
            else:
                raise ValueError(f"不支持的报表格式: {report_format}")
            
            report_data = ReportData(
                report_type=report_type,
                report_format=report_format,
                data=output_data,
                metadata=metadata,
                generated_at=datetime.now()
            )
            
            logger.info(f"报表生成完成: {report_type.value}")
            return report_data
        except Exception as e:
            logger.error(f"生成报表失败: {str(e)}")
            raise
    
    def _generate_project_summary_data(self, project_ids: List[str]) -> Dict[str, Any]:
        """生成项目汇总数据"""
        projects_data = []
        
        for project_id in project_ids:
            try:
                # 获取项目信息
                project = project_service.get_project(project_id)
                if not project:
                    continue
                
                # 获取项目统计
                summary = project_service.get_project_summary(project_id)
                
                project_info = {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "project_code": project.project_code,
                    "status": project.status,
                    "priority": project.priority,
                    "project_manager": project.project_manager,
                    "start_date": project.start_date.isoformat() if project.start_date else None,
                    "planned_end_date": project.planned_end_date.isoformat() if project.planned_end_date else None,
                    "budget": float(project.budget) if project.budget else None,
                    "actual_cost": float(project.actual_cost) if project.actual_cost else None,
                    "progress_percentage": project.progress_percentage,
                    "budget_utilization": project.budget_utilization,
                    "total_tasks": summary.total_tasks if summary else 0,
                    "completed_tasks": summary.completed_tasks if summary else 0,
                    "total_risks": summary.total_risks if summary else 0,
                    "high_risks": summary.high_risks if summary else 0,
                    "completion_rate": (summary.completed_tasks / summary.total_tasks * 100) if summary and summary.total_tasks > 0 else 0
                }
                
                projects_data.append(project_info)
            except Exception as e:
                logger.error(f"获取项目 {project_id} 数据失败: {str(e)}")
                continue
        
        return {
            "report_title": "项目汇总报表",
            "generated_at": datetime.now().isoformat(),
            "total_projects": len(projects_data),
            "items": projects_data
        }
    
    def _generate_task_progress_data(self, project_ids: List[str]) -> Dict[str, Any]:
        """生成任务进度数据"""
        tasks_data = []
        
        for project_id in project_ids:
            try:
                # 获取项目任务
                tasks = task_service.get_project_tasks(project_id)
                
                for task in tasks:
                    task_info = {
                        "project_id": project_id,
                        "task_id": task.task_id,
                        "task_name": task.task_name,
                        "status": task.status,
                        "priority": task.priority,
                        "assigned_to": task.assigned_to,
                        "progress_percentage": task.progress_percentage,
                        "start_date": task.start_date.isoformat() if task.start_date else None,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
                        "actual_hours": float(task.actual_hours) if task.actual_hours else None,
                        "is_overdue": task.is_overdue,
                        "completion_rate": task.completion_rate
                    }
                    tasks_data.append(task_info)
            except Exception as e:
                logger.error(f"获取项目 {project_id} 任务数据失败: {str(e)}")
                continue
        
        # 统计信息
        total_tasks = len(tasks_data)
        completed_tasks = len([t for t in tasks_data if t["status"] == "已完成"])
        overdue_tasks = len([t for t in tasks_data if t["is_overdue"]])
        
        return {
            "report_title": "任务进度报表",
            "generated_at": datetime.now().isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "items": tasks_data
        }
    
    def _generate_risk_analysis_data(self, project_ids: List[str]) -> Dict[str, Any]:
        """生成风险分析数据"""
        risks_data = []
        
        for project_id in project_ids:
            try:
                # 获取项目风险
                risks = risk_service.get_project_risks(project_id)
                
                for risk in risks:
                    risk_info = {
                        "project_id": project_id,
                        "risk_id": risk.risk_id,
                        "risk_title": risk.risk_title,
                        "category": risk.category,
                        "probability": risk.probability,
                        "impact": risk.impact,
                        "risk_level": risk.risk_level,
                        "status": risk.status,
                        "owner": risk.owner,
                        "identified_date": risk.identified_date.isoformat() if risk.identified_date else None,
                        "risk_score": risk.risk_score,
                        "mitigation_progress": risk.mitigation_progress
                    }
                    risks_data.append(risk_info)
            except Exception as e:
                logger.error(f"获取项目 {project_id} 风险数据失败: {str(e)}")
                continue
        
        # 统计信息
        total_risks = len(risks_data)
        high_risks = len([r for r in risks_data if r["risk_level"] in ["高", "严重"]])
        medium_risks = len([r for r in risks_data if r["risk_level"] == "中"])
        low_risks = len([r for r in risks_data if r["risk_level"] == "低"])
        
        return {
            "report_title": "风险分析报表",
            "generated_at": datetime.now().isoformat(),
            "total_risks": total_risks,
            "high_risks": high_risks,
            "medium_risks": medium_risks,
            "low_risks": low_risks,
            "high_risk_ratio": (high_risks / total_risks * 100) if total_risks > 0 else 0,
            "items": risks_data
        }
    
    def _generate_team_performance_data(self, project_ids: List[str]) -> Dict[str, Any]:
        """生成团队绩效数据"""
        performance_data = []
        
        for project_id in project_ids:
            try:
                # 获取项目任务
                tasks = task_service.get_project_tasks(project_id)
                
                # 按用户统计
                user_stats = {}
                for task in tasks:
                    assigned_to = task.assigned_to
                    if assigned_to not in user_stats:
                        user_stats[assigned_to] = {
                            "total_tasks": 0,
                            "completed_tasks": 0,
                            "in_progress_tasks": 0,
                            "overdue_tasks": 0,
                            "total_hours": 0,
                            "actual_hours": 0
                        }
                    
                    user_stats[assigned_to]["total_tasks"] += 1
                    if task.status == "已完成":
                        user_stats[assigned_to]["completed_tasks"] += 1
                    elif task.status == "进行中":
                        user_stats[assigned_to]["in_progress_tasks"] += 1
                    
                    if task.is_overdue:
                        user_stats[assigned_to]["overdue_tasks"] += 1
                    
                    if task.estimated_hours:
                        user_stats[assigned_to]["total_hours"] += float(task.estimated_hours)
                    if task.actual_hours:
                        user_stats[assigned_to]["actual_hours"] += float(task.actual_hours)
                
                # 计算绩效指标
                for user, stats in user_stats.items():
                    completion_rate = (stats["completed_tasks"] / stats["total_tasks"] * 100) if stats["total_tasks"] > 0 else 0
                    efficiency = (stats["actual_hours"] / stats["total_hours"] * 100) if stats["total_hours"] > 0 else 0
                    
                    user_performance = {
                        "project_id": project_id,
                        "user": user,
                        "total_tasks": stats["total_tasks"],
                        "completed_tasks": stats["completed_tasks"],
                        "in_progress_tasks": stats["in_progress_tasks"],
                        "overdue_tasks": stats["overdue_tasks"],
                        "completion_rate": completion_rate,
                        "total_hours": stats["total_hours"],
                        "actual_hours": stats["actual_hours"],
                        "efficiency": efficiency,
                        "performance_level": self._get_performance_level(completion_rate, efficiency)
                    }
                    performance_data.append(user_performance)
            except Exception as e:
                logger.error(f"获取项目 {project_id} 团队绩效数据失败: {str(e)}")
                continue
        
        return {
            "report_title": "团队绩效报表",
            "generated_at": datetime.now().isoformat(),
            "total_users": len(set(item["user"] for item in performance_data)),
            "items": performance_data
        }
    
    def _generate_executive_dashboard_data(self, project_ids: List[str]) -> Dict[str, Any]:
        """生成高管仪表板数据"""
        dashboard_data = {
            "report_title": "高管仪表板",
            "generated_at": datetime.now().isoformat(),
            "overview": {},
            "projects": [],
            "risks": [],
            "issues": [],
            "team_performance": {}
        }
        
        # 总体概览
        total_projects = len(project_ids)
        active_projects = 0
        total_tasks = 0
        completed_tasks = 0
        total_risks = 0
        high_risks = 0
        total_issues = 0
        open_issues = 0
        
        for project_id in project_ids:
            try:
                # 项目信息
                project = project_service.get_project(project_id)
                if project and project.status == "进行中":
                    active_projects += 1
                
                # 任务统计
                tasks = task_service.get_project_tasks(project_id)
                total_tasks += len(tasks)
                completed_tasks += len([t for t in tasks if t.status == "已完成"])
                
                # 风险统计
                risks = risk_service.get_project_risks(project_id)
                total_risks += len(risks)
                high_risks += len([r for r in risks if r.risk_level in ["高", "严重"]])
                
                # 问题统计
                issues = issue_service.get_project_issues(project_id)
                total_issues += len(issues)
                open_issues += len([i for i in issues if i.status not in ["已解决", "已关闭"]])
                
            except Exception as e:
                logger.error(f"获取项目 {project_id} 仪表板数据失败: {str(e)}")
                continue
        
        dashboard_data["overview"] = {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_risks": total_risks,
            "high_risks": high_risks,
            "total_issues": total_issues,
            "open_issues": open_issues
        }
        
        return dashboard_data
    
    def _get_performance_level(self, completion_rate: float, efficiency: float) -> str:
        """获取绩效等级"""
        if completion_rate >= 90 and efficiency >= 90:
            return "优秀"
        elif completion_rate >= 80 and efficiency >= 80:
            return "良好"
        elif completion_rate >= 70 and efficiency >= 70:
            return "一般"
        else:
            return "需改进"
    
    def _generate_json_report(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """生成JSON格式报表"""
        return {
            "metadata": metadata,
            "data": data
        }
    
    def _generate_csv_report(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """生成CSV格式报表"""
        items = data.get("items", [])
        if not items:
            return ""
        
        # 获取所有字段
        fieldnames = set()
        for item in items:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        # 生成CSV内容
        output = []
        output.append(",".join(fieldnames))
        
        for item in items:
            row = []
            for field in fieldnames:
                value = item.get(field, "")
                # 处理特殊字符
                if isinstance(value, str) and ("," in value or '"' in value or "\n" in value):
                    value = f'"{value.replace('"', '""')}"'
                row.append(str(value))
            output.append(",".join(row))
        
        return "\n".join(output)
    
    def _generate_html_report(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """生成HTML格式报表"""
        items = data.get("items", [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{data.get('report_title', '报表')}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{data.get('report_title', '报表')}</h1>
                <p>生成时间: {metadata.get('generation_time', '')}</p>
                <p>报表类型: {metadata.get('report_type', '')}</p>
            </div>
        """
        
        # 添加汇总信息
        if "total_projects" in data:
            html += f"""
            <div class="summary">
                <h2>汇总信息</h2>
                <p>总项目数: {data.get('total_projects', 0)}</p>
            </div>
            """
        elif "total_tasks" in data:
            html += f"""
            <div class="summary">
                <h2>汇总信息</h2>
                <p>总任务数: {data.get('total_tasks', 0)}</p>
                <p>已完成任务: {data.get('completed_tasks', 0)}</p>
                <p>完成率: {data.get('completion_rate', 0):.1f}%</p>
            </div>
            """
        elif "total_risks" in data:
            html += f"""
            <div class="summary">
                <h2>汇总信息</h2>
                <p>总风险数: {data.get('total_risks', 0)}</p>
                <p>高风险数: {data.get('high_risks', 0)}</p>
                <p>高风险比例: {data.get('high_risk_ratio', 0):.1f}%</p>
            </div>
            """
        
        # 添加数据表格
        if items:
            html += "<h2>详细数据</h2><table>"
            
            # 表头
            fieldnames = list(items[0].keys())
            html += "<tr>"
            for field in fieldnames:
                html += f"<th>{field}</th>"
            html += "</tr>"
            
            # 数据行
            for item in items:
                html += "<tr>"
                for field in fieldnames:
                    value = item.get(field, "")
                    html += f"<td>{value}</td>"
                html += "</tr>"
            
            html += "</table>"
        
        html += f"""
            <div class="footer">
                <p>报表由系统自动生成</p>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def export_report(self, report_data: ReportData, filename: Optional[str] = None) -> str:
        """导出报表到文件"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{report_data.report_type.value}_{timestamp}.{report_data.report_format.value}"
            
            file_path = self.output_dir / filename
            
            if report_data.report_format == ReportFormat.JSON:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data.data, f, ensure_ascii=False, indent=2)
            elif report_data.report_format == ReportFormat.CSV:
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    f.write(report_data.data)
            elif report_data.report_format == ReportFormat.HTML:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_data.data)
            
            logger.info(f"报表导出成功: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"导出报表失败: {str(e)}")
            raise
    
    def get_report_templates(self) -> Dict[str, Any]:
        """获取报表模板"""
        templates = {
            "project_summary": {
                "name": "项目汇总报表",
                "description": "展示项目基本信息和关键指标",
                "fields": ["project_id", "project_name", "status", "progress_percentage", "completion_rate"]
            },
            "task_progress": {
                "name": "任务进度报表",
                "description": "展示任务执行情况和进度",
                "fields": ["task_id", "task_name", "status", "progress_percentage", "assigned_to"]
            },
            "risk_analysis": {
                "name": "风险分析报表",
                "description": "展示项目风险状况和分析",
                "fields": ["risk_id", "risk_title", "risk_level", "category", "owner"]
            },
            "team_performance": {
                "name": "团队绩效报表",
                "description": "展示团队成员绩效表现",
                "fields": ["user", "total_tasks", "completed_tasks", "completion_rate", "performance_level"]
            },
            "executive_dashboard": {
                "name": "高管仪表板",
                "description": "面向高管的项目概览和关键指标",
                "fields": ["overview", "projects", "risks", "issues"]
            }
        }
        
        return templates


# 创建全局服务实例
report_generator_service = ReportGeneratorService()

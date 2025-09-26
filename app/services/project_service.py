"""
项目服务
"""
from typing import List, Optional, Dict, Any
from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectResponse, ProjectSummary, ProjectStatistics
from app.services.database_service import database_service
from app.utils.logger import get_logger
from app.utils.helpers import generate_id

logger = get_logger(__name__)


class ProjectService:
    """项目服务类"""
    
    def __init__(self):
        """初始化项目服务"""
        self.db = database_service.get_database()
        logger.info("项目服务初始化完成")
    
    def get_projects(self, filters: Optional[Dict[str, Any]] = None, search: Optional[str] = None) -> List[ProjectResponse]:
        """获取项目列表"""
        try:
            projects_data = self.db.read("projects", filters=filters)
            
            if search:
                projects_data = self.db.search("projects", search, ["project_name", "description", "project_code"])
            
            projects = []
            for project_data in projects_data:
                # 计算项目指标
                project_response = self._calculate_project_metrics(project_data)
                projects.append(project_response)
            
            logger.info(f"获取到 {len(projects)} 个项目")
            return projects
        except Exception as e:
            logger.error(f"获取项目列表失败: {str(e)}")
            raise
    
    def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        """获取单个项目"""
        try:
            project_data = self.db.read("projects", project_id)
            if not project_data:
                return None
            
            # 计算项目指标
            project_response = self._calculate_project_metrics(project_data)
            logger.info(f"获取项目 {project_id} 成功")
            return project_response
        except Exception as e:
            logger.error(f"获取项目 {project_id} 失败: {str(e)}")
            raise
    
    def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        """创建项目"""
        try:
            # 生成项目ID
            project_id = f"PRJ-{generate_id()[:8].upper()}"
            
            # 创建项目数据
            project_dict = project_data.dict()
            project_dict["project_id"] = project_id
            project_dict["status"] = "规划中"
            
            # 保存到数据库
            created_project = self.db.create("projects", project_dict)
            
            # 计算项目指标
            project_response = self._calculate_project_metrics(created_project)
            
            logger.info(f"创建项目 {project_id} 成功")
            return project_response
        except Exception as e:
            logger.error(f"创建项目失败: {str(e)}")
            raise
    
    def update_project(self, project_id: str, project_data: ProjectUpdate) -> Optional[ProjectResponse]:
        """更新项目"""
        try:
            # 获取现有项目
            existing_project = self.db.read("projects", project_id)
            if not existing_project:
                return None
            
            # 更新项目数据
            updates = {k: v for k, v in project_data.dict().items() if v is not None}
            updated_project = self.db.update("projects", project_id, updates)
            
            if not updated_project:
                return None
            
            # 计算项目指标
            project_response = self._calculate_project_metrics(updated_project)
            
            logger.info(f"更新项目 {project_id} 成功")
            return project_response
        except Exception as e:
            logger.error(f"更新项目 {project_id} 失败: {str(e)}")
            raise
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        try:
            success = self.db.delete("projects", project_id)
            if success:
                logger.info(f"删除项目 {project_id} 成功")
            else:
                logger.warning(f"项目 {project_id} 不存在")
            return success
        except Exception as e:
            logger.error(f"删除项目 {project_id} 失败: {str(e)}")
            raise
    
    def get_project_summary(self, project_id: str) -> Optional[ProjectSummary]:
        """获取项目摘要"""
        try:
            project = self.get_project(project_id)
            if not project:
                return None
            
            # 获取项目相关统计
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            risks = self.db.get_by_field("risks", "project_id", project_id)
            
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
            total_risks = len(risks)
            high_risks = len([r for r in risks if r.get("risk_level") == "高" or r.get("risk_level") == "严重"])
            
            summary = ProjectSummary(
                project_id=project.project_id,
                project_name=project.project_name,
                project_code=project.project_code,
                status=project.status,
                priority=project.priority,
                project_manager=project.project_manager,
                progress_percentage=project.progress_percentage or 0.0,
                budget_utilization=project.budget_utilization or 0.0,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                total_risks=total_risks,
                high_risks=high_risks
            )
            
            logger.info(f"获取项目 {project_id} 摘要成功")
            return summary
        except Exception as e:
            logger.error(f"获取项目 {project_id} 摘要失败: {str(e)}")
            raise
    
    def get_project_statistics(self) -> ProjectStatistics:
        """获取项目统计信息"""
        try:
            projects = self.db.read("projects")
            
            # 统计项目状态
            total_projects = len(projects)
            active_projects = len([p for p in projects if p.get("status") == "进行中"])
            completed_projects = len([p for p in projects if p.get("status") == "已完成"])
            cancelled_projects = len([p for p in projects if p.get("status") == "已取消"])
            
            # 统计项目类型
            research_projects = len([p for p in projects if p.get("project_type") == "研发项目"])
            implementation_projects = len([p for p in projects if p.get("project_type") == "实施项目"])
            maintenance_projects = len([p for p in projects if p.get("project_type") == "维护项目"])
            consulting_projects = len([p for p in projects if p.get("project_type") == "咨询项目"])
            
            # 统计优先级
            urgent_projects = len([p for p in projects if p.get("priority") == "紧急"])
            high_priority_projects = len([p for p in projects if p.get("priority") == "高"])
            medium_priority_projects = len([p for p in projects if p.get("priority") == "中"])
            low_priority_projects = len([p for p in projects if p.get("priority") == "低"])
            
            # 统计项目阶段
            initiation_projects = len([p for p in projects if p.get("project_phase") == "启动"])
            planning_projects = len([p for p in projects if p.get("project_phase") == "规划"])
            execution_projects = len([p for p in projects if p.get("project_phase") == "执行"])
            monitoring_projects = len([p for p in projects if p.get("project_phase") == "监控"])
            closure_projects = len([p for p in projects if p.get("project_phase") == "收尾"])
            
            statistics = ProjectStatistics(
                total_projects=total_projects,
                active_projects=active_projects,
                completed_projects=completed_projects,
                cancelled_projects=cancelled_projects,
                research_projects=research_projects,
                implementation_projects=implementation_projects,
                maintenance_projects=maintenance_projects,
                consulting_projects=consulting_projects,
                urgent_projects=urgent_projects,
                high_priority_projects=high_priority_projects,
                medium_priority_projects=medium_priority_projects,
                low_priority_projects=low_priority_projects,
                initiation_projects=initiation_projects,
                planning_projects=planning_projects,
                execution_projects=execution_projects,
                monitoring_projects=monitoring_projects,
                closure_projects=closure_projects
            )
            
            logger.info("获取项目统计信息成功")
            return statistics
        except Exception as e:
            logger.error(f"获取项目统计信息失败: {str(e)}")
            raise
    
    def _calculate_project_metrics(self, project_data: Dict[str, Any]) -> ProjectResponse:
        """计算项目指标"""
        try:
            project_id = project_data.get("project_id")
            
            # 获取项目相关数据
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            risks = self.db.get_by_field("risks", "project_id", project_id)
            issues = self.db.get_by_field("issues", "project_id", project_id)
            
            # 计算进度百分比
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
            progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            # 计算预算使用率
            budget = project_data.get("budget", 0)
            actual_cost = project_data.get("actual_cost", 0)
            budget_utilization = (actual_cost / budget * 100) if budget > 0 else 0.0
            
            # 计算进度偏差（简化计算）
            schedule_variance = 0.0  # TODO: 实现更复杂的进度偏差计算
            
            # 计算成本偏差
            cost_variance = actual_cost - budget if budget > 0 else 0.0
            
            # 统计信息
            total_risks = len(risks)
            high_risks = len([r for r in risks if r.get("risk_level") in ["高", "严重"]])
            total_issues = len(issues)
            open_issues = len([i for i in issues if i.get("status") not in ["已解决", "已关闭"]])
            
            # 创建项目响应对象
            project_response = ProjectResponse(
                **project_data,
                progress_percentage=progress_percentage,
                budget_utilization=budget_utilization,
                schedule_variance=schedule_variance,
                cost_variance=cost_variance,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                total_risks=total_risks,
                high_risks=high_risks,
                total_issues=total_issues,
                open_issues=open_issues
            )
            
            return project_response
        except Exception as e:
            logger.error(f"计算项目指标失败: {str(e)}")
            # 返回基础项目数据
            return ProjectResponse(**project_data)


# 创建全局项目服务实例
project_service = ProjectService()

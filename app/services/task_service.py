"""
任务服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse, TaskSummary, TaskStatistics
from app.services.database_service import database_service
from app.utils.logger import get_logger
from app.utils.helpers import generate_id

logger = get_logger(__name__)


class TaskService:
    """任务服务类"""
    
    def __init__(self):
        """初始化任务服务"""
        self.db = database_service.get_database()
        logger.info("任务服务初始化完成")
    
    def get_tasks(self, filters: Optional[Dict[str, Any]] = None, search: Optional[str] = None) -> List[TaskResponse]:
        """获取任务列表"""
        try:
            tasks_data = self.db.read("tasks", filters=filters)
            
            if search:
                tasks_data = self.db.search("tasks", search, ["task_name", "description"])
            
            tasks = []
            for task_data in tasks_data:
                task_response = self._calculate_task_metrics(task_data)
                tasks.append(task_response)
            
            logger.info(f"获取到 {len(tasks)} 个任务")
            return tasks
        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
            raise
    
    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """获取单个任务"""
        try:
            task_data = self.db.read("tasks", task_id)
            if not task_data:
                return None
            
            task_response = self._calculate_task_metrics(task_data)
            logger.info(f"获取任务 {task_id} 成功")
            return task_response
        except Exception as e:
            logger.error(f"获取任务 {task_id} 失败: {str(e)}")
            raise
    
    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """创建任务"""
        try:
            # 生成任务ID
            task_id = f"TASK-{generate_id()[:8].upper()}"
            
            # 创建任务数据
            task_dict = task_data.dict()
            task_dict["task_id"] = task_id
            task_dict["status"] = "待开始"
            task_dict["progress_percentage"] = 0
            
            # 保存到数据库
            created_task = self.db.create("tasks", task_dict)
            
            task_response = self._calculate_task_metrics(created_task)
            
            logger.info(f"创建任务 {task_id} 成功")
            return task_response
        except Exception as e:
            logger.error(f"创建任务失败: {str(e)}")
            raise
    
    def update_task(self, task_id: str, task_data: TaskUpdate) -> Optional[TaskResponse]:
        """更新任务"""
        try:
            # 获取现有任务
            existing_task = self.db.read("tasks", task_id)
            if not existing_task:
                return None
            
            # 更新任务数据
            updates = {k: v for k, v in task_data.dict().items() if v is not None}
            updated_task = self.db.update("tasks", task_id, updates)
            
            if not updated_task:
                return None
            
            task_response = self._calculate_task_metrics(updated_task)
            
            logger.info(f"更新任务 {task_id} 成功")
            return task_response
        except Exception as e:
            logger.error(f"更新任务 {task_id} 失败: {str(e)}")
            raise
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            success = self.db.delete("tasks", task_id)
            if success:
                logger.info(f"删除任务 {task_id} 成功")
            else:
                logger.warning(f"任务 {task_id} 不存在")
            return success
        except Exception as e:
            logger.error(f"删除任务 {task_id} 失败: {str(e)}")
            raise
    
    def get_project_tasks(self, project_id: str, filters: Optional[Dict[str, Any]] = None) -> List[TaskResponse]:
        """获取项目的任务列表"""
        try:
            project_filters = {"project_id": project_id}
            if filters:
                project_filters.update(filters)
            
            tasks = self.get_tasks(project_filters)
            logger.info(f"获取项目 {project_id} 的 {len(tasks)} 个任务")
            return tasks
        except Exception as e:
            logger.error(f"获取项目 {project_id} 的任务列表失败: {str(e)}")
            raise
    
    def get_overdue_tasks(self) -> List[TaskResponse]:
        """获取逾期任务列表"""
        try:
            all_tasks = self.db.read("tasks")
            overdue_tasks = []
            
            current_date = datetime.now()
            
            for task_data in all_tasks:
                due_date = task_data.get("due_date")
                if due_date and task_data.get("status") not in ["已完成", "已取消"]:
                    # 简化日期比较，实际应该解析日期字符串
                    if due_date < current_date.isoformat():
                        task_response = self._calculate_task_metrics(task_data)
                        overdue_tasks.append(task_response)
            
            logger.info(f"获取到 {len(overdue_tasks)} 个逾期任务")
            return overdue_tasks
        except Exception as e:
            logger.error(f"获取逾期任务列表失败: {str(e)}")
            raise
    
    def get_task_statistics(self) -> TaskStatistics:
        """获取任务统计信息"""
        try:
            tasks = self.db.read("tasks")
            
            # 统计任务状态
            total_tasks = len(tasks)
            pending_tasks = len([t for t in tasks if t.get("status") == "待开始"])
            in_progress_tasks = len([t for t in tasks if t.get("status") == "进行中"])
            completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
            paused_tasks = len([t for t in tasks if t.get("status") == "已暂停"])
            cancelled_tasks = len([t for t in tasks if t.get("status") == "已取消"])
            
            # 统计任务类型
            development_tasks = len([t for t in tasks if t.get("task_type") == "开发任务"])
            testing_tasks = len([t for t in tasks if t.get("task_type") == "测试任务"])
            documentation_tasks = len([t for t in tasks if t.get("task_type") == "文档任务"])
            meeting_tasks = len([t for t in tasks if t.get("task_type") == "会议任务"])
            review_tasks = len([t for t in tasks if t.get("task_type") == "评审任务"])
            
            # 统计优先级
            urgent_tasks = len([t for t in tasks if t.get("priority") == "紧急"])
            high_priority_tasks = len([t for t in tasks if t.get("priority") == "高"])
            medium_priority_tasks = len([t for t in tasks if t.get("priority") == "中"])
            low_priority_tasks = len([t for t in tasks if t.get("priority") == "低"])
            
            # 统计逾期任务
            overdue_tasks = len(self.get_overdue_tasks())
            overdue_rate = (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            # 计算完成率
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            # 计算平均进度
            total_progress = sum(t.get("progress_percentage", 0) for t in tasks)
            average_progress = (total_progress / total_tasks) if total_tasks > 0 else 0.0
            
            statistics = TaskStatistics(
                total_tasks=total_tasks,
                pending_tasks=pending_tasks,
                in_progress_tasks=in_progress_tasks,
                completed_tasks=completed_tasks,
                paused_tasks=paused_tasks,
                cancelled_tasks=cancelled_tasks,
                development_tasks=development_tasks,
                testing_tasks=testing_tasks,
                documentation_tasks=documentation_tasks,
                meeting_tasks=meeting_tasks,
                review_tasks=review_tasks,
                urgent_tasks=urgent_tasks,
                high_priority_tasks=high_priority_tasks,
                medium_priority_tasks=medium_priority_tasks,
                low_priority_tasks=low_priority_tasks,
                overdue_tasks=overdue_tasks,
                overdue_rate=overdue_rate,
                completion_rate=completion_rate,
                average_progress=average_progress
            )
            
            logger.info("获取任务统计信息成功")
            return statistics
        except Exception as e:
            logger.error(f"获取任务统计信息失败: {str(e)}")
            raise
    
    def _calculate_task_metrics(self, task_data: Dict[str, Any]) -> TaskResponse:
        """计算任务指标"""
        try:
            # 计算是否逾期
            due_date = task_data.get("due_date")
            is_overdue = False
            days_remaining = None
            
            if due_date:
                # 简化日期比较，实际应该解析日期字符串
                current_date = datetime.now()
                # TODO: 实现更准确的日期比较逻辑
                is_overdue = False  # 临时设置
            
            # 计算完成率（基于进度百分比）
            completion_rate = task_data.get("progress_percentage", 0)
            
            # 创建任务响应对象
            task_response = TaskResponse(
                **task_data,
                is_overdue=is_overdue,
                days_remaining=days_remaining,
                completion_rate=completion_rate
            )
            
            return task_response
        except Exception as e:
            logger.error(f"计算任务指标失败: {str(e)}")
            # 返回基础任务数据
            return TaskResponse(**task_data)


# 创建全局任务服务实例
task_service = TaskService()

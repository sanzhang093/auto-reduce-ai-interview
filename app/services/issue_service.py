"""
问题服务
"""
from typing import List, Optional, Dict, Any
from app.models.issue import Issue, IssueCreate, IssueUpdate, IssueResponse
from app.services.database_service import database_service
from app.utils.logger import get_logger
from app.utils.helpers import generate_id

logger = get_logger(__name__)


class IssueService:
    """问题服务类"""
    
    def __init__(self):
        """初始化问题服务"""
        self.db = database_service.get_database()
        logger.info("问题服务初始化完成")
    
    def get_issues(self, filters: Optional[Dict[str, Any]] = None, search: Optional[str] = None) -> List[IssueResponse]:
        """获取问题列表"""
        try:
            issues_data = self.db.read("issues", filters=filters)
            
            if search:
                issues_data = self.db.search("issues", search, ["issue_title", "description"])
            
            issues = []
            for issue_data in issues_data:
                issue_response = self._calculate_issue_metrics(issue_data)
                issues.append(issue_response)
            
            logger.info(f"获取到 {len(issues)} 个问题")
            return issues
        except Exception as e:
            logger.error(f"获取问题列表失败: {str(e)}")
            raise
    
    def get_issue(self, issue_id: str) -> Optional[IssueResponse]:
        """获取单个问题"""
        try:
            issue_data = self.db.read("issues", issue_id)
            if not issue_data:
                return None
            
            issue_response = self._calculate_issue_metrics(issue_data)
            logger.info(f"获取问题 {issue_id} 成功")
            return issue_response
        except Exception as e:
            logger.error(f"获取问题 {issue_id} 失败: {str(e)}")
            raise
    
    def create_issue(self, issue_data: IssueCreate) -> IssueResponse:
        """创建问题"""
        try:
            # 生成问题ID
            issue_id = f"ISSUE-{generate_id()[:8].upper()}"
            
            # 创建问题数据
            issue_dict = issue_data.dict()
            issue_dict["issue_id"] = issue_id
            issue_dict["status"] = "新建"
            
            # 保存到数据库
            created_issue = self.db.create("issues", issue_dict)
            
            issue_response = self._calculate_issue_metrics(created_issue)
            
            logger.info(f"创建问题 {issue_id} 成功")
            return issue_response
        except Exception as e:
            logger.error(f"创建问题失败: {str(e)}")
            raise
    
    def update_issue(self, issue_id: str, issue_data: IssueUpdate) -> Optional[IssueResponse]:
        """更新问题"""
        try:
            # 获取现有问题
            existing_issue = self.db.read("issues", issue_id)
            if not existing_issue:
                return None
            
            # 更新问题数据
            updates = {k: v for k, v in issue_data.dict().items() if v is not None}
            updated_issue = self.db.update("issues", issue_id, updates)
            
            if not updated_issue:
                return None
            
            issue_response = self._calculate_issue_metrics(updated_issue)
            
            logger.info(f"更新问题 {issue_id} 成功")
            return issue_response
        except Exception as e:
            logger.error(f"更新问题 {issue_id} 失败: {str(e)}")
            raise
    
    def delete_issue(self, issue_id: str) -> bool:
        """删除问题"""
        try:
            success = self.db.delete("issues", issue_id)
            if success:
                logger.info(f"删除问题 {issue_id} 成功")
            else:
                logger.warning(f"问题 {issue_id} 不存在")
            return success
        except Exception as e:
            logger.error(f"删除问题 {issue_id} 失败: {str(e)}")
            raise
    
    def get_project_issues(self, project_id: str, filters: Optional[Dict[str, Any]] = None) -> List[IssueResponse]:
        """获取项目的问题列表"""
        try:
            project_filters = {"project_id": project_id}
            if filters:
                project_filters.update(filters)
            
            issues = self.get_issues(project_filters)
            logger.info(f"获取项目 {project_id} 的 {len(issues)} 个问题")
            return issues
        except Exception as e:
            logger.error(f"获取项目 {project_id} 的问题列表失败: {str(e)}")
            raise
    
    def get_open_issues(self) -> List[IssueResponse]:
        """获取未解决问题列表"""
        try:
            open_statuses = ["新建", "已分配", "进行中"]
            open_issues = []
            
            for status in open_statuses:
                issues = self.get_issues(filters={"status": status})
                open_issues.extend(issues)
            
            logger.info(f"获取到 {len(open_issues)} 个未解决问题")
            return open_issues
        except Exception as e:
            logger.error(f"获取未解决问题列表失败: {str(e)}")
            raise
    
    def _calculate_issue_metrics(self, issue_data: Dict[str, Any]) -> IssueResponse:
        """计算问题指标"""
        try:
            # 计算报告天数（简化计算）
            days_since_reported = 0  # TODO: 实现更准确的日期计算
            
            # 计算解决天数（简化计算）
            days_to_resolve = 0  # TODO: 实现更准确的日期计算
            
            # 计算是否逾期（基于严重程度和报告时间）
            is_overdue = False  # TODO: 实现更复杂的逾期判断逻辑
            
            # 创建问题响应对象
            issue_response = IssueResponse(
                **issue_data,
                days_since_reported=days_since_reported,
                days_to_resolve=days_to_resolve,
                is_overdue=is_overdue
            )
            
            return issue_response
        except Exception as e:
            logger.error(f"计算问题指标失败: {str(e)}")
            # 返回基础问题数据
            return IssueResponse(**issue_data)


# 创建全局问题服务实例
issue_service = IssueService()

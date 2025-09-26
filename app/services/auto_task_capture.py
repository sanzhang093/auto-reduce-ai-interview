"""
自动任务捕捉服务
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.models.task import TaskCreate, TaskType, Priority
from app.models.enums import DataSourceType
from app.utils.logger import get_logger
from app.utils.helpers import generate_id, extract_dates, clean_string
from app.services.database_service import database_service

logger = get_logger(__name__)


@dataclass
class ExtractedTask:
    """提取的任务信息"""
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    task_type: TaskType = TaskType.DEVELOPMENT
    confidence: float = 0.0
    source_text: str = ""
    source_type: DataSourceType = DataSourceType.MEETING


class TaskExtractionRule:
    """任务提取规则"""
    
    def __init__(self):
        """初始化提取规则"""
        # 任务关键词
        self.task_keywords = [
            "负责", "完成", "实现", "开发", "测试", "编写", "创建", "制作",
            "准备", "整理", "检查", "审核", "提交", "部署", "配置", "优化"
        ]
        
        # 时间关键词
        self.time_keywords = [
            "今天", "明天", "后天", "本周", "下周", "本月", "下月",
            "月底", "月初", "年底", "年初", "之前", "之后", "内完成"
        ]
        
        # 优先级关键词
        self.priority_keywords = {
            "紧急": Priority.URGENT,
            "重要": Priority.HIGH,
            "高优先级": Priority.HIGH,
            "优先": Priority.HIGH,
            "一般": Priority.MEDIUM,
            "低优先级": Priority.LOW,
            "不急": Priority.LOW
        }
        
        # 任务类型关键词
        self.task_type_keywords = {
            "开发": TaskType.DEVELOPMENT,
            "测试": TaskType.TESTING,
            "文档": TaskType.DOCUMENTATION,
            "会议": TaskType.MEETING,
            "评审": TaskType.REVIEW
        }
        
        # 人名模式（简化版）
        self.name_pattern = r'[张王李赵刘陈杨黄周吴徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾萧田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤][\u4e00-\u9fa5]{1,2}'
        
        # 日期模式
        self.date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}',
            r'今天|明天|后天',
            r'本周|下周',
            r'本月|下月',
            r'月底|月初'
        ]

    def extract_tasks_from_text(self, text: str, source_type: DataSourceType = DataSourceType.MEETING) -> List[ExtractedTask]:
        """从文本中提取任务"""
        try:
            tasks = []
            sentences = self._split_into_sentences(text)
            
            for sentence in sentences:
                if self._is_task_sentence(sentence):
                    task = self._extract_task_from_sentence(sentence, source_type)
                    if task and task.confidence > 0.3:  # 置信度阈值
                        tasks.append(task)
            
            logger.info(f"从文本中提取到 {len(tasks)} 个任务")
            return tasks
        except Exception as e:
            logger.error(f"提取任务失败: {str(e)}")
            return []

    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        # 简单的句子分割
        sentences = re.split(r'[。！？；\n]', text)
        return [s.strip() for s in sentences if s.strip()]

    def _is_task_sentence(self, sentence: str) -> bool:
        """判断句子是否包含任务信息"""
        # 检查是否包含任务关键词
        has_task_keyword = any(keyword in sentence for keyword in self.task_keywords)
        
        # 检查是否包含人名
        has_person = bool(re.search(self.name_pattern, sentence))
        
        # 检查是否包含时间信息
        has_time = any(keyword in sentence for keyword in self.time_keywords) or \
                  any(re.search(pattern, sentence) for pattern in self.date_patterns)
        
        return has_task_keyword and (has_person or has_time)

    def _extract_task_from_sentence(self, sentence: str, source_type: DataSourceType) -> Optional[ExtractedTask]:
        """从句子中提取任务信息"""
        try:
            # 提取任务标题
            title = self._extract_task_title(sentence)
            if not title:
                return None
            
            # 提取负责人
            assigned_to = self._extract_assigned_person(sentence)
            
            # 提取截止日期
            due_date = self._extract_due_date(sentence)
            
            # 提取优先级
            priority = self._extract_priority(sentence)
            
            # 提取任务类型
            task_type = self._extract_task_type(sentence)
            
            # 计算置信度
            confidence = self._calculate_confidence(sentence, assigned_to, due_date)
            
            return ExtractedTask(
                title=title,
                description=sentence,
                assigned_to=assigned_to,
                due_date=due_date,
                priority=priority,
                task_type=task_type,
                confidence=confidence,
                source_text=sentence,
                source_type=source_type
            )
        except Exception as e:
            logger.error(f"从句子提取任务失败: {str(e)}")
            return None

    def _extract_task_title(self, sentence: str) -> Optional[str]:
        """提取任务标题"""
        # 简化版：取句子中任务关键词后的内容作为标题
        for keyword in self.task_keywords:
            if keyword in sentence:
                # 找到关键词位置，提取后面的内容
                index = sentence.find(keyword)
                if index != -1:
                    title = sentence[index:].strip()
                    # 清理标题
                    title = re.sub(r'[。！？；\n]', '', title)
                    if len(title) > 3:
                        return title[:50]  # 限制长度
        return None

    def _extract_assigned_person(self, sentence: str) -> Optional[str]:
        """提取负责人"""
        # 查找人名
        match = re.search(self.name_pattern, sentence)
        if match:
            return match.group()
        return None

    def _extract_due_date(self, sentence: str) -> Optional[datetime]:
        """提取截止日期"""
        try:
            # 提取日期字符串
            dates = extract_dates(sentence)
            if dates:
                # 简化处理，返回第一个找到的日期
                date_str = dates[0]
                # 这里应该实现更复杂的日期解析逻辑
                # 暂时返回None，实际项目中需要实现完整的日期解析
                return None
            
            # 处理相对时间
            if "今天" in sentence:
                return datetime.now()
            elif "明天" in sentence:
                return datetime.now() + timedelta(days=1)
            elif "后天" in sentence:
                return datetime.now() + timedelta(days=2)
            elif "本周" in sentence:
                return datetime.now() + timedelta(days=7)
            elif "下周" in sentence:
                return datetime.now() + timedelta(days=14)
            
            return None
        except Exception as e:
            logger.error(f"提取日期失败: {str(e)}")
            return None

    def _extract_priority(self, sentence: str) -> Priority:
        """提取优先级"""
        for keyword, priority in self.priority_keywords.items():
            if keyword in sentence:
                return priority
        return Priority.MEDIUM

    def _extract_task_type(self, sentence: str) -> TaskType:
        """提取任务类型"""
        for keyword, task_type in self.task_type_keywords.items():
            if keyword in sentence:
                return task_type
        return TaskType.DEVELOPMENT

    def _calculate_confidence(self, sentence: str, assigned_to: Optional[str], due_date: Optional[datetime]) -> float:
        """计算提取置信度"""
        confidence = 0.0
        
        # 基础置信度
        confidence += 0.3
        
        # 有负责人加分
        if assigned_to:
            confidence += 0.3
        
        # 有截止日期加分
        if due_date:
            confidence += 0.2
        
        # 句子长度适中加分
        if 10 <= len(sentence) <= 100:
            confidence += 0.1
        
        # 包含多个任务关键词加分
        keyword_count = sum(1 for keyword in self.task_keywords if keyword in sentence)
        confidence += min(keyword_count * 0.05, 0.1)
        
        return min(confidence, 1.0)


class AutoTaskCaptureService:
    """自动任务捕捉服务"""
    
    def __init__(self):
        """初始化服务"""
        self.extraction_rule = TaskExtractionRule()
        self.db = database_service.get_database()
        logger.info("自动任务捕捉服务初始化完成")
    
    def extract_tasks_from_meeting(self, meeting_content: str, project_id: str, created_by: str) -> List[Dict[str, Any]]:
        """从会议纪要中提取任务"""
        try:
            extracted_tasks = self.extraction_rule.extract_tasks_from_text(
                meeting_content, DataSourceType.MEETING
            )
            
            created_tasks = []
            for extracted_task in extracted_tasks:
                task_data = TaskCreate(
                    project_id=project_id,
                    task_name=extracted_task.title,
                    description=extracted_task.description,
                    task_type=extracted_task.task_type,
                    priority=extracted_task.priority,
                    assigned_to=extracted_task.assigned_to or created_by,
                    created_by=created_by,
                    due_date=extracted_task.due_date
                )
                
                # 保存任务到数据库
                task_dict = task_data.dict()
                task_dict["task_id"] = f"TASK-{generate_id()[:8].upper()}"
                task_dict["status"] = "待开始"
                task_dict["progress_percentage"] = 0
                
                created_task = self.db.create("tasks", task_dict)
                created_tasks.append(created_task)
                
                logger.info(f"从会议纪要创建任务: {extracted_task.title}")
            
            return created_tasks
        except Exception as e:
            logger.error(f"从会议纪要提取任务失败: {str(e)}")
            raise
    
    def extract_tasks_from_chat(self, chat_content: str, project_id: str, created_by: str) -> List[Dict[str, Any]]:
        """从群聊消息中提取任务"""
        try:
            extracted_tasks = self.extraction_rule.extract_tasks_from_text(
                chat_content, DataSourceType.CHAT
            )
            
            created_tasks = []
            for extracted_task in extracted_tasks:
                task_data = TaskCreate(
                    project_id=project_id,
                    task_name=extracted_task.title,
                    description=extracted_task.description,
                    task_type=extracted_task.task_type,
                    priority=extracted_task.priority,
                    assigned_to=extracted_task.assigned_to or created_by,
                    created_by=created_by,
                    due_date=extracted_task.due_date
                )
                
                # 保存任务到数据库
                task_dict = task_data.dict()
                task_dict["task_id"] = f"TASK-{generate_id()[:8].upper()}"
                task_dict["status"] = "待开始"
                task_dict["progress_percentage"] = 0
                
                created_task = self.db.create("tasks", task_dict)
                created_tasks.append(created_task)
                
                logger.info(f"从群聊消息创建任务: {extracted_task.title}")
            
            return created_tasks
        except Exception as e:
            logger.error(f"从群聊消息提取任务失败: {str(e)}")
            raise
    
    def extract_tasks_from_email(self, email_content: str, project_id: str, created_by: str) -> List[Dict[str, Any]]:
        """从邮件内容中提取任务"""
        try:
            extracted_tasks = self.extraction_rule.extract_tasks_from_text(
                email_content, DataSourceType.EMAIL
            )
            
            created_tasks = []
            for extracted_task in extracted_tasks:
                task_data = TaskCreate(
                    project_id=project_id,
                    task_name=extracted_task.title,
                    description=extracted_task.description,
                    task_type=extracted_task.task_type,
                    priority=extracted_task.priority,
                    assigned_to=extracted_task.assigned_to or created_by,
                    created_by=created_by,
                    due_date=extracted_task.due_date
                )
                
                # 保存任务到数据库
                task_dict = task_data.dict()
                task_dict["task_id"] = f"TASK-{generate_id()[:8].upper()}"
                task_dict["status"] = "待开始"
                task_dict["progress_percentage"] = 0
                
                created_task = self.db.create("tasks", task_dict)
                created_tasks.append(created_task)
                
                logger.info(f"从邮件内容创建任务: {extracted_task.title}")
            
            return created_tasks
        except Exception as e:
            logger.error(f"从邮件内容提取任务失败: {str(e)}")
            raise
    
    def extract_tasks_from_document(self, document_content: str, project_id: str, created_by: str) -> List[Dict[str, Any]]:
        """从文档内容中提取任务"""
        try:
            extracted_tasks = self.extraction_rule.extract_tasks_from_text(
                document_content, DataSourceType.DOCUMENT
            )
            
            created_tasks = []
            for extracted_task in extracted_tasks:
                task_data = TaskCreate(
                    project_id=project_id,
                    task_name=extracted_task.title,
                    description=extracted_task.description,
                    task_type=extracted_task.task_type,
                    priority=extracted_task.priority,
                    assigned_to=extracted_task.assigned_to or created_by,
                    created_by=created_by,
                    due_date=extracted_task.due_date
                )
                
                # 保存任务到数据库
                task_dict = task_data.dict()
                task_dict["task_id"] = f"TASK-{generate_id()[:8].upper()}"
                task_dict["status"] = "待开始"
                task_dict["progress_percentage"] = 0
                
                created_task = self.db.create("tasks", task_dict)
                created_tasks.append(created_task)
                
                logger.info(f"从文档内容创建任务: {extracted_task.title}")
            
            return created_tasks
        except Exception as e:
            logger.error(f"从文档内容提取任务失败: {str(e)}")
            raise
    
    def batch_extract_tasks(self, content_list: List[Dict[str, str]], project_id: str, created_by: str) -> Dict[str, List[Dict[str, Any]]]:
        """批量提取任务"""
        try:
            results = {
                "meeting": [],
                "chat": [],
                "email": [],
                "document": []
            }
            
            for content_item in content_list:
                content_type = content_item.get("type", "meeting")
                content_text = content_item.get("content", "")
                
                if content_type == "meeting":
                    tasks = self.extract_tasks_from_meeting(content_text, project_id, created_by)
                    results["meeting"].extend(tasks)
                elif content_type == "chat":
                    tasks = self.extract_tasks_from_chat(content_text, project_id, created_by)
                    results["chat"].extend(tasks)
                elif content_type == "email":
                    tasks = self.extract_tasks_from_email(content_text, project_id, created_by)
                    results["email"].extend(tasks)
                elif content_type == "document":
                    tasks = self.extract_tasks_from_document(content_text, project_id, created_by)
                    results["document"].extend(tasks)
            
            total_tasks = sum(len(tasks) for tasks in results.values())
            logger.info(f"批量提取任务完成，共创建 {total_tasks} 个任务")
            
            return results
        except Exception as e:
            logger.error(f"批量提取任务失败: {str(e)}")
            raise
    
    def get_extraction_statistics(self, project_id: str) -> Dict[str, Any]:
        """获取任务提取统计信息"""
        try:
            # 获取项目所有任务
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 统计各来源的任务数量
            source_stats = {
                "meeting": 0,
                "chat": 0,
                "email": 0,
                "document": 0,
                "manual": 0
            }
            
            # 统计任务状态
            status_stats = {
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "paused": 0,
                "cancelled": 0
            }
            
            for task in tasks:
                # 根据任务描述判断来源（简化版）
                description = task.get("description", "")
                if "会议" in description or "meeting" in description.lower():
                    source_stats["meeting"] += 1
                elif "群聊" in description or "chat" in description.lower():
                    source_stats["chat"] += 1
                elif "邮件" in description or "email" in description.lower():
                    source_stats["email"] += 1
                elif "文档" in description or "document" in description.lower():
                    source_stats["document"] += 1
                else:
                    source_stats["manual"] += 1
                
                # 统计状态
                status = task.get("status", "pending")
                if status == "待开始":
                    status_stats["pending"] += 1
                elif status == "进行中":
                    status_stats["in_progress"] += 1
                elif status == "已完成":
                    status_stats["completed"] += 1
                elif status == "已暂停":
                    status_stats["paused"] += 1
                elif status == "已取消":
                    status_stats["cancelled"] += 1
            
            return {
                "total_tasks": len(tasks),
                "source_distribution": source_stats,
                "status_distribution": status_stats,
                "extraction_success_rate": 0.85  # 模拟数据
            }
        except Exception as e:
            logger.error(f"获取提取统计信息失败: {str(e)}")
            raise


# 创建全局服务实例
auto_task_capture_service = AutoTaskCaptureService()

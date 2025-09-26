"""
通义千问Agent服务
"""
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import dashscope
from dashscope import Generation
from app.utils.logger import get_logger
from app.services.database_service import database_service
from config.settings import settings

logger = get_logger(__name__)


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    message_id: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class ChatSession:
    """聊天会话"""
    session_id: str
    user_id: str
    project_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage]
    context: Dict[str, Any]
    is_active: bool = True


@dataclass
class RAGDocument:
    """RAG文档"""
    doc_id: str
    title: str
    content: str
    doc_type: str  # project, task, risk, issue, meeting, document
    project_id: Optional[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None


@dataclass
class RAGSearchResult:
    """RAG搜索结果"""
    doc_id: str
    title: str
    content: str
    doc_type: str
    relevance_score: float
    metadata: Dict[str, Any]


class QwenAgentService:
    """通义千问Agent服务"""
    
    def __init__(self):
        """初始化服务"""
        self.db = database_service.get_database()
        self.api_key = settings.qwen_api_key
        self.model = settings.qwen_model
        self.max_tokens = settings.qwen_max_tokens
        self.temperature = settings.qwen_temperature
        
        # 设置API密钥
        dashscope.api_key = self.api_key
        
        # 初始化向量数据库（简化版，使用内存存储）
        self.vector_db = {}
        self.chat_sessions = {}
        
        logger.info("通义千问Agent服务初始化完成")
    
    async def chat(self, user_id: str, message: str, session_id: Optional[str] = None, 
                   project_id: Optional[str] = None) -> Dict[str, Any]:
        """智能对话"""
        try:
            logger.info(f"用户 {user_id} 发起对话: {message[:50]}...")
            
            # 获取或创建会话
            session = self._get_or_create_session(user_id, session_id, project_id)
            
            # 添加用户消息
            user_msg = ChatMessage(
                role="user",
                content=message,
                timestamp=datetime.now(),
                message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            )
            session.messages.append(user_msg)
            
            # RAG检索相关文档
            relevant_docs = await self._search_relevant_documents(message, project_id)
            
            # 构建上下文
            context = self._build_context(session, relevant_docs, project_id)
            
            # 调用通义千问API
            response = await self._call_qwen_api(context, message)
            
            # 添加助手回复
            assistant_msg = ChatMessage(
                role="assistant",
                content=response["content"],
                timestamp=datetime.now(),
                message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                context={"relevant_docs": [asdict(doc) for doc in relevant_docs]}
            )
            session.messages.append(assistant_msg)
            
            # 更新会话
            session.updated_at = datetime.now()
            self.chat_sessions[session.session_id] = session
            
            # 保存会话到数据库
            self._save_session(session)
            
            return {
                "session_id": session.session_id,
                "response": response["content"],
                "relevant_docs": [asdict(doc) for doc in relevant_docs],
                "context": context,
                "timestamp": assistant_msg.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"智能对话失败: {str(e)}")
            raise
    
    def _get_or_create_session(self, user_id: str, session_id: Optional[str], 
                              project_id: Optional[str]) -> ChatSession:
        """获取或创建聊天会话"""
        if session_id and session_id in self.chat_sessions:
            return self.chat_sessions[session_id]
        
        # 创建新会话
        new_session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = ChatSession(
            session_id=new_session_id,
            user_id=user_id,
            project_id=project_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[],
            context={}
        )
        
        self.chat_sessions[new_session_id] = session
        return session
    
    async def _search_relevant_documents(self, query: str, project_id: Optional[str]) -> List[RAGSearchResult]:
        """搜索相关文档"""
        try:
            # 简化版RAG检索，实际项目中应该使用向量数据库
            relevant_docs = []
            
            # 从项目数据中搜索
            if project_id:
                # 搜索项目信息
                project = self.db.read("projects", project_id)
                if project:
                    doc = RAGDocument(
                        doc_id=f"project_{project_id}",
                        title=f"项目: {project.get('project_name', '')}",
                        content=f"项目名称: {project.get('project_name', '')}\n项目状态: {project.get('status', '')}\n项目经理: {project.get('project_manager', '')}",
                        doc_type="project",
                        project_id=project_id,
                        metadata=project
                    )
                    relevant_docs.append(RAGSearchResult(
                        doc_id=doc.doc_id,
                        title=doc.title,
                        content=doc.content,
                        doc_type=doc.doc_type,
                        relevance_score=0.9,
                        metadata=doc.metadata
                    ))
                
                # 搜索任务信息
                tasks = self.db.get_by_field("tasks", "project_id", project_id)
                for task in tasks[:3]:  # 限制数量
                    doc = RAGDocument(
                        doc_id=f"task_{task.get('task_id', '')}",
                        title=f"任务: {task.get('task_name', '')}",
                        content=f"任务名称: {task.get('task_name', '')}\n任务状态: {task.get('status', '')}\n负责人: {task.get('assigned_to', '')}",
                        doc_type="task",
                        project_id=project_id,
                        metadata=task
                    )
                    relevant_docs.append(RAGSearchResult(
                        doc_id=doc.doc_id,
                        title=doc.title,
                        content=doc.content,
                        doc_type=doc.doc_type,
                        relevance_score=0.8,
                        metadata=doc.metadata
                    ))
                
                # 搜索风险信息
                risks = self.db.get_by_field("risks", "project_id", project_id)
                for risk in risks[:2]:  # 限制数量
                    doc = RAGDocument(
                        doc_id=f"risk_{risk.get('risk_id', '')}",
                        title=f"风险: {risk.get('risk_title', '')}",
                        content=f"风险标题: {risk.get('risk_title', '')}\n风险等级: {risk.get('risk_level', '')}\n负责人: {risk.get('owner', '')}",
                        doc_type="risk",
                        project_id=project_id,
                        metadata=risk
                    )
                    relevant_docs.append(RAGSearchResult(
                        doc_id=doc.doc_id,
                        title=doc.title,
                        content=doc.content,
                        doc_type=doc.doc_type,
                        relevance_score=0.7,
                        metadata=doc.metadata
                    ))
            
            # 根据查询内容调整相关性分数
            query_lower = query.lower()
            for doc in relevant_docs:
                if any(keyword in doc.content.lower() for keyword in query_lower.split()):
                    doc.relevance_score += 0.1
            
            # 按相关性排序
            relevant_docs.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return relevant_docs[:5]  # 返回前5个最相关的文档
        except Exception as e:
            logger.error(f"搜索相关文档失败: {str(e)}")
            return []
    
    def _build_context(self, session: ChatSession, relevant_docs: List[RAGSearchResult], 
                      project_id: Optional[str]) -> str:
        """构建上下文"""
        context_parts = []
        
        # 添加系统提示
        system_prompt = """你是一个专业的项目管理AI助手，能够帮助用户管理项目、分析任务、识别风险、生成报告等。
请根据提供的项目信息，给出专业、准确的回答。如果信息不足，请说明需要更多信息。"""
        context_parts.append(f"系统提示: {system_prompt}")
        
        # 添加项目上下文
        if project_id:
            context_parts.append(f"当前项目ID: {project_id}")
        
        # 添加相关文档
        if relevant_docs:
            context_parts.append("相关项目信息:")
            for doc in relevant_docs:
                context_parts.append(f"- {doc.title}: {doc.content}")
        
        # 添加对话历史（最近3轮）
        if session.messages:
            context_parts.append("对话历史:")
            recent_messages = session.messages[-6:]  # 最近3轮对话
            for msg in recent_messages:
                context_parts.append(f"{msg.role}: {msg.content}")
        
        return "\n".join(context_parts)
    
    async def _call_qwen_api(self, context: str, user_message: str) -> Dict[str, Any]:
        """调用通义千问API"""
        try:
            # 构建完整的提示
            full_prompt = f"{context}\n\n用户问题: {user_message}\n\n请回答:"
            
            # 调用通义千问API
            response = Generation.call(
                model=self.model,
                prompt=full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            if response.status_code == 200:
                content = response.output.text
                return {
                    "content": content,
                    "status": "success",
                    "model": self.model
                }
            else:
                logger.error(f"通义千问API调用失败: {response.message}")
                return {
                    "content": "抱歉，我暂时无法回答您的问题，请稍后再试。",
                    "status": "error",
                    "error": response.message
                }
        except Exception as e:
            logger.error(f"调用通义千问API失败: {str(e)}")
            return {
                "content": "抱歉，我暂时无法回答您的问题，请稍后再试。",
                "status": "error",
                "error": str(e)
            }
    
    def _save_session(self, session: ChatSession):
        """保存会话到数据库"""
        try:
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "project_id": session.project_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "messages": [asdict(msg) for msg in session.messages],
                "context": session.context,
                "is_active": session.is_active
            }
            
            # 保存到数据库
            self.db.create("chat_sessions", session_data)
        except Exception as e:
            logger.error(f"保存会话失败: {str(e)}")
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取聊天历史"""
        try:
            if session_id in self.chat_sessions:
                session = self.chat_sessions[session_id]
                return [asdict(msg) for msg in session.messages]
            else:
                # 从数据库加载
                session_data = self.db.read("chat_sessions", session_id)
                if session_data:
                    return session_data.get("messages", [])
                return []
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            return []
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        try:
            sessions = self.db.get_by_field("chat_sessions", "user_id", user_id)
            return [
                {
                    "session_id": session["session_id"],
                    "project_id": session.get("project_id"),
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                    "message_count": len(session.get("messages", [])),
                    "is_active": session.get("is_active", True)
                }
                for session in sessions
            ]
        except Exception as e:
            logger.error(f"获取用户会话失败: {str(e)}")
            return []
    
    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        try:
            if session_id in self.chat_sessions:
                session = self.chat_sessions[session_id]
                session.is_active = False
                session.updated_at = datetime.now()
                self._save_session(session)
                return True
            return False
        except Exception as e:
            logger.error(f"关闭会话失败: {str(e)}")
            return False
    
    async def process_task_request(self, user_id: str, request: str, project_id: str) -> Dict[str, Any]:
        """处理任务相关请求"""
        try:
            logger.info(f"处理任务请求: {request}")
            
            # 分析请求类型
            request_type = self._analyze_request_type(request)
            
            if request_type == "create_task":
                return await self._handle_create_task_request(user_id, request, project_id)
            elif request_type == "update_task":
                return await self._handle_update_task_request(user_id, request, project_id)
            elif request_type == "query_task":
                return await self._handle_query_task_request(user_id, request, project_id)
            elif request_type == "analyze_progress":
                return await self._handle_analyze_progress_request(user_id, request, project_id)
            else:
                # 使用通用对话处理
                return await self.chat(user_id, request, project_id=project_id)
        except Exception as e:
            logger.error(f"处理任务请求失败: {str(e)}")
            raise
    
    def _analyze_request_type(self, request: str) -> str:
        """分析请求类型"""
        request_lower = request.lower()
        
        if any(keyword in request_lower for keyword in ["创建任务", "新建任务", "添加任务"]):
            return "create_task"
        elif any(keyword in request_lower for keyword in ["更新任务", "修改任务", "编辑任务"]):
            return "update_task"
        elif any(keyword in request_lower for keyword in ["查询任务", "查看任务", "任务列表"]):
            return "query_task"
        elif any(keyword in request_lower for keyword in ["分析进度", "进度分析", "项目进度"]):
            return "analyze_progress"
        else:
            return "general"
    
    async def _handle_create_task_request(self, user_id: str, request: str, project_id: str) -> Dict[str, Any]:
        """处理创建任务请求"""
        # 使用AI分析任务信息
        analysis_prompt = f"""
        请分析以下任务创建请求，提取任务信息：
        请求: {request}
        
        请以JSON格式返回：
        {{
            "task_name": "任务名称",
            "description": "任务描述",
            "assigned_to": "负责人",
            "priority": "优先级(低/中/高/紧急)",
            "due_date": "截止日期",
            "task_type": "任务类型(开发任务/测试任务/文档任务/会议任务/评审任务)"
        }}
        """
        
        response = await self._call_qwen_api("", analysis_prompt)
        
        try:
            # 解析AI返回的JSON
            task_info = json.loads(response["content"])
            
            # 创建任务
            task_data = {
                "project_id": project_id,
                "task_name": task_info.get("task_name", "新任务"),
                "description": task_info.get("description", ""),
                "assigned_to": task_info.get("assigned_to", user_id),
                "priority": task_info.get("priority", "中"),
                "task_type": task_info.get("task_type", "开发任务"),
                "created_by": user_id
            }
            
            # 保存任务到数据库
            task_data["task_id"] = f"TASK-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            task_data["status"] = "待开始"
            task_data["progress_percentage"] = 0
            
            created_task = self.db.create("tasks", task_data)
            
            return {
                "action": "task_created",
                "task": created_task,
                "message": f"已成功创建任务: {task_info.get('task_name', '新任务')}"
            }
        except Exception as e:
            logger.error(f"解析AI返回的任务信息失败: {str(e)}")
            return {
                "action": "error",
                "message": "抱歉，我无法理解您的任务创建请求，请提供更详细的信息。"
            }
    
    async def _handle_update_task_request(self, user_id: str, request: str, project_id: str) -> Dict[str, Any]:
        """处理更新任务请求"""
        # 简化实现
        return {
            "action": "task_update",
            "message": "任务更新功能正在开发中，请使用项目管理界面进行更新。"
        }
    
    async def _handle_query_task_request(self, user_id: str, request: str, project_id: str) -> Dict[str, Any]:
        """处理查询任务请求"""
        try:
            # 获取项目任务
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 使用AI分析查询意图
            analysis_prompt = f"""
            请分析以下任务查询请求，确定查询条件：
            请求: {request}
            
            请返回查询条件：
            - status: 任务状态筛选
            - assigned_to: 负责人筛选
            - priority: 优先级筛选
            """
            
            response = await self._call_qwen_api("", analysis_prompt)
            
            # 简化筛选逻辑
            filtered_tasks = tasks[:10]  # 限制返回数量
            
            return {
                "action": "task_query",
                "tasks": filtered_tasks,
                "message": f"找到 {len(filtered_tasks)} 个任务"
            }
        except Exception as e:
            logger.error(f"查询任务失败: {str(e)}")
            return {
                "action": "error",
                "message": "查询任务时发生错误，请稍后再试。"
            }
    
    async def _handle_analyze_progress_request(self, user_id: str, request: str, project_id: str) -> Dict[str, Any]:
        """处理分析进度请求"""
        try:
            # 获取项目数据
            project = self.db.read("projects", project_id)
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            
            # 计算进度统计
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get("status") == "已完成"])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # 使用AI生成分析报告
            analysis_prompt = f"""
            请分析以下项目进度数据，生成分析报告：
            项目名称: {project.get('project_name', '') if project else ''}
            总任务数: {total_tasks}
            已完成任务: {completed_tasks}
            完成率: {completion_rate:.1f}%
            
            请生成简洁的进度分析报告。
            """
            
            response = await self._call_qwen_api("", analysis_prompt)
            
            return {
                "action": "progress_analysis",
                "analysis": response["content"],
                "statistics": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_rate": completion_rate
                },
                "message": "进度分析完成"
            }
        except Exception as e:
            logger.error(f"分析进度失败: {str(e)}")
            return {
                "action": "error",
                "message": "分析进度时发生错误，请稍后再试。"
            }


# 创建全局服务实例
qwen_agent_service = QwenAgentService()

"""
智能对话API
"""
from fastapi import APIRouter, HTTPException, Body, Query, Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.base import APIResponse
from app.services.qwen_agent import qwen_agent_service
from app.services.rag_system import rag_system
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    project_id: Optional[str] = Field(None, description="项目ID")


class TaskRequest(BaseModel):
    """任务请求"""
    user_id: str = Field(..., description="用户ID")
    request: str = Field(..., description="任务请求内容")
    project_id: str = Field(..., description="项目ID")


class RAGSearchRequest(BaseModel):
    """RAG搜索请求"""
    query: str = Field(..., description="搜索查询")
    project_id: Optional[str] = Field(None, description="项目ID")
    doc_types: Optional[List[str]] = Field(None, description="文档类型筛选")
    top_k: int = Field(default=5, description="返回结果数量")


@router.post("/auto-reduce/intelligent-chat/chat", response_model=APIResponse)
async def chat_with_ai(request: ChatRequest):
    """与AI进行智能对话"""
    try:
        logger.info(f"用户 {request.user_id} 发起对话")
        
        response = await qwen_agent_service.chat(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id,
            project_id=request.project_id
        )
        
        return APIResponse.success_response(
            data=response,
            message="智能对话完成"
        )
    except Exception as e:
        logger.error(f"智能对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"智能对话失败: {str(e)}")


@router.post("/auto-reduce/intelligent-chat/task-request", response_model=APIResponse)
async def process_task_request(request: TaskRequest):
    """处理任务相关请求"""
    try:
        logger.info(f"处理任务请求: {request.request}")
        
        response = await qwen_agent_service.process_task_request(
            user_id=request.user_id,
            request=request.request,
            project_id=request.project_id
        )
        
        return APIResponse.success_response(
            data=response,
            message="任务请求处理完成"
        )
    except Exception as e:
        logger.error(f"处理任务请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理任务请求失败: {str(e)}")


@router.get("/auto-reduce/intelligent-chat/history/{session_id}", response_model=APIResponse)
async def get_chat_history(session_id: str = Path(..., description="会话ID")):
    """获取聊天历史"""
    try:
        history = qwen_agent_service.get_chat_history(session_id)
        
        return APIResponse.success_response(
            data={
                "session_id": session_id,
                "messages": history,
                "message_count": len(history)
            },
            message="获取聊天历史成功"
        )
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取聊天历史失败: {str(e)}")


@router.get("/auto-reduce/intelligent-chat/sessions/{user_id}", response_model=APIResponse)
async def get_user_sessions(user_id: str = Path(..., description="用户ID")):
    """获取用户的所有会话"""
    try:
        sessions = qwen_agent_service.get_user_sessions(user_id)
        
        return APIResponse.success_response(
            data={
                "user_id": user_id,
                "sessions": sessions,
                "session_count": len(sessions)
            },
            message="获取用户会话成功"
        )
    except Exception as e:
        logger.error(f"获取用户会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户会话失败: {str(e)}")


@router.delete("/auto-reduce/intelligent-chat/sessions/{session_id}", response_model=APIResponse)
async def close_session(session_id: str = Path(..., description="会话ID")):
    """关闭会话"""
    try:
        success = qwen_agent_service.close_session(session_id)
        
        if success:
            return APIResponse.success_response(
                data={"session_id": session_id},
                message="会话已关闭"
            )
        else:
            raise HTTPException(status_code=404, detail="会话不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"关闭会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"关闭会话失败: {str(e)}")


@router.post("/auto-reduce/intelligent-chat/rag/search", response_model=APIResponse)
async def search_documents(request: RAGSearchRequest):
    """搜索相关文档"""
    try:
        logger.info(f"RAG搜索: {request.query}")
        
        results = rag_system.search_documents(
            query=request.query,
            top_k=request.top_k,
            project_id=request.project_id,
            doc_types=request.doc_types
        )
        
        return APIResponse.success_response(
            data={
                "query": request.query,
                "results": [
                    {
                        "doc_id": result.doc_id,
                        "title": result.title,
                        "content": result.content,
                        "doc_type": result.doc_type,
                        "relevance_score": result.relevance_score,
                        "metadata": result.metadata
                    }
                    for result in results
                ],
                "result_count": len(results)
            },
            message=f"搜索完成，找到 {len(results)} 个相关文档"
        )
    except Exception as e:
        logger.error(f"RAG搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG搜索失败: {str(e)}")


@router.post("/auto-reduce/intelligent-chat/rag/index/{project_id}", response_model=APIResponse)
async def index_project_data(project_id: str = Path(..., description="项目ID")):
    """索引项目数据"""
    try:
        logger.info(f"索引项目 {project_id} 的数据")
        
        indexed_count = rag_system.index_project_data(project_id)
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "indexed_count": indexed_count
            },
            message=f"项目数据索引完成，共索引 {indexed_count} 个文档"
        )
    except Exception as e:
        logger.error(f"索引项目数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"索引项目数据失败: {str(e)}")


@router.get("/auto-reduce/intelligent-chat/rag/document/{doc_id}", response_model=APIResponse)
async def get_document(doc_id: str = Path(..., description="文档ID")):
    """获取文档"""
    try:
        document = rag_system.get_document(doc_id)
        
        if document:
            return APIResponse.success_response(
                data={
                    "doc_id": document.doc_id,
                    "title": document.title,
                    "content": document.content,
                    "doc_type": document.doc_type,
                    "project_id": document.project_id,
                    "metadata": document.metadata,
                    "created_at": document.created_at.isoformat() if document.created_at else None
                },
                message="获取文档成功"
            )
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")


@router.delete("/auto-reduce/intelligent-chat/rag/document/{doc_id}", response_model=APIResponse)
async def delete_document(doc_id: str = Path(..., description="文档ID")):
    """删除文档"""
    try:
        success = rag_system.delete_document(doc_id)
        
        if success:
            return APIResponse.success_response(
                data={"doc_id": doc_id},
                message="文档已删除"
            )
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.get("/auto-reduce/intelligent-chat/rag/statistics", response_model=APIResponse)
async def get_rag_statistics():
    """获取RAG系统统计信息"""
    try:
        statistics = rag_system.get_system_statistics()
        
        return APIResponse.success_response(
            data=statistics,
            message="获取RAG系统统计信息成功"
        )
    except Exception as e:
        logger.error(f"获取RAG系统统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取RAG系统统计信息失败: {str(e)}")


@router.post("/auto-reduce/intelligent-chat/analyze", response_model=APIResponse)
async def analyze_project_data(
    project_id: str = Body(..., description="项目ID"),
    analysis_type: str = Body(..., description="分析类型"),
    user_id: str = Body(..., description="用户ID")
):
    """分析项目数据"""
    try:
        logger.info(f"分析项目 {project_id} 的 {analysis_type} 数据")
        
        # 根据分析类型调用不同的分析功能
        if analysis_type == "progress":
            response = await qwen_agent_service._handle_analyze_progress_request(
                user_id, f"分析项目 {project_id} 的进度", project_id
            )
        elif analysis_type == "risks":
            # 获取风险数据并分析
            risks = rag_system.search_documents(
                query="项目风险分析",
                project_id=project_id,
                doc_types=["risk"]
            )
            response = {
                "action": "risk_analysis",
                "analysis": f"项目共有 {len(risks)} 个风险需要关注",
                "risks": [asdict(risk) for risk in risks],
                "message": "风险分析完成"
            }
        elif analysis_type == "tasks":
            # 获取任务数据并分析
            tasks = rag_system.search_documents(
                query="项目任务分析",
                project_id=project_id,
                doc_types=["task"]
            )
            response = {
                "action": "task_analysis",
                "analysis": f"项目共有 {len(tasks)} 个任务",
                "tasks": [asdict(task) for task in tasks],
                "message": "任务分析完成"
            }
        else:
            response = {
                "action": "general_analysis",
                "analysis": "正在进行项目数据分析...",
                "message": "分析完成"
            }
        
        return APIResponse.success_response(
            data=response,
            message=f"项目 {analysis_type} 分析完成"
        )
    except Exception as e:
        logger.error(f"分析项目数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析项目数据失败: {str(e)}")


@router.get("/auto-reduce/intelligent-chat/suggestions", response_model=APIResponse)
async def get_ai_suggestions(
    project_id: str = Query(..., description="项目ID"),
    suggestion_type: str = Query(default="general", description="建议类型")
):
    """获取AI建议"""
    try:
        logger.info(f"获取项目 {project_id} 的 {suggestion_type} 建议")
        
        # 获取项目数据
        project_docs = rag_system.search_documents(
            query="项目信息",
            project_id=project_id,
            doc_types=["project"]
        )
        
        task_docs = rag_system.search_documents(
            query="任务信息",
            project_id=project_id,
            doc_types=["task"]
        )
        
        risk_docs = rag_system.search_documents(
            query="风险信息",
            project_id=project_id,
            doc_types=["risk"]
        )
        
        # 生成建议
        suggestions = []
        
        if suggestion_type == "general":
            suggestions = [
                "建议定期更新项目进度",
                "关注高风险任务的状态",
                "及时处理项目中的问题"
            ]
        elif suggestion_type == "tasks":
            suggestions = [
                f"项目共有 {len(task_docs)} 个任务，建议按优先级排序",
                "检查是否有逾期任务需要处理",
                "考虑任务依赖关系优化"
            ]
        elif suggestion_type == "risks":
            suggestions = [
                f"项目共有 {len(risk_docs)} 个风险，建议制定缓解计划",
                "重点关注高风险项目",
                "建立风险监控机制"
            ]
        
        return APIResponse.success_response(
            data={
                "project_id": project_id,
                "suggestion_type": suggestion_type,
                "suggestions": suggestions,
                "data_summary": {
                    "projects": len(project_docs),
                    "tasks": len(task_docs),
                    "risks": len(risk_docs)
                }
            },
            message=f"获取 {suggestion_type} 建议成功"
        )
    except Exception as e:
        logger.error(f"获取AI建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取AI建议失败: {str(e)}")


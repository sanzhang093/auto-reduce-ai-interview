"""
自动任务捕捉API
"""
from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.base import APIResponse
from app.services.auto_task_capture import auto_task_capture_service
from app.models.enums import DataSourceType
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class TaskExtractionRequest(BaseModel):
    """任务提取请求"""
    content: str = Field(..., description="要提取任务的文本内容")
    project_id: str = Field(..., description="项目ID")
    created_by: str = Field(..., description="创建者")
    source_type: DataSourceType = Field(default=DataSourceType.MEETING, description="数据源类型")


class BatchTaskExtractionRequest(BaseModel):
    """批量任务提取请求"""
    content_list: List[Dict[str, str]] = Field(..., description="内容列表，每个元素包含type和content字段")
    project_id: str = Field(..., description="项目ID")
    created_by: str = Field(..., description="创建者")


class TaskExtractionResponse(BaseModel):
    """任务提取响应"""
    extracted_tasks: List[Dict[str, Any]] = Field(description="提取的任务列表")
    total_count: int = Field(description="提取的任务总数")
    success_rate: float = Field(description="提取成功率")


@router.post("/auto-reduce/task-capture/extract", response_model=APIResponse)
async def extract_tasks_from_content(request: TaskExtractionRequest):
    """从文本内容中提取任务"""
    try:
        logger.info(f"开始从 {request.source_type} 中提取任务")
        
        if request.source_type == DataSourceType.MEETING:
            tasks = auto_task_capture_service.extract_tasks_from_meeting(
                request.content, request.project_id, request.created_by
            )
        elif request.source_type == DataSourceType.CHAT:
            tasks = auto_task_capture_service.extract_tasks_from_chat(
                request.content, request.project_id, request.created_by
            )
        elif request.source_type == DataSourceType.EMAIL:
            tasks = auto_task_capture_service.extract_tasks_from_email(
                request.content, request.project_id, request.created_by
            )
        elif request.source_type == DataSourceType.DOCUMENT:
            tasks = auto_task_capture_service.extract_tasks_from_document(
                request.content, request.project_id, request.created_by
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的数据源类型")
        
        response = TaskExtractionResponse(
            extracted_tasks=tasks,
            total_count=len(tasks),
            success_rate=0.85  # 模拟成功率
        )
        
        return APIResponse.success_response(
            data=response.dict(),
            message=f"成功从 {request.source_type} 中提取 {len(tasks)} 个任务"
        )
    except Exception as e:
        logger.error(f"提取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提取任务失败: {str(e)}")


@router.post("/auto-reduce/task-capture/batch-extract", response_model=APIResponse)
async def batch_extract_tasks(request: BatchTaskExtractionRequest):
    """批量提取任务"""
    try:
        logger.info(f"开始批量提取任务，共 {len(request.content_list)} 个内容项")
        
        results = auto_task_capture_service.batch_extract_tasks(
            request.content_list, request.project_id, request.created_by
        )
        
        # 统计总数
        total_tasks = sum(len(tasks) for tasks in results.values())
        
        return APIResponse.success_response(
            data={
                "results": results,
                "total_tasks": total_tasks,
                "summary": {
                    "meeting_tasks": len(results["meeting"]),
                    "chat_tasks": len(results["chat"]),
                    "email_tasks": len(results["email"]),
                    "document_tasks": len(results["document"])
                }
            },
            message=f"批量提取完成，共创建 {total_tasks} 个任务"
        )
    except Exception as e:
        logger.error(f"批量提取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量提取任务失败: {str(e)}")


@router.post("/auto-reduce/task-capture/meeting", response_model=APIResponse)
async def extract_tasks_from_meeting(
    content: str = Body(..., description="会议纪要内容"),
    project_id: str = Body(..., description="项目ID"),
    created_by: str = Body(..., description="创建者")
):
    """从会议纪要中提取任务"""
    try:
        logger.info("从会议纪要中提取任务")
        
        tasks = auto_task_capture_service.extract_tasks_from_meeting(
            content, project_id, created_by
        )
        
        return APIResponse.success_response(
            data={
                "tasks": tasks,
                "count": len(tasks)
            },
            message=f"从会议纪要中成功提取 {len(tasks)} 个任务"
        )
    except Exception as e:
        logger.error(f"从会议纪要提取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从会议纪要提取任务失败: {str(e)}")


@router.post("/auto-reduce/task-capture/chat", response_model=APIResponse)
async def extract_tasks_from_chat(
    content: str = Body(..., description="群聊消息内容"),
    project_id: str = Body(..., description="项目ID"),
    created_by: str = Body(..., description="创建者")
):
    """从群聊消息中提取任务"""
    try:
        logger.info("从群聊消息中提取任务")
        
        tasks = auto_task_capture_service.extract_tasks_from_chat(
            content, project_id, created_by
        )
        
        return APIResponse.success_response(
            data={
                "tasks": tasks,
                "count": len(tasks)
            },
            message=f"从群聊消息中成功提取 {len(tasks)} 个任务"
        )
    except Exception as e:
        logger.error(f"从群聊消息提取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从群聊消息提取任务失败: {str(e)}")


@router.post("/auto-reduce/task-capture/email", response_model=APIResponse)
async def extract_tasks_from_email(
    content: str = Body(..., description="邮件内容"),
    project_id: str = Body(..., description="项目ID"),
    created_by: str = Body(..., description="创建者")
):
    """从邮件内容中提取任务"""
    try:
        logger.info("从邮件内容中提取任务")
        
        tasks = auto_task_capture_service.extract_tasks_from_email(
            content, project_id, created_by
        )
        
        return APIResponse.success_response(
            data={
                "tasks": tasks,
                "count": len(tasks)
            },
            message=f"从邮件内容中成功提取 {len(tasks)} 个任务"
        )
    except Exception as e:
        logger.error(f"从邮件内容提取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从邮件内容提取任务失败: {str(e)}")


@router.post("/auto-reduce/task-capture/document", response_model=APIResponse)
async def extract_tasks_from_document(
    content: str = Body(..., description="文档内容"),
    project_id: str = Body(..., description="项目ID"),
    created_by: str = Body(..., description="创建者")
):
    """从文档内容中提取任务"""
    try:
        logger.info("从文档内容中提取任务")
        
        tasks = auto_task_capture_service.extract_tasks_from_document(
            content, project_id, created_by
        )
        
        return APIResponse.success_response(
            data={
                "tasks": tasks,
                "count": len(tasks)
            },
            message=f"从文档内容中成功提取 {len(tasks)} 个任务"
        )
    except Exception as e:
        logger.error(f"从文档内容提取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从文档内容提取任务失败: {str(e)}")


@router.get("/auto-reduce/task-capture/statistics/{project_id}", response_model=APIResponse)
async def get_extraction_statistics(project_id: str):
    """获取任务提取统计信息"""
    try:
        logger.info(f"获取项目 {project_id} 的任务提取统计信息")
        
        statistics = auto_task_capture_service.get_extraction_statistics(project_id)
        
        return APIResponse.success_response(
            data=statistics,
            message="获取任务提取统计信息成功"
        )
    except Exception as e:
        logger.error(f"获取任务提取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务提取统计信息失败: {str(e)}")


@router.post("/auto-reduce/task-capture/test", response_model=APIResponse)
async def test_task_extraction(
    content: str = Body(..., description="测试文本内容")
):
    """测试任务提取功能"""
    try:
        logger.info("测试任务提取功能")
        
        # 使用测试项目ID和创建者
        test_project_id = "PRJ-2024-001"
        test_created_by = "测试用户"
        
        # 测试从会议纪要提取
        tasks = auto_task_capture_service.extract_tasks_from_meeting(
            content, test_project_id, test_created_by
        )
        
        return APIResponse.success_response(
            data={
                "test_content": content,
                "extracted_tasks": tasks,
                "task_count": len(tasks),
                "test_result": "success"
            },
            message=f"测试完成，成功提取 {len(tasks)} 个任务"
        )
    except Exception as e:
        logger.error(f"测试任务提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试任务提取失败: {str(e)}")

"""
智能进度汇总API
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
from datetime import datetime
from app.models.base import APIResponse
from app.services.intelligent_progress_summary import intelligent_progress_summary_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/auto-reduce/progress-summary/daily/{project_id}", response_model=APIResponse)
async def generate_daily_summary(
    project_id: str = Path(..., description="项目ID"),
    date: Optional[str] = Query(None, description="日期，格式：YYYY-MM-DD")
):
    """生成日报"""
    try:
        logger.info(f"生成项目 {project_id} 的日报")
        
        # 解析日期
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 生成日报
        daily_summary = intelligent_progress_summary_service.generate_daily_summary(
            project_id, target_date
        )
        
        return APIResponse.success_response(
            data={
                "summary_type": "daily",
                "project_id": daily_summary.project_id,
                "project_name": daily_summary.project_name,
                "date": daily_summary.start_date.isoformat(),
                "task_statistics": {
                    "total_tasks": daily_summary.total_tasks,
                    "completed_tasks": daily_summary.completed_tasks,
                    "in_progress_tasks": daily_summary.in_progress_tasks,
                    "pending_tasks": daily_summary.pending_tasks,
                    "overdue_tasks": daily_summary.overdue_tasks,
                    "completion_rate": daily_summary.completion_rate,
                    "progress_percentage": daily_summary.progress_percentage
                },
                "achievements": daily_summary.achievements,
                "challenges": daily_summary.challenges,
                "tomorrow_plan": daily_summary.tomorrow_plan,
                "today_tasks": daily_summary.today_tasks,
                "risks": daily_summary.risks,
                "issues": daily_summary.issues,
                "team_performance": daily_summary.team_performance
            },
            message=f"成功生成项目 {daily_summary.project_name} 的日报"
        )
    except ValueError as e:
        logger.warning(f"生成日报失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成日报失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成日报失败: {str(e)}")


@router.get("/auto-reduce/progress-summary/weekly/{project_id}", response_model=APIResponse)
async def generate_weekly_summary(
    project_id: str = Path(..., description="项目ID"),
    week_start: Optional[str] = Query(None, description="周开始日期，格式：YYYY-MM-DD")
):
    """生成周报"""
    try:
        logger.info(f"生成项目 {project_id} 的周报")
        
        # 解析周开始日期
        target_week_start = None
        if week_start:
            try:
                target_week_start = datetime.strptime(week_start, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 生成周报
        weekly_summary = intelligent_progress_summary_service.generate_weekly_summary(
            project_id, target_week_start
        )
        
        return APIResponse.success_response(
            data={
                "summary_type": "weekly",
                "project_id": weekly_summary.project_id,
                "project_name": weekly_summary.project_name,
                "week_start": weekly_summary.start_date.isoformat(),
                "week_end": weekly_summary.end_date.isoformat(),
                "task_statistics": {
                    "total_tasks": weekly_summary.total_tasks,
                    "completed_tasks": weekly_summary.completed_tasks,
                    "in_progress_tasks": weekly_summary.in_progress_tasks,
                    "pending_tasks": weekly_summary.pending_tasks,
                    "overdue_tasks": weekly_summary.overdue_tasks,
                    "completion_rate": weekly_summary.completion_rate,
                    "progress_percentage": weekly_summary.progress_percentage
                },
                "week_highlights": weekly_summary.week_highlights,
                "week_challenges": weekly_summary.week_challenges,
                "next_week_focus": weekly_summary.next_week_focus,
                "risks": weekly_summary.risks,
                "issues": weekly_summary.issues,
                "team_performance": weekly_summary.team_performance
            },
            message=f"成功生成项目 {weekly_summary.project_name} 的周报"
        )
    except ValueError as e:
        logger.warning(f"生成周报失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成周报失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成周报失败: {str(e)}")


@router.get("/auto-reduce/progress-summary/monthly/{project_id}", response_model=APIResponse)
async def generate_monthly_summary(
    project_id: str = Path(..., description="项目ID"),
    month_start: Optional[str] = Query(None, description="月开始日期，格式：YYYY-MM-DD")
):
    """生成月报"""
    try:
        logger.info(f"生成项目 {project_id} 的月报")
        
        # 解析月开始日期
        target_month_start = None
        if month_start:
            try:
                target_month_start = datetime.strptime(month_start, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 生成月报
        monthly_summary = intelligent_progress_summary_service.generate_monthly_summary(
            project_id, target_month_start
        )
        
        return APIResponse.success_response(
            data={
                "summary_type": "monthly",
                "project_id": monthly_summary.project_id,
                "project_name": monthly_summary.project_name,
                "month_start": monthly_summary.start_date.isoformat(),
                "month_end": monthly_summary.end_date.isoformat(),
                "task_statistics": {
                    "total_tasks": monthly_summary.total_tasks,
                    "completed_tasks": monthly_summary.completed_tasks,
                    "in_progress_tasks": monthly_summary.in_progress_tasks,
                    "pending_tasks": monthly_summary.pending_tasks,
                    "overdue_tasks": monthly_summary.overdue_tasks,
                    "completion_rate": monthly_summary.completion_rate,
                    "progress_percentage": monthly_summary.progress_percentage
                },
                "month_achievements": monthly_summary.month_achievements,
                "month_lessons": monthly_summary.month_lessons,
                "next_month_goals": monthly_summary.next_month_goals,
                "risks": monthly_summary.risks,
                "issues": monthly_summary.issues,
                "team_performance": monthly_summary.team_performance
            },
            message=f"成功生成项目 {monthly_summary.project_name} 的月报"
        )
    except ValueError as e:
        logger.warning(f"生成月报失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成月报失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成月报失败: {str(e)}")


@router.get("/auto-reduce/progress-summary/statistics/{project_id}", response_model=APIResponse)
async def get_summary_statistics(project_id: str = Path(..., description="项目ID")):
    """获取汇总统计信息"""
    try:
        logger.info(f"获取项目 {project_id} 的汇总统计信息")
        
        statistics = intelligent_progress_summary_service.get_summary_statistics(project_id)
        
        return APIResponse.success_response(
            data=statistics,
            message="获取汇总统计信息成功"
        )
    except ValueError as e:
        logger.warning(f"获取汇总统计信息失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取汇总统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取汇总统计信息失败: {str(e)}")


@router.post("/auto-reduce/progress-summary/custom", response_model=APIResponse)
async def generate_custom_summary(
    project_id: str,
    start_date: str,
    end_date: str,
    summary_type: str = "custom"
):
    """生成自定义时间段汇总"""
    try:
        logger.info(f"生成项目 {project_id} 的自定义汇总")
        
        # 解析日期
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
        
        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="开始日期必须早于结束日期")
        
        # 根据时间段长度选择汇总类型
        days_diff = (end_dt - start_dt).days
        
        if days_diff <= 1:
            # 日报
            summary = intelligent_progress_summary_service.generate_daily_summary(project_id, start_dt)
        elif days_diff <= 7:
            # 周报
            summary = intelligent_progress_summary_service.generate_weekly_summary(project_id, start_dt)
        else:
            # 月报
            summary = intelligent_progress_summary_service.generate_monthly_summary(project_id, start_dt)
        
        return APIResponse.success_response(
            data={
                "summary_type": summary_type,
                "project_id": summary.project_id,
                "project_name": summary.project_name,
                "start_date": start_date,
                "end_date": end_date,
                "task_statistics": {
                    "total_tasks": summary.total_tasks,
                    "completed_tasks": summary.completed_tasks,
                    "in_progress_tasks": summary.in_progress_tasks,
                    "pending_tasks": summary.pending_tasks,
                    "overdue_tasks": summary.overdue_tasks,
                    "completion_rate": summary.completion_rate,
                    "progress_percentage": summary.progress_percentage
                },
                "achievements": summary.achievements,
                "challenges": summary.challenges,
                "next_week_plan": summary.next_week_plan,
                "risks": summary.risks,
                "issues": summary.issues,
                "team_performance": summary.team_performance
            },
            message=f"成功生成项目 {summary.project_name} 的自定义汇总"
        )
    except ValueError as e:
        logger.warning(f"生成自定义汇总失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成自定义汇总失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成自定义汇总失败: {str(e)}")


@router.get("/auto-reduce/progress-summary/templates", response_model=APIResponse)
async def get_summary_templates():
    """获取汇总模板"""
    try:
        templates = {
            "daily_template": {
                "title": "项目日报 - {project_name}",
                "sections": [
                    "今日完成",
                    "今日进展",
                    "遇到问题",
                    "明日计划",
                    "风险提醒"
                ]
            },
            "weekly_template": {
                "title": "项目周报 - {project_name}",
                "sections": [
                    "本周亮点",
                    "本周进展",
                    "本周挑战",
                    "下周重点",
                    "风险状态"
                ]
            },
            "monthly_template": {
                "title": "项目月报 - {project_name}",
                "sections": [
                    "本月成就",
                    "项目进展",
                    "经验教训",
                    "下月目标",
                    "风险分析"
                ]
            }
        }
        
        return APIResponse.success_response(
            data=templates,
            message="获取汇总模板成功"
        )
    except Exception as e:
        logger.error(f"获取汇总模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取汇总模板失败: {str(e)}")

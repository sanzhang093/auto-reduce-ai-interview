"""
报表生成API
"""
from fastapi import APIRouter, HTTPException, Query, Path, Body
from fastapi.responses import FileResponse
from typing import List, Optional
from app.models.base import APIResponse
from app.models.enums import ReportType, ReportFormat
from app.services.report_generator import report_generator_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/auto-reduce/reports/generate", response_model=APIResponse)
async def generate_report(
    report_type: ReportType = Body(..., description="报表类型"),
    report_format: ReportFormat = Body(..., description="报表格式"),
    project_ids: List[str] = Body(..., description="项目ID列表"),
    export_file: bool = Body(default=False, description="是否导出文件")
):
    """生成报表"""
    try:
        logger.info(f"生成报表: {report_type.value} - {report_format.value}")
        
        # 生成报表
        report_data = report_generator_service.generate_report(
            report_type, report_format, project_ids
        )
        
        response_data = {
            "report_type": report_data.report_type.value,
            "report_format": report_data.report_format.value,
            "metadata": report_data.metadata,
            "generated_at": report_data.generated_at.isoformat()
        }
        
        # 如果请求导出文件
        if export_file:
            file_path = report_generator_service.export_report(report_data)
            response_data["file_path"] = file_path
            response_data["download_url"] = f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}"
        else:
            # 返回报表数据
            response_data["data"] = report_data.data
        
        return APIResponse.success_response(
            data=response_data,
            message=f"报表生成成功: {report_type.value}"
        )
    except Exception as e:
        logger.error(f"生成报表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成报表失败: {str(e)}")


@router.get("/auto-reduce/reports/project-summary/{project_id}", response_model=APIResponse)
async def generate_project_summary_report(
    project_id: str = Path(..., description="项目ID"),
    format: ReportFormat = Query(default=ReportFormat.JSON, description="报表格式"),
    export: bool = Query(default=False, description="是否导出文件")
):
    """生成项目汇总报表"""
    try:
        logger.info(f"生成项目 {project_id} 的汇总报表")
        
        report_data = report_generator_service.generate_report(
            ReportType.PROJECT_SUMMARY, format, [project_id]
        )
        
        response_data = {
            "report_type": "项目汇总报表",
            "report_format": format.value,
            "project_id": project_id,
            "metadata": report_data.metadata
        }
        
        if export:
            file_path = report_generator_service.export_report(report_data)
            response_data["file_path"] = file_path
            response_data["download_url"] = f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}"
        else:
            response_data["data"] = report_data.data
        
        return APIResponse.success_response(
            data=response_data,
            message=f"项目 {project_id} 汇总报表生成成功"
        )
    except Exception as e:
        logger.error(f"生成项目汇总报表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成项目汇总报表失败: {str(e)}")


@router.get("/auto-reduce/reports/task-progress/{project_id}", response_model=APIResponse)
async def generate_task_progress_report(
    project_id: str = Path(..., description="项目ID"),
    format: ReportFormat = Query(default=ReportFormat.JSON, description="报表格式"),
    export: bool = Query(default=False, description="是否导出文件")
):
    """生成任务进度报表"""
    try:
        logger.info(f"生成项目 {project_id} 的任务进度报表")
        
        report_data = report_generator_service.generate_report(
            ReportType.TASK_PROGRESS, format, [project_id]
        )
        
        response_data = {
            "report_type": "任务进度报表",
            "report_format": format.value,
            "project_id": project_id,
            "metadata": report_data.metadata
        }
        
        if export:
            file_path = report_generator_service.export_report(report_data)
            response_data["file_path"] = file_path
            response_data["download_url"] = f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}"
        else:
            response_data["data"] = report_data.data
        
        return APIResponse.success_response(
            data=response_data,
            message=f"项目 {project_id} 任务进度报表生成成功"
        )
    except Exception as e:
        logger.error(f"生成任务进度报表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成任务进度报表失败: {str(e)}")


@router.get("/auto-reduce/reports/risk-analysis/{project_id}", response_model=APIResponse)
async def generate_risk_analysis_report(
    project_id: str = Path(..., description="项目ID"),
    format: ReportFormat = Query(default=ReportFormat.JSON, description="报表格式"),
    export: bool = Query(default=False, description="是否导出文件")
):
    """生成风险分析报表"""
    try:
        logger.info(f"生成项目 {project_id} 的风险分析报表")
        
        report_data = report_generator_service.generate_report(
            ReportType.RISK_ANALYSIS, format, [project_id]
        )
        
        response_data = {
            "report_type": "风险分析报表",
            "report_format": format.value,
            "project_id": project_id,
            "metadata": report_data.metadata
        }
        
        if export:
            file_path = report_generator_service.export_report(report_data)
            response_data["file_path"] = file_path
            response_data["download_url"] = f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}"
        else:
            response_data["data"] = report_data.data
        
        return APIResponse.success_response(
            data=response_data,
            message=f"项目 {project_id} 风险分析报表生成成功"
        )
    except Exception as e:
        logger.error(f"生成风险分析报表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成风险分析报表失败: {str(e)}")


@router.get("/auto-reduce/reports/team-performance/{project_id}", response_model=APIResponse)
async def generate_team_performance_report(
    project_id: str = Path(..., description="项目ID"),
    format: ReportFormat = Query(default=ReportFormat.JSON, description="报表格式"),
    export: bool = Query(default=False, description="是否导出文件")
):
    """生成团队绩效报表"""
    try:
        logger.info(f"生成项目 {project_id} 的团队绩效报表")
        
        report_data = report_generator_service.generate_report(
            ReportType.TEAM_PERFORMANCE, format, [project_id]
        )
        
        response_data = {
            "report_type": "团队绩效报表",
            "report_format": format.value,
            "project_id": project_id,
            "metadata": report_data.metadata
        }
        
        if export:
            file_path = report_generator_service.export_report(report_data)
            response_data["file_path"] = file_path
            response_data["download_url"] = f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}"
        else:
            response_data["data"] = report_data.data
        
        return APIResponse.success_response(
            data=response_data,
            message=f"项目 {project_id} 团队绩效报表生成成功"
        )
    except Exception as e:
        logger.error(f"生成团队绩效报表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成团队绩效报表失败: {str(e)}")


@router.get("/auto-reduce/reports/executive-dashboard", response_model=APIResponse)
async def generate_executive_dashboard(
    project_ids: List[str] = Query(..., description="项目ID列表"),
    format: ReportFormat = Query(default=ReportFormat.JSON, description="报表格式"),
    export: bool = Query(default=False, description="是否导出文件")
):
    """生成高管仪表板"""
    try:
        logger.info(f"生成高管仪表板，项目数量: {len(project_ids)}")
        
        report_data = report_generator_service.generate_report(
            ReportType.EXECUTIVE_DASHBOARD, format, project_ids
        )
        
        response_data = {
            "report_type": "高管仪表板",
            "report_format": format.value,
            "project_ids": project_ids,
            "metadata": report_data.metadata
        }
        
        if export:
            file_path = report_generator_service.export_report(report_data)
            response_data["file_path"] = file_path
            response_data["download_url"] = f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}"
        else:
            response_data["data"] = report_data.data
        
        return APIResponse.success_response(
            data=response_data,
            message="高管仪表板生成成功"
        )
    except Exception as e:
        logger.error(f"生成高管仪表板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成高管仪表板失败: {str(e)}")


@router.get("/auto-reduce/reports/templates", response_model=APIResponse)
async def get_report_templates():
    """获取报表模板"""
    try:
        templates = report_generator_service.get_report_templates()
        
        return APIResponse.success_response(
            data=templates,
            message="获取报表模板成功"
        )
    except Exception as e:
        logger.error(f"获取报表模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报表模板失败: {str(e)}")


@router.get("/auto-reduce/reports/download/{filename}")
async def download_report(filename: str = Path(..., description="文件名")):
    """下载报表文件"""
    try:
        from pathlib import Path
        file_path = Path("./reports") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 根据文件扩展名确定媒体类型
        if filename.endswith('.json'):
            media_type = 'application/json'
        elif filename.endswith('.csv'):
            media_type = 'text/csv'
        elif filename.endswith('.html'):
            media_type = 'text/html'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载报表文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载报表文件失败: {str(e)}")


@router.get("/auto-reduce/reports/batch-generate", response_model=APIResponse)
async def batch_generate_reports(
    project_ids: List[str] = Query(..., description="项目ID列表"),
    report_types: List[ReportType] = Query(..., description="报表类型列表"),
    format: ReportFormat = Query(default=ReportFormat.JSON, description="报表格式")
):
    """批量生成报表"""
    try:
        logger.info(f"批量生成报表，项目数量: {len(project_ids)}, 报表类型: {len(report_types)}")
        
        results = []
        
        for report_type in report_types:
            try:
                report_data = report_generator_service.generate_report(
                    report_type, format, project_ids
                )
                
                # 导出文件
                file_path = report_generator_service.export_report(report_data)
                
                results.append({
                    "report_type": report_type.value,
                    "report_format": format.value,
                    "file_path": file_path,
                    "download_url": f"/api/v1/auto-reduce/reports/download/{Path(file_path).name}",
                    "status": "success"
                })
            except Exception as e:
                logger.error(f"生成报表 {report_type.value} 失败: {str(e)}")
                results.append({
                    "report_type": report_type.value,
                    "report_format": format.value,
                    "status": "failed",
                    "error": str(e)
                })
        
        success_count = len([r for r in results if r["status"] == "success"])
        
        return APIResponse.success_response(
            data={
                "results": results,
                "total_count": len(results),
                "success_count": success_count,
                "failed_count": len(results) - success_count
            },
            message=f"批量生成报表完成，成功 {success_count}/{len(results)} 个"
        )
    except Exception as e:
        logger.error(f"批量生成报表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量生成报表失败: {str(e)}")

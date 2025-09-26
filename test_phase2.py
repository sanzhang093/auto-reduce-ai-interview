"""
第二阶段功能测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.auto_task_capture import auto_task_capture_service
from app.services.intelligent_progress_summary import intelligent_progress_summary_service
from app.services.risk_monitoring import risk_monitoring_service
from app.services.report_generator import report_generator_service
from app.models.enums import DataSourceType, ReportType, ReportFormat
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_auto_task_capture():
    """测试自动任务捕捉功能"""
    print("=== 测试自动任务捕捉功能 ===")
    
    try:
        # 测试会议纪要任务提取
        meeting_content = """
        会议纪要：
        1. 张三负责完成用户认证模块的开发，本周内完成
        2. 李四需要实现数据可视化界面，优先级高
        3. 王五负责编写API文档，明天提交
        4. 赵六进行系统测试，确保质量
        """
        
        test_project_id = "PRJ-2024-001"
        test_created_by = "测试用户"
        
        tasks = auto_task_capture_service.extract_tasks_from_meeting(
            meeting_content, test_project_id, test_created_by
        )
        
        print(f"从会议纪要中提取到 {len(tasks)} 个任务")
        for task in tasks:
            print(f"  - {task.get('task_name', '')}")
        
        # 测试群聊消息任务提取
        chat_content = "@张三 请完成数据库设计，@李四 负责前端界面开发"
        
        chat_tasks = auto_task_capture_service.extract_tasks_from_chat(
            chat_content, test_project_id, test_created_by
        )
        
        print(f"从群聊消息中提取到 {len(chat_tasks)} 个任务")
        
        # 测试批量提取
        content_list = [
            {"type": "meeting", "content": meeting_content},
            {"type": "chat", "content": chat_content}
        ]
        
        batch_results = auto_task_capture_service.batch_extract_tasks(
            content_list, test_project_id, test_created_by
        )
        
        total_tasks = sum(len(tasks) for tasks in batch_results.values())
        print(f"批量提取完成，共创建 {total_tasks} 个任务")
        
        # 测试统计信息
        statistics = auto_task_capture_service.get_extraction_statistics(test_project_id)
        print(f"提取统计信息: {statistics}")
        
        print("✅ 自动任务捕捉功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 自动任务捕捉功能测试失败: {str(e)}")
        return False


def test_intelligent_progress_summary():
    """测试智能进度汇总功能"""
    print("\n=== 测试智能进度汇总功能 ===")
    
    try:
        test_project_id = "PRJ-2024-001"
        
        # 测试日报生成
        daily_summary = intelligent_progress_summary_service.generate_daily_summary(test_project_id)
        print(f"生成日报: {daily_summary.project_name}")
        print(f"  总任务数: {daily_summary.total_tasks}")
        print(f"  已完成: {daily_summary.completed_tasks}")
        print(f"  进度: {daily_summary.progress_percentage:.1f}%")
        print(f"  成就: {len(daily_summary.achievements)} 项")
        print(f"  挑战: {len(daily_summary.challenges)} 项")
        
        # 测试周报生成
        weekly_summary = intelligent_progress_summary_service.generate_weekly_summary(test_project_id)
        print(f"生成周报: {weekly_summary.project_name}")
        print(f"  周亮点: {len(weekly_summary.week_highlights)} 项")
        print(f"  周挑战: {len(weekly_summary.week_challenges)} 项")
        print(f"  下周重点: {len(weekly_summary.next_week_focus)} 项")
        
        # 测试月报生成
        monthly_summary = intelligent_progress_summary_service.generate_monthly_summary(test_project_id)
        print(f"生成月报: {monthly_summary.project_name}")
        print(f"  月成就: {len(monthly_summary.month_achievements)} 项")
        print(f"  经验教训: {len(monthly_summary.month_lessons)} 项")
        print(f"  下月目标: {len(monthly_summary.next_month_goals)} 项")
        
        # 测试统计信息
        statistics = intelligent_progress_summary_service.get_summary_statistics(test_project_id)
        print(f"汇总统计信息: {statistics}")
        
        print("✅ 智能进度汇总功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 智能进度汇总功能测试失败: {str(e)}")
        return False


def test_risk_monitoring():
    """测试风险监控功能"""
    print("\n=== 测试风险监控功能 ===")
    
    try:
        test_project_id = "PRJ-2024-001"
        
        # 测试风险扫描
        alerts = risk_monitoring_service.scan_project_risks(test_project_id)
        print(f"风险扫描完成，发现 {len(alerts)} 个风险预警")
        
        for alert in alerts[:3]:  # 显示前3个预警
            print(f"  - {alert.risk_title} ({alert.risk_level.value}) - 紧急度: {alert.urgency_score}")
        
        # 测试风险分析
        analysis = risk_monitoring_service.analyze_project_risks(test_project_id)
        print(f"风险分析完成:")
        print(f"  总风险数: {analysis.total_risks}")
        print(f"  高风险数: {analysis.high_risks}")
        print(f"  风险趋势: {analysis.risk_trend}")
        print(f"  主要风险类别: {analysis.top_risk_categories}")
        
        # 测试风险报告生成
        report = risk_monitoring_service.generate_risk_report(test_project_id)
        print(f"风险报告生成完成:")
        print(f"  报告标题: {report['project_info']['project_name']}")
        print(f"  总预警数: {report['risk_summary']['total_alerts']}")
        print(f"  严重预警: {report['risk_summary']['critical_alerts']}")
        print(f"  高风险预警: {report['risk_summary']['high_alerts']}")
        
        print("✅ 风险监控功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 风险监控功能测试失败: {str(e)}")
        return False


def test_report_generator():
    """测试报表生成功能"""
    print("\n=== 测试报表生成功能 ===")
    
    try:
        test_project_ids = ["PRJ-2024-001"]
        
        # 测试项目汇总报表
        project_summary_report = report_generator_service.generate_report(
            ReportType.PROJECT_SUMMARY, ReportFormat.JSON, test_project_ids
        )
        print(f"生成项目汇总报表: {project_summary_report.report_type.value}")
        print(f"  报表格式: {project_summary_report.report_format.value}")
        print(f"  数据项数: {project_summary_report.metadata['data_count']}")
        
        # 测试任务进度报表
        task_progress_report = report_generator_service.generate_report(
            ReportType.TASK_PROGRESS, ReportFormat.CSV, test_project_ids
        )
        print(f"生成任务进度报表: {task_progress_report.report_type.value}")
        print(f"  报表格式: {task_progress_report.report_format.value}")
        
        # 测试风险分析报表
        risk_analysis_report = report_generator_service.generate_report(
            ReportType.RISK_ANALYSIS, ReportFormat.HTML, test_project_ids
        )
        print(f"生成风险分析报表: {risk_analysis_report.report_type.value}")
        print(f"  报表格式: {risk_analysis_report.report_format.value}")
        
        # 测试团队绩效报表
        team_performance_report = report_generator_service.generate_report(
            ReportType.TEAM_PERFORMANCE, ReportFormat.JSON, test_project_ids
        )
        print(f"生成团队绩效报表: {team_performance_report.report_type.value}")
        print(f"  报表格式: {team_performance_report.report_format.value}")
        
        # 测试高管仪表板
        executive_dashboard = report_generator_service.generate_report(
            ReportType.EXECUTIVE_DASHBOARD, ReportFormat.JSON, test_project_ids
        )
        print(f"生成高管仪表板: {executive_dashboard.report_type.value}")
        print(f"  报表格式: {executive_dashboard.report_format.value}")
        
        # 测试报表导出
        file_path = report_generator_service.export_report(project_summary_report)
        print(f"报表导出成功: {file_path}")
        
        # 测试报表模板
        templates = report_generator_service.get_report_templates()
        print(f"获取报表模板: {len(templates)} 个")
        
        print("✅ 报表生成功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 报表生成功能测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始第二阶段功能测试...")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_auto_task_capture())
    test_results.append(test_intelligent_progress_summary())
    test_results.append(test_risk_monitoring())
    test_results.append(test_report_generator())
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 第二阶段功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
第一阶段功能测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database_service import database_service
from app.services.project_service import project_service
from app.services.task_service import task_service
from app.services.risk_service import risk_service
from app.services.issue_service import issue_service
from app.models.project import ProjectCreate, ProjectType, Priority, ProjectPhase
from app.models.task import TaskCreate, TaskType
from app.models.risk import RiskCreate, RiskCategory
from app.models.issue import IssueCreate, IssueCategory, Severity
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_database_service():
    """测试数据库服务"""
    print("=== 测试数据库服务 ===")
    
    try:
        # 获取数据库信息
        db_info = database_service.get_database_info()
        print(f"数据库信息: {db_info}")
        
        # 测试备份
        backup_file = database_service.backup_database()
        print(f"数据库备份完成: {backup_file}")
        
        print("✅ 数据库服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据库服务测试失败: {str(e)}")
        return False


def test_project_service():
    """测试项目服务"""
    print("\n=== 测试项目服务 ===")
    
    try:
        # 获取项目列表
        projects = project_service.get_projects()
        print(f"获取到 {len(projects)} 个项目")
        
        # 获取项目统计
        statistics = project_service.get_project_statistics()
        print(f"项目统计: 总计 {statistics.total_projects} 个，进行中 {statistics.active_projects} 个")
        
        # 创建新项目
        new_project_data = ProjectCreate(
            project_name="测试项目",
            project_code="TEST-001",
            description="这是一个测试项目",
            project_type=ProjectType.RESEARCH,
            priority=Priority.HIGH,
            project_manager="测试经理",
            project_phase=ProjectPhase.INITIATION
        )
        
        new_project = project_service.create_project(new_project_data)
        print(f"创建项目成功: {new_project.project_id}")
        
        # 获取项目详情
        project = project_service.get_project(new_project.project_id)
        if project:
            print(f"获取项目详情成功: {project.project_name}")
        
        # 获取项目摘要
        summary = project_service.get_project_summary(new_project.project_id)
        if summary:
            print(f"项目摘要: {summary.project_name} - 进度 {summary.progress_percentage}%")
        
        print("✅ 项目服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 项目服务测试失败: {str(e)}")
        return False


def test_task_service():
    """测试任务服务"""
    print("\n=== 测试任务服务 ===")
    
    try:
        # 获取任务列表
        tasks = task_service.get_tasks()
        print(f"获取到 {len(tasks)} 个任务")
        
        # 获取任务统计
        statistics = task_service.get_task_statistics()
        print(f"任务统计: 总计 {statistics.total_tasks} 个，已完成 {statistics.completed_tasks} 个")
        
        # 创建新任务
        new_task_data = TaskCreate(
            project_id="PRJ-2024-001",
            task_name="测试任务",
            description="这是一个测试任务",
            task_type=TaskType.DEVELOPMENT,
            priority=Priority.HIGH,
            assigned_to="测试用户",
            created_by="测试用户"
        )
        
        new_task = task_service.create_task(new_task_data)
        print(f"创建任务成功: {new_task.task_id}")
        
        # 获取任务详情
        task = task_service.get_task(new_task.task_id)
        if task:
            print(f"获取任务详情成功: {task.task_name}")
        
        print("✅ 任务服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 任务服务测试失败: {str(e)}")
        return False


def test_risk_service():
    """测试风险服务"""
    print("\n=== 测试风险服务 ===")
    
    try:
        # 获取风险列表
        risks = risk_service.get_risks()
        print(f"获取到 {len(risks)} 个风险")
        
        # 创建新风险
        new_risk_data = RiskCreate(
            project_id="PRJ-2024-001",
            risk_title="测试风险",
            description="这是一个测试风险",
            category=RiskCategory.TECHNICAL,
            probability="中",
            impact="高",
            owner="测试用户"
        )
        
        new_risk = risk_service.create_risk(new_risk_data)
        print(f"创建风险成功: {new_risk.risk_id} - 风险等级: {new_risk.risk_level}")
        
        # 获取风险详情
        risk = risk_service.get_risk(new_risk.risk_id)
        if risk:
            print(f"获取风险详情成功: {risk.risk_title}")
        
        print("✅ 风险服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 风险服务测试失败: {str(e)}")
        return False


def test_issue_service():
    """测试问题服务"""
    print("\n=== 测试问题服务 ===")
    
    try:
        # 获取问题列表
        issues = issue_service.get_issues()
        print(f"获取到 {len(issues)} 个问题")
        
        # 创建新问题
        new_issue_data = IssueCreate(
            project_id="PRJ-2024-001",
            issue_title="测试问题",
            description="这是一个测试问题",
            category=IssueCategory.TECHNICAL,
            severity=Severity.MEDIUM,
            assigned_to="测试用户",
            reported_by="测试用户"
        )
        
        new_issue = issue_service.create_issue(new_issue_data)
        print(f"创建问题成功: {new_issue.issue_id}")
        
        # 获取问题详情
        issue = issue_service.get_issue(new_issue.issue_id)
        if issue:
            print(f"获取问题详情成功: {issue.issue_title}")
        
        print("✅ 问题服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 问题服务测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始第一阶段功能测试...")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_database_service())
    test_results.append(test_project_service())
    test_results.append(test_task_service())
    test_results.append(test_risk_service())
    test_results.append(test_issue_service())
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 第一阶段功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

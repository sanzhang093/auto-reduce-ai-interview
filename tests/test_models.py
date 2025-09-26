"""
数据模型测试
"""
import pytest
from datetime import datetime, date
from app.models.project import Project
from app.models.task import Task
from app.models.risk import Risk
from app.models.issue import Issue
from app.models.enums import ProjectStatus, TaskStatus, RiskLevel, IssueSeverity


class TestProjectModel:
    """项目模型测试"""
    
    def test_project_creation(self):
        """测试项目创建"""
        project = Project(
            project_name="测试项目",
            description="测试项目描述",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            manager_id="manager_001",
            budget=100000.0
        )
        
        assert project.project_name == "测试项目"
        assert project.description == "测试项目描述"
        assert project.status == ProjectStatus.PLANNING
        assert project.budget == 100000.0
        assert project.progress == 0.0
        assert project.id is not None
        assert project.created_at is not None
    
    def test_project_validation(self):
        """测试项目验证"""
        with pytest.raises(ValueError):
            Project(
                project_name="",  # 空名称应该失败
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                manager_id="manager_001"
            )
    
    def test_project_serialization(self):
        """测试项目序列化"""
        project = Project(
            project_name="测试项目",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            manager_id="manager_001"
        )
        
        project_dict = project.model_dump()
        assert "id" in project_dict
        assert "created_at" in project_dict
        assert "project_name" in project_dict


class TestTaskModel:
    """任务模型测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            project_id="PRJ-001",
            name="测试任务",
            description="测试任务描述",
            assigned_to="user_001",
            due_date=date(2024, 6, 30),
            priority="高"
        )
        
        assert task.project_id == "PRJ-001"
        assert task.name == "测试任务"
        assert task.status == TaskStatus.NOT_STARTED
        assert task.priority == "高"
        assert task.progress == 0.0
        assert task.id is not None
    
    def test_task_validation(self):
        """测试任务验证"""
        with pytest.raises(ValueError):
            Task(
                project_id="PRJ-001",
                name="",  # 空名称应该失败
                due_date=date(2024, 6, 30)
            )
    
    def test_task_progress_validation(self):
        """测试任务进度验证"""
        task = Task(
            project_id="PRJ-001",
            name="测试任务",
            due_date=date(2024, 6, 30)
        )
        
        # 测试进度范围验证
        task.progress = 50.0
        assert task.progress == 50.0
        
        with pytest.raises(ValueError):
            task.progress = 150.0  # 超过100%应该失败


class TestRiskModel:
    """风险模型测试"""
    
    def test_risk_creation(self):
        """测试风险创建"""
        risk = Risk(
            project_id="PRJ-001",
            name="测试风险",
            description="测试风险描述",
            probability=0.7,
            impact="高"
        )
        
        assert risk.project_id == "PRJ-001"
        assert risk.name == "测试风险"
        assert risk.probability == 0.7
        assert risk.impact == "高"
        assert risk.status == "Open"
        assert risk.id is not None
    
    def test_risk_probability_validation(self):
        """测试风险概率验证"""
        with pytest.raises(ValueError):
            Risk(
                project_id="PRJ-001",
                name="测试风险",
                probability=1.5,  # 超过1.0应该失败
                impact="高"
            )


class TestIssueModel:
    """问题模型测试"""
    
    def test_issue_creation(self):
        """测试问题创建"""
        issue = Issue(
            project_id="PRJ-001",
            title="测试问题",
            description="测试问题描述",
            severity="高",
            reported_by="user_001"
        )
        
        assert issue.project_id == "PRJ-001"
        assert issue.title == "测试问题"
        assert issue.severity == "高"
        assert issue.status == "开放"
        assert issue.id is not None
    
    def test_issue_validation(self):
        """测试问题验证"""
        with pytest.raises(ValueError):
            Issue(
                project_id="PRJ-001",
                title="",  # 空标题应该失败
                severity="高",
                reported_by="user_001"
            )

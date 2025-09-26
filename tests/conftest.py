"""
测试配置和固件
"""
import pytest
import asyncio
import tempfile
import os
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from app.main import app
from app.services.database_service import database_service
from app.utils.database import JSONDatabase


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_db_path():
    """创建临时数据库文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    # 创建测试数据库
    test_db = JSONDatabase(temp_path)
    
    # 添加测试数据
    test_data = {
        "projects": [
            {
                "project_id": "PRJ-TEST-001",
                "project_name": "测试项目1",
                "description": "这是一个测试项目",
                "status": "进行中",
                "project_manager": "测试经理",
                "start_date": "2024-01-01",
                "planned_end_date": "2024-12-31",
                "budget": 100000.0,
                "progress_percentage": 50.0
            }
        ],
        "tasks": [
            {
                "task_id": "TASK-TEST-001",
                "project_id": "PRJ-TEST-001",
                "task_name": "测试任务1",
                "description": "这是一个测试任务",
                "status": "进行中",
                "assigned_to": "测试用户",
                "priority": "高",
                "progress_percentage": 75.0
            }
        ],
        "risks": [
            {
                "risk_id": "RISK-TEST-001",
                "project_id": "PRJ-TEST-001",
                "risk_title": "测试风险1",
                "description": "这是一个测试风险",
                "risk_level": "高",
                "status": "Open"
            }
        ],
        "issues": [
            {
                "issue_id": "ISSUE-TEST-001",
                "project_id": "PRJ-TEST-001",
                "issue_title": "测试问题1",
                "description": "这是一个测试问题",
                "severity": "高",
                "status": "开放"
            }
        ]
    }
    
    for collection_name, items in test_data.items():
        for item in items:
            test_db.add_item(collection_name, item)
    
    yield temp_path
    
    # 清理
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def test_client(temp_db_path):
    """创建测试客户端"""
    # 临时替换数据库路径
    original_path = database_service._db.db_path
    database_service._db.db_path = temp_db_path
    database_service._db._load_db()
    
    with TestClient(app) as client:
        yield client
    
    # 恢复原始数据库路径
    database_service._db.db_path = original_path
    database_service._db._load_db()


@pytest.fixture
def test_project_id():
    """测试项目ID"""
    return "PRJ-TEST-001"


@pytest.fixture
def test_user_id():
    """测试用户ID"""
    return "test_user_001"


@pytest.fixture
def test_task_data():
    """测试任务数据"""
    return {
        "project_id": "PRJ-TEST-001",
        "task_name": "测试任务",
        "description": "这是一个测试任务",
        "assigned_to": "test_user_001",
        "priority": "中",
        "task_type": "开发任务"
    }


@pytest.fixture
def test_risk_data():
    """测试风险数据"""
    return {
        "project_id": "PRJ-TEST-001",
        "risk_title": "测试风险",
        "description": "这是一个测试风险",
        "risk_level": "中",
        "category": "技术风险"
    }


@pytest.fixture
def test_issue_data():
    """测试问题数据"""
    return {
        "project_id": "PRJ-TEST-001",
        "issue_title": "测试问题",
        "description": "这是一个测试问题",
        "severity": "中",
        "reported_by": "test_user_001"
    }


@pytest.fixture
def mock_qwen_response():
    """模拟通义千问响应"""
    return {
        "content": "这是一个模拟的AI回复",
        "status": "success",
        "model": "qwen-turbo"
    }


@pytest.fixture
def mock_rag_documents():
    """模拟RAG文档"""
    return [
        {
            "doc_id": "doc_001",
            "title": "测试文档1",
            "content": "这是测试文档1的内容",
            "doc_type": "project",
            "relevance_score": 0.9
        },
        {
            "doc_id": "doc_002",
            "title": "测试文档2",
            "content": "这是测试文档2的内容",
            "doc_type": "task",
            "relevance_score": 0.8
        }
    ]

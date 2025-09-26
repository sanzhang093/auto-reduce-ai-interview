"""
服务层测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.project_service import project_service
from app.services.task_service import task_service
from app.services.risk_service import risk_service
from app.services.issue_service import issue_service
from app.services.auto_task_capture import auto_task_capture_service
from app.services.intelligent_progress_summary import intelligent_progress_summary_service
from app.services.risk_monitoring import risk_monitoring_service
from app.services.report_generator import report_generator_service
from app.services.qwen_agent import qwen_agent_service
from app.services.rag_system import rag_system
from app.services.ai_analysis import ai_analysis_service


class TestProjectService:
    """项目服务测试"""
    
    def test_create_project(self, test_client, test_project_id):
        """测试创建项目"""
        project_data = {
            "project_name": "新测试项目",
            "description": "新测试项目描述",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001",
            "budget": 150000.0
        }
        
        response = test_client.post("/api/v1/projects/", json=project_data)
        assert response.status_code == 201
        assert response.json()["project_name"] == "新测试项目"
    
    def test_get_project(self, test_client, test_project_id):
        """测试获取项目"""
        response = test_client.get(f"/api/v1/projects/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["project_id"] == test_project_id
    
    def test_get_all_projects(self, test_client):
        """测试获取所有项目"""
        response = test_client.get("/api/v1/projects/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_project(self, test_client, test_project_id):
        """测试更新项目"""
        update_data = {
            "project_name": "更新后的测试项目",
            "description": "更新后的描述",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001",
            "budget": 200000.0
        }
        
        response = test_client.put(f"/api/v1/projects/{test_project_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["project_name"] == "更新后的测试项目"
    
    def test_delete_project(self, test_client):
        """测试删除项目"""
        # 先创建一个项目
        project_data = {
            "project_name": "待删除项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001"
        }
        
        create_response = test_client.post("/api/v1/projects/", json=project_data)
        project_id = create_response.json()["project_id"]
        
        # 删除项目
        response = test_client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == 204
        
        # 验证项目已删除
        get_response = test_client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404


class TestTaskService:
    """任务服务测试"""
    
    def test_create_task(self, test_client, test_task_data):
        """测试创建任务"""
        response = test_client.post("/api/v1/tasks/", json=test_task_data)
        assert response.status_code == 201
        assert response.json()["task_name"] == test_task_data["task_name"]
    
    def test_get_task(self, test_client):
        """测试获取任务"""
        # 先创建一个任务
        task_data = {
            "project_id": "PRJ-TEST-001",
            "task_name": "测试任务",
            "due_date": "2024-06-30",
            "assigned_to": "test_user"
        }
        
        create_response = test_client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["task_id"]
        
        # 获取任务
        response = test_client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["task_id"] == task_id
    
    def test_get_all_tasks(self, test_client):
        """测试获取所有任务"""
        response = test_client.get("/api/v1/tasks/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAutoTaskCaptureService:
    """自动任务捕捉服务测试"""
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_meeting')
    def test_extract_tasks_from_meeting(self, mock_extract, test_client):
        """测试从会议纪要提取任务"""
        mock_extract.return_value = [
            {
                "task_id": "TASK-001",
                "task_name": "测试任务",
                "status": "待开始"
            }
        ]
        
        request_data = {
            "content": "会议纪要：张三负责完成用户认证模块",
            "project_id": "PRJ-TEST-001",
            "created_by": "test_user"
        }
        
        response = test_client.post("/api/v1/auto-reduce/task-capture/meeting", json=request_data)
        assert response.status_code == 200
        assert response.json()["data"]["count"] == 1
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_chat')
    def test_extract_tasks_from_chat(self, mock_extract, test_client):
        """测试从群聊消息提取任务"""
        mock_extract.return_value = [
            {
                "task_id": "TASK-002",
                "task_name": "聊天任务",
                "status": "待开始"
            }
        ]
        
        request_data = {
            "content": "@张三 请完成数据库设计",
            "project_id": "PRJ-TEST-001",
            "created_by": "test_user"
        }
        
        response = test_client.post("/api/v1/auto-reduce/task-capture/chat", json=request_data)
        assert response.status_code == 200
        assert response.json()["data"]["count"] == 1


class TestIntelligentProgressSummaryService:
    """智能进度汇总服务测试"""
    
    @patch('app.services.intelligent_progress_summary.intelligent_progress_summary_service.generate_daily_summary')
    def test_generate_daily_summary(self, mock_generate, test_client, test_project_id):
        """测试生成日报"""
        mock_summary = Mock()
        mock_summary.project_id = test_project_id
        mock_summary.project_name = "测试项目"
        mock_summary.total_tasks = 10
        mock_summary.completed_tasks = 5
        mock_summary.progress_percentage = 50.0
        mock_summary.achievements = ["完成用户认证模块"]
        mock_summary.challenges = ["数据库连接问题"]
        mock_summary.tomorrow_plan = ["完成API接口"]
        mock_summary.start_date = "2024-06-15"
        mock_summary.today_tasks = []
        mock_summary.risks = []
        mock_summary.issues = []
        mock_summary.team_performance = {}
        
        mock_generate.return_value = mock_summary
        
        response = test_client.get(f"/api/v1/auto-reduce/progress-summary/daily/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["project_id"] == test_project_id
    
    @patch('app.services.intelligent_progress_summary.intelligent_progress_summary_service.generate_weekly_summary')
    def test_generate_weekly_summary(self, mock_generate, test_client, test_project_id):
        """测试生成周报"""
        mock_summary = Mock()
        mock_summary.project_id = test_project_id
        mock_summary.project_name = "测试项目"
        mock_summary.total_tasks = 10
        mock_summary.completed_tasks = 7
        mock_summary.progress_percentage = 70.0
        mock_summary.week_highlights = ["完成核心功能开发"]
        mock_summary.week_challenges = ["性能优化需要更多时间"]
        mock_summary.next_week_focus = ["完成测试用例"]
        mock_summary.start_date = "2024-06-10"
        mock_summary.end_date = "2024-06-16"
        mock_summary.risks = []
        mock_summary.issues = []
        mock_summary.team_performance = {}
        
        mock_generate.return_value = mock_summary
        
        response = test_client.get(f"/api/v1/auto-reduce/progress-summary/weekly/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["project_id"] == test_project_id


class TestRiskMonitoringService:
    """风险监控服务测试"""
    
    @patch('app.services.risk_monitoring.risk_monitoring_service.scan_project_risks')
    def test_scan_project_risks(self, mock_scan, test_client, test_project_id):
        """测试扫描项目风险"""
        mock_alert = Mock()
        mock_alert.risk_id = "RISK-001"
        mock_alert.project_id = test_project_id
        mock_alert.risk_title = "测试风险"
        mock_alert.risk_level = "高"
        mock_alert.alert_type = "SCHEDULE_DELAY"
        mock_alert.alert_message = "项目进度延期风险"
        mock_alert.alert_time = "2024-06-15T10:00:00"
        mock_alert.mitigation_suggestion = "重新评估任务优先级"
        mock_alert.urgency_score = 8
        
        mock_scan.return_value = [mock_alert]
        
        response = test_client.get(f"/api/v1/auto-reduce/risk-monitoring/scan/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["total_alerts"] == 1
    
    @patch('app.services.risk_monitoring.risk_monitoring_service.analyze_project_risks')
    def test_analyze_project_risks(self, mock_analyze, test_client, test_project_id):
        """测试分析项目风险"""
        mock_analysis = Mock()
        mock_analysis.project_id = test_project_id
        mock_analysis.total_risks = 5
        mock_analysis.high_risks = 2
        mock_analysis.medium_risks = 2
        mock_analysis.low_risks = 1
        mock_analysis.risk_trend = "上升"
        mock_analysis.top_risk_categories = [("技术风险", 3), ("进度风险", 2)]
        mock_analysis.risk_impact_assessment = {"schedule_impact": "中等"}
        mock_analysis.mitigation_recommendations = ["加强风险监控"]
        
        mock_analyze.return_value = mock_analysis
        
        response = test_client.get(f"/api/v1/auto-reduce/risk-monitoring/analysis/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["total_risks"] == 5


class TestReportGeneratorService:
    """报表生成服务测试"""
    
    @patch('app.services.report_generator.report_generator_service.generate_report')
    def test_generate_project_summary_report(self, mock_generate, test_client, test_project_id):
        """测试生成项目汇总报表"""
        mock_report = Mock()
        mock_report.report_type = "PROJECT_SUMMARY"
        mock_report.report_format = "JSON"
        mock_report.metadata = {"total_projects": 1}
        mock_report.data = {
            "report_title": "项目汇总报表",
            "items": [{"project_id": test_project_id, "project_name": "测试项目"}]
        }
        mock_report.generated_at = "2024-06-15T10:00:00"
        
        mock_generate.return_value = mock_report
        
        response = test_client.get(f"/api/v1/auto-reduce/reports/project-summary/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["project_id"] == test_project_id


class TestQwenAgentService:
    """通义千问Agent服务测试"""
    
    @patch('app.services.qwen_agent.qwen_agent_service.chat')
    def test_chat_with_ai(self, mock_chat, test_client):
        """测试AI对话"""
        mock_response = {
            "session_id": "session_001",
            "response": "这是一个测试回复",
            "relevant_docs": [],
            "context": "测试上下文",
            "timestamp": "2024-06-15T10:00:00"
        }
        
        mock_chat.return_value = mock_response
        
        request_data = {
            "user_id": "test_user",
            "message": "请分析项目进度",
            "project_id": "PRJ-TEST-001"
        }
        
        response = test_client.post("/api/v1/auto-reduce/intelligent-chat/chat", json=request_data)
        assert response.status_code == 200
        assert response.json()["data"]["response"] == "这是一个测试回复"
    
    @patch('app.services.qwen_agent.qwen_agent_service.process_task_request')
    def test_process_task_request(self, mock_process, test_client):
        """测试处理任务请求"""
        mock_response = {
            "action": "task_created",
            "task": {"task_id": "TASK-001", "task_name": "测试任务"},
            "message": "任务创建成功"
        }
        
        mock_process.return_value = mock_response
        
        request_data = {
            "user_id": "test_user",
            "request": "创建一个新任务：实现用户登录",
            "project_id": "PRJ-TEST-001"
        }
        
        response = test_client.post("/api/v1/auto-reduce/intelligent-chat/task-request", json=request_data)
        assert response.status_code == 200
        assert response.json()["data"]["action"] == "task_created"


class TestRAGSystem:
    """RAG检索系统测试"""
    
    @patch('app.services.rag_system.rag_system.search_documents')
    def test_search_documents(self, mock_search, test_client):
        """测试搜索文档"""
        mock_results = [
            Mock(
                doc_id="doc_001",
                title="测试文档",
                content="测试内容",
                doc_type="project",
                relevance_score=0.9,
                metadata={}
            )
        ]
        
        mock_search.return_value = mock_results
        
        request_data = {
            "query": "项目进度分析",
            "project_id": "PRJ-TEST-001",
            "top_k": 5
        }
        
        response = test_client.post("/api/v1/auto-reduce/intelligent-chat/rag/search", json=request_data)
        assert response.status_code == 200
        assert response.json()["data"]["result_count"] == 1
    
    @patch('app.services.rag_system.rag_system.index_project_data')
    def test_index_project_data(self, mock_index, test_client, test_project_id):
        """测试索引项目数据"""
        mock_index.return_value = 10
        
        response = test_client.post(f"/api/v1/auto-reduce/intelligent-chat/rag/index/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["indexed_count"] == 10


class TestAIAnalysisService:
    """智能分析服务测试"""
    
    @patch('app.services.ai_analysis.ai_analysis_service.analyze_project_trends')
    def test_analyze_project_trends(self, mock_analyze, test_client, test_project_id):
        """测试分析项目趋势"""
        mock_trend = Mock()
        mock_trend.metric_name = "任务完成率"
        mock_trend.current_value = 75.0
        mock_trend.previous_value = 60.0
        mock_trend.trend_direction = "上升"
        mock_trend.trend_percentage = 15.0
        mock_trend.trend_description = "任务完成率上升15%"
        mock_trend.prediction = "预计继续上升"
        
        mock_analyze.return_value = [mock_trend]
        
        response = test_client.get(f"/api/v1/auto-reduce/ai-analysis/trends/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["trend_count"] == 1
    
    @patch('app.services.ai_analysis.ai_analysis_service.generate_project_insights')
    def test_generate_project_insights(self, mock_generate, test_client, test_project_id):
        """测试生成项目洞察"""
        mock_insight = Mock()
        mock_insight.insight_type = "performance"
        mock_insight.title = "项目性能分析"
        mock_insight.description = "项目完成率为75%"
        mock_insight.impact_level = "中"
        mock_insight.confidence = 0.8
        mock_insight.recommendations = ["优化任务分配"]
        mock_insight.data_support = {"completion_rate": 75.0}
        
        mock_generate.return_value = [mock_insight]
        
        response = test_client.get(f"/api/v1/auto-reduce/ai-analysis/insights/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["insight_count"] == 1
    
    @patch('app.services.ai_analysis.ai_analysis_service.generate_ai_recommendations')
    def test_generate_ai_recommendations(self, mock_generate, test_client, test_project_id):
        """测试生成AI建议"""
        mock_recommendation = Mock()
        mock_recommendation.recommendation_type = "task"
        mock_recommendation.title = "任务管理优化建议"
        mock_recommendation.description = "建议优化任务分配"
        mock_recommendation.priority = "高"
        mock_recommendation.action_items = ["重新评估任务优先级"]
        mock_recommendation.expected_impact = "提高任务完成效率"
        mock_recommendation.implementation_difficulty = "中等"
        
        mock_generate.return_value = [mock_recommendation]
        
        response = test_client.get(f"/api/v1/auto-reduce/ai-analysis/recommendations/{test_project_id}")
        assert response.status_code == 200
        assert response.json()["data"]["recommendation_count"] == 1

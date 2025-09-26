"""
集成测试
"""
import pytest
import asyncio
from unittest.mock import patch, Mock
from app.services.database_service import database_service
from app.services.auto_task_capture import auto_task_capture_service
from app.services.intelligent_progress_summary import intelligent_progress_summary_service
from app.services.risk_monitoring import risk_monitoring_service
from app.services.report_generator import report_generator_service
from app.services.qwen_agent import qwen_agent_service
from app.services.rag_system import rag_system
from app.services.ai_analysis import ai_analysis_service


class TestDataFlowIntegration:
    """数据流集成测试"""
    
    def test_project_to_task_flow(self, test_client, test_project_id):
        """测试项目到任务的数据流"""
        # 1. 创建项目
        project_data = {
            "project_name": "集成测试项目",
            "description": "用于集成测试的项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001",
            "budget": 200000.0
        }
        
        project_response = test_client.post("/api/v1/projects/", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]
        
        # 2. 为项目创建任务
        task_data = {
            "project_id": project_id,
            "task_name": "集成测试任务",
            "description": "用于集成测试的任务",
            "assigned_to": "user_001",
            "due_date": "2024-06-30",
            "priority": "高"
        }
        
        task_response = test_client.post("/api/v1/tasks/", json=task_data)
        assert task_response.status_code == 201
        task_id = task_response.json()["task_id"]
        
        # 3. 验证任务与项目关联
        get_task_response = test_client.get(f"/api/v1/tasks/{task_id}")
        assert get_task_response.status_code == 200
        assert get_task_response.json()["project_id"] == project_id
        
        # 4. 验证项目统计更新
        get_project_response = test_client.get(f"/api/v1/projects/{project_id}")
        assert get_project_response.status_code == 200
        # 这里可以验证项目统计信息是否更新
    
    def test_task_to_risk_flow(self, test_client, test_project_id):
        """测试任务到风险的数据流"""
        # 1. 创建任务
        task_data = {
            "project_id": test_project_id,
            "task_name": "高风险任务",
            "description": "可能遇到技术风险的任务",
            "assigned_to": "user_001",
            "due_date": "2024-06-30",
            "priority": "高"
        }
        
        task_response = test_client.post("/api/v1/tasks/", json=task_data)
        assert task_response.status_code == 201
        task_id = task_response.json()["task_id"]
        
        # 2. 创建相关风险
        risk_data = {
            "project_id": test_project_id,
            "risk_title": "技术实现风险",
            "description": "任务可能遇到技术实现困难",
            "risk_level": "高",
            "category": "技术风险",
            "probability": 0.7,
            "impact": "高"
        }
        
        risk_response = test_client.post("/api/v1/risks/", json=risk_data)
        assert risk_response.status_code == 201
        risk_id = risk_response.json()["risk_id"]
        
        # 3. 验证风险与项目关联
        get_risk_response = test_client.get(f"/api/v1/risks/{risk_id}")
        assert get_risk_response.status_code == 200
        assert get_risk_response.json()["project_id"] == test_project_id


class TestServiceIntegration:
    """服务集成测试"""
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_meeting')
    @patch('app.services.intelligent_progress_summary.intelligent_progress_summary_service.generate_daily_summary')
    def test_task_capture_to_progress_summary_flow(self, mock_summary, mock_extract, test_client, test_project_id):
        """测试任务捕捉到进度汇总的流程"""
        # 1. 模拟任务提取
        mock_extract.return_value = [
            {
                "task_id": "TASK-001",
                "task_name": "从会议提取的任务",
                "status": "待开始",
                "project_id": test_project_id
            }
        ]
        
        # 2. 执行任务提取
        extract_request = {
            "content": "会议纪要：张三负责完成用户认证模块",
            "project_id": test_project_id,
            "created_by": "test_user"
        }
        
        extract_response = test_client.post("/api/v1/auto-reduce/task-capture/meeting", json=extract_request)
        assert extract_response.status_code == 200
        
        # 3. 模拟进度汇总
        mock_summary_obj = Mock()
        mock_summary_obj.project_id = test_project_id
        mock_summary_obj.project_name = "测试项目"
        mock_summary_obj.total_tasks = 1
        mock_summary_obj.completed_tasks = 0
        mock_summary_obj.progress_percentage = 0.0
        mock_summary_obj.achievements = []
        mock_summary_obj.challenges = []
        mock_summary_obj.tomorrow_plan = []
        mock_summary_obj.start_date = "2024-06-15"
        mock_summary_obj.today_tasks = []
        mock_summary_obj.risks = []
        mock_summary_obj.issues = []
        mock_summary_obj.team_performance = {}
        
        mock_summary.return_value = mock_summary_obj
        
        # 4. 生成进度汇总
        summary_response = test_client.get(f"/api/v1/auto-reduce/progress-summary/daily/{test_project_id}")
        assert summary_response.status_code == 200
        assert summary_response.json()["data"]["project_id"] == test_project_id
    
    @patch('app.services.risk_monitoring.risk_monitoring_service.scan_project_risks')
    @patch('app.services.report_generator.report_generator_service.generate_report')
    def test_risk_monitoring_to_report_generation_flow(self, mock_report, mock_scan, test_client, test_project_id):
        """测试风险监控到报表生成的流程"""
        # 1. 模拟风险扫描
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
        
        # 2. 执行风险扫描
        scan_response = test_client.get(f"/api/v1/auto-reduce/risk-monitoring/scan/{test_project_id}")
        assert scan_response.status_code == 200
        assert scan_response.json()["data"]["total_alerts"] == 1
        
        # 3. 模拟报表生成
        mock_report_obj = Mock()
        mock_report_obj.report_type = "RISK_ANALYSIS"
        mock_report_obj.report_format = "JSON"
        mock_report_obj.metadata = {"total_risks": 1}
        mock_report_obj.data = {
            "report_title": "风险分析报表",
            "items": [{"risk_id": "RISK-001", "risk_title": "测试风险"}]
        }
        mock_report_obj.generated_at = "2024-06-15T10:00:00"
        
        mock_report.return_value = mock_report_obj
        
        # 4. 生成风险分析报表
        report_response = test_client.get(f"/api/v1/auto-reduce/reports/risk-analysis/{test_project_id}")
        assert report_response.status_code == 200
        assert report_response.json()["data"]["project_id"] == test_project_id


class TestAIIntegration:
    """AI集成测试"""
    
    @patch('app.services.rag_system.rag_system.index_project_data')
    @patch('app.services.rag_system.rag_system.search_documents')
    @patch('app.services.qwen_agent.qwen_agent_service.chat')
    def test_rag_to_ai_chat_integration(self, mock_chat, mock_search, mock_index, test_client, test_project_id):
        """测试RAG到AI对话的集成"""
        # 1. 模拟项目数据索引
        mock_index.return_value = 5
        
        # 2. 执行数据索引
        index_response = test_client.post(f"/api/v1/auto-reduce/intelligent-chat/rag/index/{test_project_id}")
        assert index_response.status_code == 200
        assert index_response.json()["data"]["indexed_count"] == 5
        
        # 3. 模拟文档搜索
        mock_search_result = Mock()
        mock_search_result.doc_id = "doc_001"
        mock_search_result.title = "项目信息"
        mock_search_result.content = "项目进度良好"
        mock_search_result.doc_type = "project"
        mock_search_result.relevance_score = 0.9
        mock_search_result.metadata = {}
        
        mock_search.return_value = [mock_search_result]
        
        # 4. 执行文档搜索
        search_request = {
            "query": "项目进度分析",
            "project_id": test_project_id,
            "top_k": 5
        }
        
        search_response = test_client.post("/api/v1/auto-reduce/intelligent-chat/rag/search", json=search_request)
        assert search_response.status_code == 200
        assert search_response.json()["data"]["result_count"] == 1
        
        # 5. 模拟AI对话
        mock_chat_response = {
            "session_id": "session_001",
            "response": "根据项目数据分析，项目进度良好，建议继续关注风险控制。",
            "relevant_docs": [{"doc_id": "doc_001", "title": "项目信息"}],
            "context": "项目上下文",
            "timestamp": "2024-06-15T10:00:00"
        }
        
        mock_chat.return_value = mock_chat_response
        
        # 6. 执行AI对话
        chat_request = {
            "user_id": "test_user",
            "message": "请分析项目进度",
            "project_id": test_project_id
        }
        
        chat_response = test_client.post("/api/v1/auto-reduce/intelligent-chat/chat", json=chat_request)
        assert chat_response.status_code == 200
        assert "项目进度良好" in chat_response.json()["data"]["response"]
    
    @patch('app.services.ai_analysis.ai_analysis_service.analyze_project_trends')
    @patch('app.services.ai_analysis.ai_analysis_service.generate_project_insights')
    @patch('app.services.ai_analysis.ai_analysis_service.generate_ai_recommendations')
    def test_ai_analysis_integration(self, mock_recommendations, mock_insights, mock_trends, test_client, test_project_id):
        """测试AI分析集成"""
        # 1. 模拟趋势分析
        mock_trend = Mock()
        mock_trend.metric_name = "任务完成率"
        mock_trend.current_value = 75.0
        mock_trend.previous_value = 60.0
        mock_trend.trend_direction = "上升"
        mock_trend.trend_percentage = 15.0
        mock_trend.trend_description = "任务完成率上升15%"
        mock_trend.prediction = "预计继续上升"
        
        mock_trends.return_value = [mock_trend]
        
        # 2. 执行趋势分析
        trends_response = test_client.get(f"/api/v1/auto-reduce/ai-analysis/trends/{test_project_id}")
        assert trends_response.status_code == 200
        assert trends_response.json()["data"]["trend_count"] == 1
        
        # 3. 模拟项目洞察
        mock_insight = Mock()
        mock_insight.insight_type = "performance"
        mock_insight.title = "项目性能分析"
        mock_insight.description = "项目完成率为75%"
        mock_insight.impact_level = "中"
        mock_insight.confidence = 0.8
        mock_insight.recommendations = ["优化任务分配"]
        mock_insight.data_support = {"completion_rate": 75.0}
        
        mock_insights.return_value = [mock_insight]
        
        # 4. 执行项目洞察
        insights_response = test_client.get(f"/api/v1/auto-reduce/ai-analysis/insights/{test_project_id}")
        assert insights_response.status_code == 200
        assert insights_response.json()["data"]["insight_count"] == 1
        
        # 5. 模拟AI建议
        mock_recommendation = Mock()
        mock_recommendation.recommendation_type = "task"
        mock_recommendation.title = "任务管理优化建议"
        mock_recommendation.description = "建议优化任务分配"
        mock_recommendation.priority = "高"
        mock_recommendation.action_items = ["重新评估任务优先级"]
        mock_recommendation.expected_impact = "提高任务完成效率"
        mock_recommendation.implementation_difficulty = "中等"
        
        mock_recommendations.return_value = [mock_recommendation]
        
        # 6. 执行AI建议生成
        recommendations_response = test_client.get(f"/api/v1/auto-reduce/ai-analysis/recommendations/{test_project_id}")
        assert recommendations_response.status_code == 200
        assert recommendations_response.json()["data"]["recommendation_count"] == 1


class TestEndToEndIntegration:
    """端到端集成测试"""
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_meeting')
    @patch('app.services.intelligent_progress_summary.intelligent_progress_summary_service.generate_daily_summary')
    @patch('app.services.risk_monitoring.risk_monitoring_service.scan_project_risks')
    @patch('app.services.report_generator.report_generator_service.generate_report')
    def test_complete_project_management_flow(self, mock_report, mock_scan, mock_summary, mock_extract, test_client):
        """测试完整的项目管理流程"""
        # 1. 创建项目
        project_data = {
            "project_name": "端到端测试项目",
            "description": "用于端到端测试的项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001",
            "budget": 300000.0
        }
        
        project_response = test_client.post("/api/v1/projects/", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]
        
        # 2. 从会议纪要提取任务
        mock_extract.return_value = [
            {
                "task_id": "TASK-001",
                "task_name": "端到端测试任务",
                "status": "待开始",
                "project_id": project_id
            }
        ]
        
        extract_request = {
            "content": "会议纪要：完成端到端测试任务",
            "project_id": project_id,
            "created_by": "test_user"
        }
        
        extract_response = test_client.post("/api/v1/auto-reduce/task-capture/meeting", json=extract_request)
        assert extract_response.status_code == 200
        
        # 3. 生成进度汇总
        mock_summary_obj = Mock()
        mock_summary_obj.project_id = project_id
        mock_summary_obj.project_name = "端到端测试项目"
        mock_summary_obj.total_tasks = 1
        mock_summary_obj.completed_tasks = 0
        mock_summary_obj.progress_percentage = 0.0
        mock_summary_obj.achievements = []
        mock_summary_obj.challenges = []
        mock_summary_obj.tomorrow_plan = []
        mock_summary_obj.start_date = "2024-06-15"
        mock_summary_obj.today_tasks = []
        mock_summary_obj.risks = []
        mock_summary_obj.issues = []
        mock_summary_obj.team_performance = {}
        
        mock_summary.return_value = mock_summary_obj
        
        summary_response = test_client.get(f"/api/v1/auto-reduce/progress-summary/daily/{project_id}")
        assert summary_response.status_code == 200
        
        # 4. 扫描项目风险
        mock_alert = Mock()
        mock_alert.risk_id = "RISK-001"
        mock_alert.project_id = project_id
        mock_alert.risk_title = "端到端测试风险"
        mock_alert.risk_level = "中"
        mock_alert.alert_type = "TECHNICAL_RISK"
        mock_alert.alert_message = "技术实现风险"
        mock_alert.alert_time = "2024-06-15T10:00:00"
        mock_alert.mitigation_suggestion = "加强技术评审"
        mock_alert.urgency_score = 6
        
        mock_scan.return_value = [mock_alert]
        
        scan_response = test_client.get(f"/api/v1/auto-reduce/risk-monitoring/scan/{project_id}")
        assert scan_response.status_code == 200
        
        # 5. 生成综合报表
        mock_report_obj = Mock()
        mock_report_obj.report_type = "PROJECT_SUMMARY"
        mock_report_obj.report_format = "JSON"
        mock_report_obj.metadata = {"total_projects": 1}
        mock_report_obj.data = {
            "report_title": "项目汇总报表",
            "items": [{"project_id": project_id, "project_name": "端到端测试项目"}]
        }
        mock_report_obj.generated_at = "2024-06-15T10:00:00"
        
        mock_report.return_value = mock_report_obj
        
        report_response = test_client.get(f"/api/v1/auto-reduce/reports/project-summary/{project_id}")
        assert report_response.status_code == 200
        
        # 6. 验证整个流程的完整性
        # 项目应该存在
        get_project_response = test_client.get(f"/api/v1/projects/{project_id}")
        assert get_project_response.status_code == 200
        
        # 任务应该被创建
        get_tasks_response = test_client.get("/api/v1/tasks/")
        assert get_tasks_response.status_code == 200
        # 这里可以验证任务是否被正确创建
        
        print(f"✅ 端到端测试完成，项目ID: {project_id}")


class TestErrorHandlingIntegration:
    """错误处理集成测试"""
    
    def test_database_error_handling(self, test_client):
        """测试数据库错误处理"""
        # 测试获取不存在的项目
        response = test_client.get("/api/v1/projects/non-existent-project")
        assert response.status_code == 404
    
    def test_validation_error_handling(self, test_client):
        """测试验证错误处理"""
        # 测试创建无效项目
        invalid_project_data = {
            "project_name": "",  # 空名称
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001"
        }
        
        response = test_client.post("/api/v1/projects/", json=invalid_project_data)
        assert response.status_code == 422  # 验证错误
    
    def test_service_error_handling(self, test_client, test_project_id):
        """测试服务错误处理"""
        # 测试不存在的项目ID
        response = test_client.get(f"/api/v1/auto-reduce/progress-summary/daily/non-existent-project")
        assert response.status_code == 500  # 服务错误

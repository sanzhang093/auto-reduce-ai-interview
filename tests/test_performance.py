"""
性能测试
"""
import pytest
import time
import asyncio
import concurrent.futures
from unittest.mock import patch, Mock
from app.services.database_service import database_service
from app.services.auto_task_capture import auto_task_capture_service
from app.services.intelligent_progress_summary import intelligent_progress_summary_service
from app.services.risk_monitoring import risk_monitoring_service
from app.services.report_generator import report_generator_service
from app.services.qwen_agent import qwen_agent_service
from app.services.rag_system import rag_system
from app.services.ai_analysis import ai_analysis_service


class TestResponseTime:
    """响应时间测试"""
    
    def test_project_crud_response_time(self, test_client):
        """测试项目CRUD操作的响应时间"""
        # 创建项目
        project_data = {
            "project_name": "性能测试项目",
            "description": "用于性能测试的项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001",
            "budget": 100000.0
        }
        
        start_time = time.time()
        response = test_client.post("/api/v1/projects/", json=project_data)
        create_time = time.time() - start_time
        
        assert response.status_code == 201
        assert create_time < 1.0  # 创建操作应在1秒内完成
        
        project_id = response.json()["project_id"]
        
        # 获取项目
        start_time = time.time()
        response = test_client.get(f"/api/v1/projects/{project_id}")
        get_time = time.time() - start_time
        
        assert response.status_code == 200
        assert get_time < 0.5  # 获取操作应在0.5秒内完成
        
        # 更新项目
        update_data = project_data.copy()
        update_data["project_name"] = "更新后的性能测试项目"
        
        start_time = time.time()
        response = test_client.put(f"/api/v1/projects/{project_id}", json=update_data)
        update_time = time.time() - start_time
        
        assert response.status_code == 200
        assert update_time < 1.0  # 更新操作应在1秒内完成
        
        # 删除项目
        start_time = time.time()
        response = test_client.delete(f"/api/v1/projects/{project_id}")
        delete_time = time.time() - start_time
        
        assert response.status_code == 204
        assert delete_time < 0.5  # 删除操作应在0.5秒内完成
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_meeting')
    def test_task_extraction_response_time(self, mock_extract, test_client, test_project_id):
        """测试任务提取的响应时间"""
        mock_extract.return_value = [
            {
                "task_id": "TASK-001",
                "task_name": "性能测试任务",
                "status": "待开始"
            }
        ]
        
        request_data = {
            "content": "会议纪要：张三负责完成性能测试任务",
            "project_id": test_project_id,
            "created_by": "test_user"
        }
        
        start_time = time.time()
        response = test_client.post("/api/v1/auto-reduce/task-capture/meeting", json=request_data)
        extraction_time = time.time() - start_time
        
        assert response.status_code == 200
        assert extraction_time < 2.0  # 任务提取应在2秒内完成
    
    @patch('app.services.intelligent_progress_summary.intelligent_progress_summary_service.generate_daily_summary')
    def test_progress_summary_response_time(self, mock_generate, test_client, test_project_id):
        """测试进度汇总的响应时间"""
        mock_summary = Mock()
        mock_summary.project_id = test_project_id
        mock_summary.project_name = "性能测试项目"
        mock_summary.total_tasks = 10
        mock_summary.completed_tasks = 5
        mock_summary.progress_percentage = 50.0
        mock_summary.achievements = ["完成核心功能"]
        mock_summary.challenges = ["性能优化"]
        mock_summary.tomorrow_plan = ["完成测试"]
        mock_summary.start_date = "2024-06-15"
        mock_summary.today_tasks = []
        mock_summary.risks = []
        mock_summary.issues = []
        mock_summary.team_performance = {}
        
        mock_generate.return_value = mock_summary
        
        start_time = time.time()
        response = test_client.get(f"/api/v1/auto-reduce/progress-summary/daily/{test_project_id}")
        summary_time = time.time() - start_time
        
        assert response.status_code == 200
        assert summary_time < 1.0  # 进度汇总应在1秒内完成
    
    @patch('app.services.risk_monitoring.risk_monitoring_service.scan_project_risks')
    def test_risk_scanning_response_time(self, mock_scan, test_client, test_project_id):
        """测试风险扫描的响应时间"""
        mock_alert = Mock()
        mock_alert.risk_id = "RISK-001"
        mock_alert.project_id = test_project_id
        mock_alert.risk_title = "性能测试风险"
        mock_alert.risk_level = "中"
        mock_alert.alert_type = "PERFORMANCE_RISK"
        mock_alert.alert_message = "性能测试风险"
        mock_alert.alert_time = "2024-06-15T10:00:00"
        mock_alert.mitigation_suggestion = "优化性能"
        mock_alert.urgency_score = 6
        
        mock_scan.return_value = [mock_alert]
        
        start_time = time.time()
        response = test_client.get(f"/api/v1/auto-reduce/risk-monitoring/scan/{test_project_id}")
        scan_time = time.time() - start_time
        
        assert response.status_code == 200
        assert scan_time < 1.0  # 风险扫描应在1秒内完成
    
    @patch('app.services.report_generator.report_generator_service.generate_report')
    def test_report_generation_response_time(self, mock_generate, test_client, test_project_id):
        """测试报表生成的响应时间"""
        mock_report = Mock()
        mock_report.report_type = "PROJECT_SUMMARY"
        mock_report.report_format = "JSON"
        mock_report.metadata = {"total_projects": 1}
        mock_report.data = {
            "report_title": "项目汇总报表",
            "items": [{"project_id": test_project_id, "project_name": "性能测试项目"}]
        }
        mock_report.generated_at = "2024-06-15T10:00:00"
        
        mock_generate.return_value = mock_report
        
        start_time = time.time()
        response = test_client.get(f"/api/v1/auto-reduce/reports/project-summary/{test_project_id}")
        report_time = time.time() - start_time
        
        assert response.status_code == 200
        assert report_time < 2.0  # 报表生成应在2秒内完成


class TestConcurrency:
    """并发测试"""
    
    def test_concurrent_project_creation(self, test_client):
        """测试并发项目创建"""
        def create_project(project_id):
            project_data = {
                "project_name": f"并发测试项目{project_id}",
                "description": f"并发测试项目{project_id}描述",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "manager_id": f"manager_{project_id}",
                "budget": 100000.0
            }
            
            response = test_client.post("/api/v1/projects/", json=project_data)
            return response.status_code == 201
        
        # 并发创建10个项目
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_project, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有项目都创建成功
        assert all(results)
        assert len(results) == 10
    
    def test_concurrent_task_creation(self, test_client, test_project_id):
        """测试并发任务创建"""
        def create_task(task_id):
            task_data = {
                "project_id": test_project_id,
                "task_name": f"并发测试任务{task_id}",
                "description": f"并发测试任务{task_id}描述",
                "assigned_to": f"user_{task_id}",
                "due_date": "2024-06-30",
                "priority": "中"
            }
            
            response = test_client.post("/api/v1/tasks/", json=task_data)
            return response.status_code == 201
        
        # 并发创建20个任务
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_task, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有任务都创建成功
        assert all(results)
        assert len(results) == 20
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_meeting')
    def test_concurrent_task_extraction(self, mock_extract, test_client, test_project_id):
        """测试并发任务提取"""
        mock_extract.return_value = [
            {
                "task_id": f"TASK-{i}",
                "task_name": f"并发提取任务{i}",
                "status": "待开始"
            }
        ]
        
        def extract_tasks(extraction_id):
            request_data = {
                "content": f"会议纪要{extraction_id}：完成并发提取任务{extraction_id}",
                "project_id": test_project_id,
                "created_by": f"user_{extraction_id}"
            }
            
            response = test_client.post("/api/v1/auto-reduce/task-capture/meeting", json=request_data)
            return response.status_code == 200
        
        # 并发执行10次任务提取
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(extract_tasks, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有任务提取都成功
        assert all(results)
        assert len(results) == 10


class TestMemoryUsage:
    """内存使用测试"""
    
    def test_large_dataset_handling(self, test_client):
        """测试大数据集处理"""
        # 创建大量项目
        project_ids = []
        for i in range(100):
            project_data = {
                "project_name": f"大数据集测试项目{i}",
                "description": f"大数据集测试项目{i}描述" * 10,  # 增加数据量
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "manager_id": f"manager_{i}",
                "budget": 100000.0 + i
            }
            
            response = test_client.post("/api/v1/projects/", json=project_data)
            assert response.status_code == 201
            project_ids.append(response.json()["project_id"])
        
        # 验证所有项目都能正常获取
        for project_id in project_ids:
            response = test_client.get(f"/api/v1/projects/{project_id}")
            assert response.status_code == 200
        
        # 获取所有项目
        response = test_client.get("/api/v1/projects/")
        assert response.status_code == 200
        assert len(response.json()) >= 100
    
    def test_database_memory_efficiency(self, test_client):
        """测试数据库内存效率"""
        # 创建项目
        project_data = {
            "project_name": "内存效率测试项目",
            "description": "用于测试数据库内存效率的项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "manager_id": "manager_001",
            "budget": 100000.0
        }
        
        response = test_client.post("/api/v1/projects/", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["project_id"]
        
        # 创建大量任务
        task_ids = []
        for i in range(50):
            task_data = {
                "project_id": project_id,
                "task_name": f"内存效率测试任务{i}",
                "description": f"内存效率测试任务{i}描述" * 5,
                "assigned_to": f"user_{i}",
                "due_date": "2024-06-30",
                "priority": "中"
            }
            
            response = test_client.post("/api/v1/tasks/", json=task_data)
            assert response.status_code == 201
            task_ids.append(response.json()["task_id"])
        
        # 验证所有任务都能正常获取
        for task_id in task_ids:
            response = test_client.get(f"/api/v1/tasks/{task_id}")
            assert response.status_code == 200
        
        # 获取项目下的所有任务
        response = test_client.get("/api/v1/tasks/")
        assert response.status_code == 200
        assert len(response.json()) >= 50


class TestScalability:
    """可扩展性测试"""
    
    def test_api_scalability(self, test_client):
        """测试API可扩展性"""
        # 测试大量API调用
        start_time = time.time()
        
        for i in range(50):
            # 创建项目
            project_data = {
                "project_name": f"可扩展性测试项目{i}",
                "description": f"可扩展性测试项目{i}描述",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "manager_id": f"manager_{i}",
                "budget": 100000.0
            }
            
            response = test_client.post("/api/v1/projects/", json=project_data)
            assert response.status_code == 201
            project_id = response.json()["project_id"]
            
            # 获取项目
            response = test_client.get(f"/api/v1/projects/{project_id}")
            assert response.status_code == 200
            
            # 创建任务
            task_data = {
                "project_id": project_id,
                "task_name": f"可扩展性测试任务{i}",
                "assigned_to": f"user_{i}",
                "due_date": "2024-06-30",
                "priority": "中"
            }
            
            response = test_client.post("/api/v1/tasks/", json=task_data)
            assert response.status_code == 201
        
        total_time = time.time() - start_time
        average_time = total_time / 50
        
        # 验证平均响应时间在可接受范围内
        assert average_time < 0.5  # 平均每个操作应在0.5秒内完成
        assert total_time < 30.0  # 总时间应在30秒内完成
    
    @patch('app.services.rag_system.rag_system.index_project_data')
    def test_rag_system_scalability(self, mock_index, test_client):
        """测试RAG系统可扩展性"""
        mock_index.return_value = 10
        
        # 测试大量项目数据索引
        start_time = time.time()
        
        for i in range(20):
            project_id = f"PRJ-SCALE-{i:03d}"
            response = test_client.post(f"/api/v1/auto-reduce/intelligent-chat/rag/index/{project_id}")
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        average_time = total_time / 20
        
        # 验证平均索引时间在可接受范围内
        assert average_time < 1.0  # 平均每个索引操作应在1秒内完成
        assert total_time < 25.0  # 总时间应在25秒内完成


class TestStressTest:
    """压力测试"""
    
    def test_high_load_project_operations(self, test_client):
        """测试高负载项目操作"""
        # 在高负载下执行项目操作
        def perform_operations(thread_id):
            results = []
            
            for i in range(10):
                # 创建项目
                project_data = {
                    "project_name": f"压力测试项目{thread_id}_{i}",
                    "description": f"压力测试项目{thread_id}_{i}描述",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "manager_id": f"manager_{thread_id}_{i}",
                    "budget": 100000.0
                }
                
                response = test_client.post("/api/v1/projects/", json=project_data)
                results.append(response.status_code == 201)
                
                if response.status_code == 201:
                    project_id = response.json()["project_id"]
                    
                    # 获取项目
                    response = test_client.get(f"/api/v1/projects/{project_id}")
                    results.append(response.status_code == 200)
            
            return results
        
        # 使用10个线程，每个线程执行10次操作
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_operations, i) for i in range(10)]
            all_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有操作都成功
        flat_results = [result for thread_results in all_results for result in thread_results]
        success_rate = sum(flat_results) / len(flat_results)
        
        assert success_rate >= 0.95  # 成功率应达到95%以上
    
    @patch('app.services.auto_task_capture.auto_task_capture_service.extract_tasks_from_meeting')
    def test_high_load_task_extraction(self, mock_extract, test_client, test_project_id):
        """测试高负载任务提取"""
        mock_extract.return_value = [
            {
                "task_id": "TASK-001",
                "task_name": "压力测试任务",
                "status": "待开始"
            }
        ]
        
        def perform_extractions(thread_id):
            results = []
            
            for i in range(5):
                request_data = {
                    "content": f"会议纪要{thread_id}_{i}：完成压力测试任务{thread_id}_{i}",
                    "project_id": test_project_id,
                    "created_by": f"user_{thread_id}_{i}"
                }
                
                response = test_client.post("/api/v1/auto-reduce/task-capture/meeting", json=request_data)
                results.append(response.status_code == 200)
            
            return results
        
        # 使用20个线程，每个线程执行5次任务提取
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(perform_extractions, i) for i in range(20)]
            all_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有任务提取都成功
        flat_results = [result for thread_results in all_results for result in thread_results]
        success_rate = sum(flat_results) / len(flat_results)
        
        assert success_rate >= 0.95  # 成功率应达到95%以上

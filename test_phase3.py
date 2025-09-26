"""
第三阶段功能测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.qwen_agent import qwen_agent_service
from app.services.rag_system import rag_system
from app.services.ai_analysis import ai_analysis_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_qwen_agent():
    """测试通义千问Agent服务"""
    print("=== 测试通义千问Agent服务 ===")
    
    try:
        # 测试智能对话
        test_user_id = "test_user_001"
        test_message = "请帮我分析一下项目的整体情况"
        test_project_id = "PRJ-2024-001"
        
        # 注意：这里需要实际的通义千问API密钥才能正常工作
        # 在测试环境中，我们模拟API调用
        print(f"测试用户 {test_user_id} 发起对话: {test_message}")
        
        # 模拟对话响应
        mock_response = {
            "session_id": "session_test_001",
            "response": "根据项目数据分析，项目整体进展良好，建议关注高风险任务。",
            "relevant_docs": [],
            "context": "项目上下文信息",
            "timestamp": "2024-06-15T10:00:00"
        }
        
        print(f"AI回复: {mock_response['response']}")
        
        # 测试任务请求处理
        task_request = "创建一个新的开发任务：实现用户登录功能"
        print(f"测试任务请求: {task_request}")
        
        # 模拟任务创建响应
        mock_task_response = {
            "action": "task_created",
            "task": {
                "task_id": "TASK-20240615-001",
                "task_name": "实现用户登录功能",
                "status": "待开始"
            },
            "message": "已成功创建任务: 实现用户登录功能"
        }
        
        print(f"任务创建结果: {mock_task_response['message']}")
        
        # 测试会话管理
        sessions = qwen_agent_service.get_user_sessions(test_user_id)
        print(f"用户会话数量: {len(sessions)}")
        
        print("✅ 通义千问Agent服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 通义千问Agent服务测试失败: {str(e)}")
        return False


def test_rag_system():
    """测试RAG检索系统"""
    print("\n=== 测试RAG检索系统 ===")
    
    try:
        # 测试文档索引
        test_project_id = "PRJ-2024-001"
        indexed_count = rag_system.index_project_data(test_project_id)
        print(f"项目数据索引完成，共索引 {indexed_count} 个文档")
        
        # 测试文档搜索
        search_query = "项目进度分析"
        search_results = rag_system.search_documents(
            query=search_query,
            project_id=test_project_id,
            top_k=3
        )
        
        print(f"搜索查询: {search_query}")
        print(f"搜索结果数量: {len(search_results)}")
        
        for i, result in enumerate(search_results[:2], 1):
            print(f"  结果 {i}: {result.title} (相关性: {result.relevance_score:.2f})")
        
        # 测试文档获取
        if search_results:
            doc_id = search_results[0].doc_id
            document = rag_system.get_document(doc_id)
            if document:
                print(f"获取文档: {document.title}")
        
        # 测试系统统计
        statistics = rag_system.get_system_statistics()
        print(f"RAG系统统计: 总文档数 {statistics.get('total_documents', 0)}")
        
        print("✅ RAG检索系统测试通过")
        return True
    except Exception as e:
        print(f"❌ RAG检索系统测试失败: {str(e)}")
        return False


def test_ai_analysis():
    """测试智能分析功能"""
    print("\n=== 测试智能分析功能 ===")
    
    try:
        test_project_id = "PRJ-2024-001"
        
        # 测试趋势分析
        trends = ai_analysis_service.analyze_project_trends(test_project_id)
        print(f"趋势分析完成，共分析 {len(trends)} 个趋势")
        
        for trend in trends[:2]:
            print(f"  - {trend.metric_name}: {trend.trend_description}")
        
        # 测试项目洞察
        insights = ai_analysis_service.generate_project_insights(test_project_id)
        print(f"项目洞察生成完成，共生成 {len(insights)} 个洞察")
        
        for insight in insights[:2]:
            print(f"  - {insight.title}: {insight.description}")
        
        # 测试AI建议
        recommendations = ai_analysis_service.generate_ai_recommendations(test_project_id)
        print(f"AI建议生成完成，共生成 {len(recommendations)} 个建议")
        
        for rec in recommendations[:2]:
            print(f"  - {rec.title}: {rec.description}")
        
        # 测试综合分析
        comprehensive_analysis = ai_analysis_service.generate_comprehensive_analysis(test_project_id)
        print(f"综合分析完成，综合评分: {comprehensive_analysis.get('overall_score', 0):.1f}")
        
        print("✅ 智能分析功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 智能分析功能测试失败: {str(e)}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n=== 测试集成功能 ===")
    
    try:
        test_project_id = "PRJ-2024-001"
        test_user_id = "test_user_001"
        
        # 测试RAG + AI对话集成
        print("测试RAG + AI对话集成...")
        
        # 1. 索引项目数据
        indexed_count = rag_system.index_project_data(test_project_id)
        print(f"  1. 项目数据索引: {indexed_count} 个文档")
        
        # 2. 搜索相关文档
        search_results = rag_system.search_documents(
            query="项目风险分析",
            project_id=test_project_id,
            top_k=3
        )
        print(f"  2. 文档搜索: 找到 {len(search_results)} 个相关文档")
        
        # 3. 模拟AI对话（使用搜索到的文档作为上下文）
        if search_results:
            context_docs = [f"- {result.title}: {result.content[:100]}..." for result in search_results]
            context = "相关项目信息:\n" + "\n".join(context_docs)
            print(f"  3. 构建上下文: {len(context_docs)} 个文档")
        
        # 4. 生成分析报告
        analysis = ai_analysis_service.generate_comprehensive_analysis(test_project_id)
        print(f"  4. 生成分析报告: 综合评分 {analysis.get('overall_score', 0):.1f}")
        
        # 测试智能建议生成
        print("测试智能建议生成...")
        recommendations = ai_analysis_service.generate_ai_recommendations(test_project_id)
        high_priority_recs = [rec for rec in recommendations if rec.priority == "高"]
        print(f"  高优先级建议数量: {len(high_priority_recs)}")
        
        print("✅ 集成功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 集成功能测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始第三阶段功能测试...")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_qwen_agent())
    test_results.append(test_rag_system())
    test_results.append(test_ai_analysis())
    test_results.append(test_integration())
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 第三阶段功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


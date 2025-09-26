"""
自动减负AI应用架构 - 功能演示脚本
"""
import requests
import json
import time

def test_api_endpoint(url, description):
    """测试API端点"""
    try:
        print(f"\n🔍 测试: {description}")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态: 成功 (HTTP {response.status_code})")
            print(f"📊 响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 状态: 失败 (HTTP {response.status_code})")
            print(f"📊 响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接错误: {str(e)}")
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")

def main():
    """主函数"""
    base_url = "http://localhost:8000"
    
    print("🚀 自动减负AI应用架构 - 功能演示")
    print("=" * 60)
    
    # 基础功能测试
    test_api_endpoint(f"{base_url}/", "根路径 - 应用信息")
    test_api_endpoint(f"{base_url}/health", "健康检查")
    
    # 项目管理功能
    test_api_endpoint(f"{base_url}/api/v1/projects", "获取项目列表")
    test_api_endpoint(f"{base_url}/api/v1/tasks", "获取任务列表")
    
    # 自动减负功能
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/task-capture/meeting", "从会议纪要提取任务")
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/progress-summary/daily/PRJ-001", "生成日报")
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/risk-monitoring/scan/PRJ-001", "扫描项目风险")
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/reports/project-summary/PRJ-001", "生成项目汇总报表")
    
    # AI功能
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/intelligent-chat/chat", "AI智能对话")
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/ai-analysis/trends/PRJ-001", "AI趋势分析")
    
    # 系统功能
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/cache/stats", "缓存统计")
    test_api_endpoint(f"{base_url}/api/v1/auto-reduce/monitoring/health", "系统健康状态")
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("📚 更多功能请访问: http://localhost:8000/docs")
    print("🔧 管理界面: http://localhost:8000/redoc")

if __name__ == "__main__":
    main()

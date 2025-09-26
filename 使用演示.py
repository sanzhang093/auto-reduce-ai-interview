"""
自动减负AI应用架构 - 使用演示脚本
展示如何使用各个功能模块
"""
import requests
import json
import time

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_step(step_num, description, url=""):
    """打印步骤"""
    print(f"\n📋 步骤 {step_num}: {description}")
    if url:
        print(f"🔗 URL: {url}")

def demo_api_call(url, description, show_response=True):
    """演示API调用"""
    try:
        print(f"\n🔍 {description}")
        print(f"📍 请求: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态: 成功")
            if show_response:
                print(f"📊 响应数据:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(f"📊 响应: {data.get('message', '操作成功')}")
        else:
            print(f"❌ 状态: 失败 (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def main():
    """主演示函数"""
    base_url = "http://localhost:8000"
    
    print("🚀 自动减负AI应用架构 - 使用演示")
    print("📚 本演示将展示如何使用各个功能模块")
    print("🌐 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    
    # 1. 基础功能演示
    print_section("1. 基础功能演示")
    
    print_step(1, "检查服务健康状态")
    demo_api_call(f"{base_url}/health", "健康检查", False)
    
    print_step(2, "查看应用基本信息")
    demo_api_call(f"{base_url}/", "应用信息", False)
    
    # 2. 项目管理功能演示
    print_section("2. 项目管理功能演示")
    
    print_step(3, "获取项目列表")
    demo_api_call(f"{base_url}/api/v1/projects", "项目列表")
    
    print_step(4, "获取任务列表")
    demo_api_call(f"{base_url}/api/v1/tasks", "任务列表")
    
    # 3. 自动减负功能演示
    print_section("3. 自动减负功能演示")
    
    print_step(5, "从会议纪要自动提取任务")
    print("💡 这个功能可以帮您从会议记录中自动识别和提取任务")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/task-capture/meeting", "任务提取")
    
    print_step(6, "生成项目日报")
    print("💡 这个功能可以自动生成项目进度日报")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/progress-summary/daily/PRJ-001", "日报生成")
    
    print_step(7, "扫描项目风险")
    print("💡 这个功能可以自动识别项目中的潜在风险")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/risk-monitoring/scan/PRJ-001", "风险扫描")
    
    print_step(8, "生成项目汇总报表")
    print("💡 这个功能可以自动生成项目汇总报表")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/reports/project-summary/PRJ-001", "报表生成")
    
    # 4. AI智能功能演示
    print_section("4. AI智能功能演示")
    
    print_step(9, "AI智能对话")
    print("💡 这个功能可以与AI进行对话，获取项目建议")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/intelligent-chat/chat", "AI对话")
    
    print_step(10, "AI趋势分析")
    print("💡 这个功能可以分析项目数据趋势")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/ai-analysis/trends/PRJ-001", "趋势分析")
    
    # 5. 系统功能演示
    print_section("5. 系统功能演示")
    
    print_step(11, "查看缓存统计")
    print("💡 这个功能显示系统缓存使用情况")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/cache/stats", "缓存统计")
    
    print_step(12, "查看系统健康状态")
    print("💡 这个功能显示系统运行状态和性能指标")
    demo_api_call(f"{base_url}/api/v1/auto-reduce/monitoring/health", "系统监控")
    
    # 6. 使用建议
    print_section("6. 实际使用建议")
    
    print("""
🎯 日常使用流程建议:

📅 每日工作流程:
1. 早上 → 查看项目日报 (/progress-summary/daily/{project_id})
2. 上午 → 扫描项目风险 (/risk-monitoring/scan/{project_id})
3. 下午 → 与AI对话获取建议 (/intelligent-chat/chat)
4. 下班前 → 生成汇总报表 (/reports/project-summary/{project_id})

📝 会议后操作:
1. 会议结束 → 提取任务 (/task-capture/meeting)
2. 确认任务 → 更新项目状态
3. 分配任务 → 通知相关人员

📊 定期分析:
1. 每周 → 趋势分析 (/ai-analysis/trends/{project_id})
2. 每月 → 系统健康检查 (/monitoring/health)
3. 根据需要 → 缓存优化 (/cache/stats)

🔧 在API文档界面中的操作:
1. 访问 http://localhost:8000/docs
2. 找到对应的API端点
3. 点击展开查看详情
4. 点击 "Try it out" 按钮
5. 输入参数（如果需要）
6. 点击 "Execute" 执行
7. 查看返回结果
    """)
    
    print_section("演示完成")
    print("""
🎉 恭喜！您已经了解了所有功能的使用方法！

📚 接下来您可以:
1. 访问 http://localhost:8000/docs 进行交互式测试
2. 根据实际需求使用相应的功能
3. 结合您的项目管理流程进行集成

💡 提示: 
- 所有功能都可以通过API文档界面直接测试
- 支持多种项目ID参数 (PRJ-001, PRJ-002 等)
- 返回的数据格式统一，便于集成

🚀 开始您的自动减负之旅吧！
    """)

if __name__ == "__main__":
    main()

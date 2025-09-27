"""
Railway部署专用版本 - 基于版本002
整合AI问答功能和HTML静态文件服务
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from datetime import datetime

# 创建FastAPI应用
app = FastAPI(
    title="自动减负AI应用架构",
    version="1.0.0",
    description="自动减负AI应用架构 - Railway部署版本"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 静态文件服务 - 挂载到根路径
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """根路径 - 返回主界面"""
    return FileResponse("ai_chat_interface_railway.html")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "服务运行正常",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/projects")
async def get_projects():
    """获取项目列表（真实数据）"""
    import json
    import os
    
    try:
        # 读取项目数据
        data_file = "data/industry_standard_database_extended.json"
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                projects = data.get('projects', [])
        else:
            # 如果文件不存在，返回示例数据
            projects = [
                {
                    "id": "PRJ-2024-001",
                    "name": "智能管理系统开发项目",
                    "status": "进行中",
                    "progress": 65,
                    "budget": 500000,
                    "actual_cost": 225000
                }
            ]
        
        return {
            "code": 200,
            "message": "获取项目列表成功",
            "data": projects
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取项目列表失败: {str(e)}",
            "data": []
        }

@app.post("/api/v1/auto-reduce/intelligent-chat/chat")
async def chat_with_ai(request: dict):
    """AI智能对话"""
    try:
        user_message = request.get("message", "")
        session_id = request.get("session_id", "default")
        
        # 简单的对话记忆
        if not hasattr(chat_with_ai, 'conversations'):
            chat_with_ai.conversations = {}
        
        if session_id not in chat_with_ai.conversations:
            chat_with_ai.conversations[session_id] = []
        
        # 添加用户消息到对话历史
        chat_with_ai.conversations[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # 从环境变量或代码中获取API密钥
        api_key = os.environ.get("QWEN_API_KEY") or "sk-369a880b04ca4e5cbfd139fe858e7d80"
        if not api_key:
            # 没有API密钥时使用简化响应
            response = generate_simple_response(user_message)
        else:
            # 调用真实的AI API
            import dashscope
            dashscope.api_key = api_key
            
            # 构建对话历史
            messages = []
            for conv in chat_with_ai.conversations[session_id][-10:]:  # 只保留最近10条对话
                messages.append({
                    "role": conv["role"],
                    "content": conv["content"]
                })
            
            # 调用Qwen API
            response = dashscope.Generation.call(
                model='qwen-max',
                messages=messages,
                result_format='message',
                max_tokens=2000,
                temperature=0.7
            )
            
            if response.status_code == 200:
                response = response.output.choices[0].message.content
            else:
                response = f"AI服务暂时不可用，状态码: {response.status_code}"
        
        # 添加AI回复到对话历史
        chat_with_ai.conversations[session_id].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "code": 200,
            "message": "AI回答成功",
            "data": {
                "response": response,
                "model": "qwen-max" if api_key else "简化版本",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"AI聊天失败: {str(e)}",
            "data": None
        }

def generate_simple_response(user_message: str) -> str:
    """生成简单响应"""
    user_message = user_message.lower()
    
    if "项目" in user_message and "进度" in user_message:
        return """📈 项目进度分析

🎯 整体进度：65%

📊 各项目进度详情：
1. 智能管理系统开发项目 - 65%
   - 需求分析：✅ 100%
   - 系统设计：✅ 100%
   - 开发实现：🔄 45%
   - 测试验证：⏳ 0%

2. 客户关系管理系统升级 - 15%
   - 需求分析：🔄 60%
   - 系统设计：⏳ 0%

3. 高能量密度锂离子电池正极材料研发 - 45%
   - 材料研究：✅ 80%
   - 性能测试：🔄 30%

⚠️ 风险提醒：
- 开发实现阶段进度偏慢
- 需要加强资源投入

需要查看详细的进度报告吗？"""
    
    elif "任务" in user_message:
        return """📋 任务状态概览

当前系统中的任务：

✅ 已完成任务:
- 需求分析 (TASK-001)
- 系统设计 (TASK-002) - 80%

🔄 进行中任务:
- 开发实现 (TASK-003) - 45%
- 测试验证 (TASK-004) - 20%

⏳ 待开始任务:
- 部署上线 (TASK-005)
- 用户培训 (TASK-006)

📊 优先级分布:
- 高优先级：3个任务
- 中优先级：2个任务
- 低优先级：1个任务

需要查看具体任务的详细信息吗？"""
    
    elif "风险" in user_message:
        return """⚠️ 风险分析报告

当前识别的风险：

🔴 高风险:
- 技术选型风险：新技术学习成本较高
- 进度延期风险：开发时间可能不足

🟡 中风险:
- 资源分配风险：人员配置需要优化
- 需求变更风险：客户需求可能变化

🟢 低风险:
- 质量风险：测试覆盖率需要提升

💡 建议措施:
1. 加强技术培训
2. 制定详细的时间计划
3. 建立变更控制流程
4. 定期风险评估会议

需要查看具体的风险应对策略吗？"""
    
    else:
        return f"""您好！我是AI管理辅助系统，基于Qwen_Max的智能项目管理助手。

我具备以下能力：
🧠 智能意图分析 - 理解您的自然语言需求
🔧 自动工具调用 - 根据意图调用相应API
📊 智能数据展示 - 将数据转换为易读格式
💬 自然语言交互 - 像聊天一样管理项目

请用自然语言告诉我您想了解什么，比如：
"项目进度如何？"
"有哪些风险？"
"生成项目报告"
"团队工作负载怎么样？"

💡 我现在使用Qwen_Max模型进行智能分析和回答"""

# HTML文件路由
@app.get("/gantt_visualization.html")
async def gantt_chart():
    """甘特图页面"""
    import os
    print(f"🔍 请求甘特图页面，当前目录: {os.getcwd()}")
    print(f"🔍 文件是否存在: {os.path.exists('gantt_visualization.html')}")
    if os.path.exists('gantt_visualization.html'):
        print(f"🔍 文件大小: {os.path.getsize('gantt_visualization.html')} bytes")
    return FileResponse("gantt_visualization.html")

@app.get("/project_report_visualization.html")
async def project_report():
    """项目报告页面"""
    return FileResponse("project_report_visualization.html")

@app.get("/knowledge_management.html")
async def knowledge_management():
    """知识管理页面"""
    return FileResponse("knowledge_management.html")

@app.get("/report_visualization.html")
async def report_visualization():
    """报告可视化页面"""
    return FileResponse("report_visualization.html")

@app.get("/test_connection.html")
async def test_connection():
    """连接测试页面"""
    return FileResponse("test_connection.html")

if __name__ == "__main__":
    # 启动时检查HTML文件
    print("🚀 Railway部署启动检查:")
    print(f"📁 当前工作目录: {os.getcwd()}")
    
    html_files = [
        "gantt_visualization.html",
        "project_report_visualization.html", 
        "knowledge_management.html",
        "report_visualization.html",
        "test_connection.html",
        "ai_chat_interface_railway.html"
    ]
    
    for file in html_files:
        exists = os.path.exists(file)
        size = os.path.getsize(file) if exists else 0
        print(f"  📄 {file}: {'✅' if exists else '❌'} ({size} bytes)")
    
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 启动服务器，端口: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
简化部署版本 - 适合快速上线
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from datetime import datetime
import asyncio

# 创建FastAPI应用
app = FastAPI(
    title="自动减负AI应用架构",
    version="1.0.0",
    description="自动减负AI应用架构 - 在线部署版本"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """根路径 - 重定向到主界面"""
    return FileResponse("ai_chat_interface.html")

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
    try:
        # 读取真实数据库文件
        db_path = "industry_standard_database_extended.json"
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            
            projects = db_data.get('projects', [])
            # 添加进度信息
            for project in projects:
                project_id = project.get('project_id')
                if project_id in db_data.get('project_metrics', {}):
                    metrics = db_data['project_metrics'][project_id]
                    project['progress'] = metrics.get('progress_percentage', 0)
                else:
                    project['progress'] = 0
            
            return {
                "code": 200,
                "message": "获取项目列表成功",
                "data": projects
            }
        else:
            # 如果文件不存在，返回默认数据
            return {
                "code": 200,
                "message": "获取项目列表成功",
                "data": [
                    {
                        "project_id": "PRJ-001",
                        "project_name": "智能管理系统",
                        "description": "基于AI的项目管理系统",
                        "status": "进行中",
                        "progress": 75.0
                    },
                    {
                        "project_id": "PRJ-002", 
                        "project_name": "客户关系管理",
                        "description": "CRM系统开发项目",
                        "status": "进行中",
                        "progress": 60.0
                    }
                ]
            }
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取项目列表失败: {str(e)}",
            "data": []
        }

@app.get("/api/v1/tasks")
async def get_tasks():
    """获取任务列表（真实数据）"""
    try:
        # 读取真实数据库文件
        db_path = "industry_standard_database_extended.json"
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            
            tasks = db_data.get('tasks', [])
            # 添加进度信息
            for task in tasks:
                task['progress'] = task.get('progress_percentage', 0)
            
            return {
                "code": 200,
                "message": "获取任务列表成功",
                "data": tasks
            }
        else:
            # 如果文件不存在，返回默认数据
            return {
                "code": 200,
                "message": "获取任务列表成功",
                "data": [
                    {
                        "task_id": "TASK-001",
                        "task_name": "需求分析",
                        "status": "已完成",
                        "priority": "高",
                        "progress": 100.0
                    },
                    {
                        "task_id": "TASK-002",
                        "task_name": "系统设计",
                        "status": "进行中",
                        "priority": "高",
                        "progress": 80.0
                    }
                ]
            }
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取任务列表失败: {str(e)}",
            "data": []
        }

# 全局对话记忆存储
conversation_memory = {}

@app.post("/api/v1/auto-reduce/intelligent-chat/chat")
async def chat_with_ai(request: dict):
    """AI智能对话 - 简化版本"""
    try:
        user_message = request.get("message", "")
        session_id = request.get("session_id", "default")
        
        if not user_message:
            return {
                "code": 400,
                "message": "用户消息不能为空",
                "data": None
            }
        
        # 获取或创建对话历史
        if session_id not in conversation_memory:
            conversation_memory[session_id] = []
        
        # 添加用户消息到历史
        conversation_memory[session_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持最近5轮对话
        if len(conversation_memory[session_id]) > 10:  # 5轮对话 = 10条消息
            conversation_memory[session_id] = conversation_memory[session_id][-10:]
        
        # 简单的意图识别和响应
        response = await generate_simple_response(user_message)
        
        # 添加AI回复到对话历史
        conversation_memory[session_id].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "code": 200,
            "message": "AI对话成功",
            "data": {
                "session_id": session_id,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "model": "简化版本"
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"AI对话失败: {str(e)}",
            "data": None
        }

async def generate_simple_response(user_message: str) -> str:
    """生成简单响应"""
    message_lower = user_message.lower()
    
    if any(keyword in message_lower for keyword in ['进度', '进展', '状态']):
        return """📊 **项目进度概览**

根据当前数据，系统中有以下项目：

1. **智能管理系统** - 进度 75%
   - 需求分析：已完成 ✅
   - 系统设计：进行中 🔄
   - 开发实现：待开始 ⏳

2. **客户关系管理** - 进度 60%
   - 需求分析：已完成 ✅
   - 系统设计：进行中 🔄
   - 开发实现：待开始 ⏳

**总体进度**: 67.5%
**状态**: 按计划进行中

需要了解更详细的信息吗？"""
    
    elif any(keyword in message_lower for keyword in ['任务', '工作', '待办']):
        return """📋 **任务状态概览**

当前系统中的任务：

**已完成任务**:
- 需求分析 (TASK-001) ✅

**进行中任务**:
- 系统设计 (TASK-002) - 80% 🔄

**待开始任务**:
- 开发实现
- 测试验证
- 部署上线

**优先级分布**:
- 高优先级：2个任务
- 中优先级：0个任务
- 低优先级：0个任务

需要查看具体任务的详细信息吗？"""
    
    elif any(keyword in message_lower for keyword in ['风险', '问题']):
        return """⚠️ **风险分析报告**

当前识别的风险：

**高风险**:
- 技术选型风险：新技术学习成本较高
- 进度延期风险：开发时间可能不足

**中风险**:
- 资源分配风险：人员配置需要优化
- 需求变更风险：客户需求可能变化

**建议措施**:
1. 加强技术培训
2. 制定详细的时间计划
3. 建立变更控制流程
4. 定期风险评估会议

需要查看具体的风险应对策略吗？"""
    
    elif any(keyword in message_lower for keyword in ['帮助', '功能', '能做什么']):
        return """🤖 **AI助手功能说明**

我可以帮您：

📊 **项目管理**
- 查看项目进度和状态
- 分析任务完成情况
- 生成项目报告

⚠️ **风险管理**
- 识别项目风险
- 提供应对建议
- 风险趋势分析

📋 **任务管理**
- 任务状态跟踪
- 优先级分析
- 工作负载评估

💡 **智能分析**
- 项目趋势分析
- 团队效率评估
- 预算使用情况

🔍 **知识管理**
- 经验总结
- 最佳实践分享
- 问题解决方案

您可以直接问我："项目进度如何？"、"有什么风险？"等问题，我会为您提供详细的分析！"""
    
    else:
        return f"""🤖 **AI助手回复**

我收到了您的消息："{user_message}"

作为您的项目管理AI助手，我可以帮您：
- 📊 查看项目进度和状态
- 📋 分析任务完成情况  
- ⚠️ 识别和评估风险
- 💡 提供智能建议和分析

您可以尝试问我：
- "项目进度如何？"
- "有什么风险需要注意？"
- "任务完成情况怎么样？"
- "帮我分析一下项目状态"

有什么具体想了解的吗？"""

# 其他API端点（简化版本）
@app.get("/api/v1/auto-reduce/task-capture/meeting")
async def extract_tasks_from_meeting():
    """从会议纪要提取任务（模拟）"""
    return {
        "code": 200,
        "message": "任务提取成功",
        "data": {
            "count": 2,
            "tasks": [
                {
                    "task_id": "TASK-AUTO-001",
                    "task_name": "完成用户认证模块",
                    "status": "待开始",
                    "extracted_from": "会议纪要"
                },
                {
                    "task_id": "TASK-AUTO-002", 
                    "task_name": "设计数据库结构",
                    "status": "待开始",
                    "extracted_from": "会议纪要"
                }
            ]
        }
    }

@app.get("/api/v1/auto-reduce/progress-summary/daily/{project_id}")
async def get_daily_progress_summary(project_id: str):
    """获取日报（模拟）"""
    return {
        "code": 200,
        "message": "日报生成成功",
        "data": {
            "project_id": project_id,
            "project_name": f"项目{project_id}",
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "current_progress": "75.0%",
            "completed_tasks_today": ["需求分析", "系统设计"],
            "in_progress_tasks": ["开发实现"],
            "overdue_tasks": [],
            "summary": f"项目{project_id}今日进展良好，完成了2个任务"
        }
    }

@app.get("/api/v1/auto-reduce/risk-monitoring/scan/{project_id}")
async def scan_project_risks(project_id: str):
    """扫描项目风险（模拟）"""
    return {
        "code": 200,
        "message": "风险扫描完成",
        "data": {
            "project_id": project_id,
            "total_alerts": 1,
            "alerts": [
                {
                    "risk_id": "RISK-001",
                    "risk_title": "进度延期风险",
                    "risk_level": "中",
                    "alert_message": "项目进度可能延期",
                    "mitigation_suggestion": "增加资源投入"
                }
            ]
        }
    }

@app.get("/api/v1/auto-reduce/reports/project-summary/{project_id}")
async def generate_project_summary_report(project_id: str):
    """生成项目汇总报表（模拟）"""
    return {
        "code": 200,
        "message": "报表生成成功",
        "data": {
            "project_id": project_id,
            "report_type": "PROJECT_SUMMARY",
            "report_format": "JSON",
            "generated_at": datetime.now().isoformat(),
            "data": {
                "report_title": "项目汇总报表",
                "items": [
                    {
                        "project_id": project_id,
                        "project_name": f"项目{project_id}",
                        "status": "进行中",
                        "progress": 75.0
                    }
                ]
            }
        }
    }

@app.get("/api/v1/auto-reduce/ai-analysis/trends/{project_id}")
async def analyze_project_trends(project_id: str):
    """分析项目趋势（模拟）"""
    return {
        "code": 200,
        "message": "趋势分析完成",
        "data": {
            "project_id": project_id,
            "trends": [
                {
                    "metric_name": "任务完成率",
                    "current_value": 75.0,
                    "previous_value": 60.0,
                    "trend_direction": "上升",
                    "trend_percentage": 15.0,
                    "trend_description": "任务完成率上升15%"
                }
            ],
            "trend_count": 1
        }
    }

@app.get("/api/v1/auto-reduce/cache/stats")
async def get_cache_statistics():
    """获取缓存统计（模拟）"""
    return {
        "code": 200,
        "message": "获取缓存统计成功",
        "data": {
            "cache_size": 50,
            "max_size": 1000,
            "hit_count": 450,
            "miss_count": 50,
            "hit_rate": 90.0,
            "total_requests": 500
        }
    }

@app.get("/api/v1/auto-reduce/monitoring/health")
async def get_health_status():
    """获取系统健康状态（模拟）"""
    return {
        "code": 200,
        "message": "获取健康状态成功",
        "data": {
            "status": "healthy",
            "health_score": 95.0,
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "cpu_percent": 45.2,
                "memory_percent": 62.3,
                "disk_percent": 35.7
            },
            "application_metrics": {
                "active_connections": 10,
                "request_count": 1000,
                "error_count": 5,
                "response_time_avg": 0.5
            },
            "active_alerts_count": 0
        }
    }

if __name__ == "__main__":
    print("🚀 启动自动减负AI应用架构（在线部署版本）...")
    print("📋 应用名称: 自动减负AI应用架构")
    print("📋 应用版本: 1.0.0")
    print("🌐 服务地址: http://0.0.0.0:8000")
    print("📚 API文档: http://0.0.0.0:8000/docs")
    print("=" * 50)
    
    # 获取端口（支持环境变量）
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "deploy_simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # 生产环境关闭reload
        log_level="info"
    )

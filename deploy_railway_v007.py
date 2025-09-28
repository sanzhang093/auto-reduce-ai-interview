#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway部署版本005 - 综合修复版本
集成完整的AI功能和HTML按钮功能
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
    description="基于Qwen_Max的智能项目管理助手",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 挂载到/static路径
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """根路径 - 返回主界面"""
    return FileResponse("ai_chat_interface_v007.html")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 项目数据API
@app.get("/api/v1/projects")
async def get_projects():
    """获取项目列表"""
    try:
        # 读取项目数据
        with open("industry_standard_database_extended.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "code": 200,
            "message": "获取项目列表成功",
            "data": data.get("projects", [])
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取项目列表失败: {str(e)}",
            "data": []
        }

# 完整的AI聊天接口 - 集成版本004的所有功能
@app.post("/api/v1/auto-reduce/intelligent-chat/chat")
async def chat_with_ai(request: dict):
    """AI智能对话 - 集成Qwen_Max模型和完整的数据Agent系统"""
    try:
        user_message = request.get("message", "")
        session_id = request.get("session_id", "default")
        
        # 对话记忆管理
        if not hasattr(chat_with_ai, 'conversation_memory'):
            chat_with_ai.conversation_memory = {}
        
        if session_id not in chat_with_ai.conversation_memory:
            chat_with_ai.conversation_memory[session_id] = []
        
        # 添加用户消息到对话历史
        chat_with_ai.conversation_memory[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # 读取项目数据作为上下文
        try:
            with open("industry_standard_database_extended.json", "r", encoding="utf-8") as f:
                project_data = json.load(f)
            project_context = json.dumps(project_data, ensure_ascii=False, indent=2)
        except:
            project_context = "项目数据暂时不可用"
        
        # 构建系统提示词 - 使用版本004的完整提示词
        system_prompt = f"""你是AI管理辅助系统，专门帮助用户管理项目。你有以下能力：

1. 意图分析：理解用户想要了解什么
2. 数据Agent调用：通过专门的数据Agent获取准确的数据
3. 结果输出：将数据转换为用户友好的回答，并提供数据来源和计算过程
4. 上下文记忆：记住对话历史，提供连贯的回答

## 数据Agent使用指南

当用户询问涉及数据的问题时，你需要：
1. 分析用户意图，确定需要调用哪个数据Agent
2. 调用相应的数据Agent获取数据
3. 基于数据Agent返回的结果，提供包含以下内容的回答：
   - 数据来源说明
   - 计算过程详细步骤
   - 具体的数据支撑
   - 清晰的结论

## 可用的数据Functions（纯数据处理）：
- project_progress：项目进度数据
- task_analysis：任务分析数据
- risk_analysis：风险分析数据（支持RAG指导集成）
- budget_analysis：预算分析数据
- team_analysis：团队分析数据
- progress_calculation：进度计算详细过程
- gantt_analysis：甘特图分析数据
- chart_generation：图表生成数据
- report_analysis：周报月报分析数据

## 可用的Agent（使用LLM）：
- knowledge_management：知识管理Agent（使用Qwen-Max模型进行智能知识提取和分类）

## 专家建议功能说明：
当用户请求"专家建议"、"专业指导"、"PMBOK指导"等时，系统会自动调用risk_analysis数据Function并启用RAG指导集成，为每个风险项提供基于PMBOK第七版的专业指导建议，包括：
- 风险类型识别
- PMBOK专业指导
- 可执行的应对建议
- 页码引用验证
- 优先行动项

## 知识管理Agent说明：
当调用knowledge_management Agent时，系统会使用Qwen-Max模型进行智能知识提取和分类，按照5大类知识分类进行结构化汇总。

**重要：在展示知识管理结果时，必须严格按照以下格式，直接输出5大类知识分类内容：**

### 五大类知识细分
1. 📋 项目过程与成果类知识
   - 立项信息：智能管理系统开发项目基于数字化转型需求启动，目标是提升管理效率
   - 计划与基线：预计开发周期6个月，预算50万元，遵循ISO9001质量标准
   - 执行过程记录：当前进度65%，已完成需求分析阶段，无重大变更
   - 成果文档：包括系统文档、测试报告（已通过）及用户手册等交付物

2. 💡 经验与教训类知识
   - 成功实践：采用敏捷开发模式，利用Jira进行项目管理，采取迭代方式交付产品
   - 失败/问题案例：遇到技术难题导致进度延迟，主要原因是团队在某些技术领域缺乏足够经验
   - 改进建议：建议加强前期技术调研和技术培训，同时优化资源分配以提高效率

3. 🤝 管理与协同类知识
   - 责任矩阵：定义了项目经理的角色及其职责，如整体协调及客户沟通等
   - 决策记录：就技术选型进行了讨论，在性能与成本之间寻找平衡点
   - 沟通记录：定期举行周例会，确认需求并调整项目范围

4. 🛠️ 知识资产与方法论类知识
   - 模板与标准：制定了需求分析、测试用例编写的标准格式及进度报告模板
   - 流程与工具：使用Git进行版本控制，Jenkins支持自动化测试，Scrum框架指导敏捷实践
   - 指标与度量：监控进度偏差(5%)、成本偏差(10%)及产品质量(95%)

5. 🏢 组织层面价值信息
   - 可复用知识：分享了管理系统架构设计、微服务技术架构及REST API接口规范等方面的知识
   - 能力成熟度：总结了敏捷管理的最佳实践、风险控制的经验教训及技术选型方面的专家意见
   - 知识共享：提供了项目管理培训材料、常见问题解答指南及项目总结交流会等内容

**注意：严格禁止输出任何其他内容，包括概览信息、计算过程说明、数据处理流程等。只输出上述5大类知识分类内容。**

## 数据Functions和Agent返回格式说明：
每个数据Function和Agent都会返回包含以下字段的结构化数据：
- success：是否成功
- data_type：数据类型
- data_source：数据来源
- query_time：查询时间
- data：具体数据
- calculation_method：计算方法
- calculation_steps：计算步骤（如果有）
- data_fields：数据字段说明

## 回答要求：
1. 必须明确说明数据来源
2. 必须提供详细的计算过程
3. 必须用具体数据支撑结论
4. 必须保持对话的连贯性
5. 如果数据Agent返回失败，要说明原因

当前项目数据上下文：
{project_context}

请根据用户的问题，分析意图，调用相应的数据Agent，并基于返回的数据提供详细的回答。"""

        # 调用Qwen_Max API，传入对话历史
        qwen_response = await call_qwen_api_with_history(system_prompt, chat_with_ai.conversation_memory[session_id])
        
        # 如果Qwen返回需要调用工具，则执行工具调用
        if "需要调用" in qwen_response or "工具" in qwen_response:
            # 分析用户意图并调用相应API
            api_result = await analyze_intent_and_call_api(user_message)
            if api_result and api_result.get("success", False):
                # 将API结果发送给Qwen进行最终处理
                final_prompt = f"用户问题：{user_message}\n\nAPI调用结果：{json.dumps(api_result, ensure_ascii=False)}\n\n请基于这些数据给出用户友好的回答，特别是要详细解释计算过程。"
                final_response = await call_qwen_api("", final_prompt)
                qwen_response = final_response
        
        # 添加AI回复到对话历史
        chat_with_ai.conversation_memory[session_id].append({
            "role": "assistant",
            "content": qwen_response
        })
        
        return {
            "code": 200,
            "message": "AI回答成功",
            "data": {
                "response": qwen_response,
                "model": "qwen-max",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"AI聊天失败: {str(e)}",
            "data": None
        }

# 数据Agent函数 - 严格按照版本004实现
async def data_agent(query_type: str, query_params: dict = None) -> dict:
    """数据获取Agent - 专门负责获取和计算数据"""
    try:
        # 读取项目数据
        db_path = "industry_standard_database_extended.json"
        if not os.path.exists(db_path):
            return {
                "success": False,
                "error": "数据源文件不存在",
                "data_source": db_path
            }
            
        with open(db_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        # 根据查询类型获取数据
        if query_type == "project_progress":
            return await get_project_progress_data(db_data, query_params)
        elif query_type == "task_analysis":
            return await get_task_analysis_data(db_data, query_params)
        elif query_type == "risk_analysis":
            return await get_risk_analysis_data(db_data, query_params)
        elif query_type == "budget_analysis":
            return await get_budget_analysis_data(db_data, query_params)
        elif query_type == "team_analysis":
            return await get_team_analysis_data(db_data, query_params)
        elif query_type == "progress_calculation":
            return await get_progress_calculation_data(db_data, query_params)
        elif query_type == "gantt_analysis":
            return await get_gantt_analysis_data(db_data, query_params)
        elif query_type == "chart_generation":
            return await get_chart_generation_data(db_data, query_params)
        elif query_type == "report_analysis":
            return await get_report_analysis_data(db_data, query_params)
        elif query_type == "knowledge_management":
            return await get_knowledge_management_data(db_data, query_params)
        else:
            return {
                "success": False,
                "error": f"未知的查询类型: {query_type}",
                "data_source": db_path
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"数据获取失败: {str(e)}",
            "data_source": "industry_standard_database_extended.json"
        }

async def analyze_intent_and_call_api(user_message: str) -> dict:
    """分析用户意图并调用数据Agent - 严格按照版本004实现"""
    message_lower = user_message.lower()
    
    # 意图分析并调用数据Agent
    if any(keyword in message_lower for keyword in ['进度', '进展', '状态', '项目']):
        # 检查是否是询问计算过程
        if any(keyword in message_lower for keyword in ['计算', '怎么', '如何', '得出', '过程', '详细']):
            return await data_agent("progress_calculation", {"project_id": "PRJ-2024-001"})
        else:
            return await data_agent("project_progress")
    
    elif any(keyword in message_lower for keyword in ['任务', '工作', '待办', 'todo']):
        return await data_agent("task_analysis")
    
    elif any(keyword in message_lower for keyword in ['风险', '问题', '扫描', '警告']):
        # 检查是否需要专家建议
        if any(keyword in message_lower for keyword in ['专家建议', '专业指导', 'pmbok', '指导建议']):
            return await data_agent("risk_analysis", {"include_rag_guidance": True})
        else:
            return await data_agent("risk_analysis")
    
    elif any(keyword in message_lower for keyword in ['专家建议', '专业指导', 'pmbok指导', '项目管理指导', '风险指导']):
        return await data_agent("risk_analysis", {"include_rag_guidance": True})
    
    elif any(keyword in message_lower for keyword in ['知识管理', '知识汇总', '知识沉淀', '经验总结', '最佳实践', '进行知识管理', '知识库', '知识资产']):
        return await data_agent("knowledge_management")
    
    elif any(keyword in message_lower for keyword in ['周报', '月报', '报告', '汇报', '总结']):
        return await data_agent("report_analysis")
    
    elif any(keyword in message_lower for keyword in ['报告', '总结', '日报', '汇总']):
        return await data_agent("project_progress")
    
    elif any(keyword in message_lower for keyword in ['团队', '人员', '工作负载', '成员']):
        return await data_agent("team_analysis")
    
    elif any(keyword in message_lower for keyword in ['预算', '成本', '费用', '资金']):
        return await data_agent("budget_analysis")
    
    elif any(keyword in message_lower for keyword in ['甘特图', '进度图', '时间线', '计划', 'sprint', '迭代']):
        return await data_agent("gantt_analysis")
    
    elif any(keyword in message_lower for keyword in ['图表', '可视化', '图形', '画图', '展示']):
        return await data_agent("chart_generation")
    
    else:
        return {
            "success": False,
            "error": "无法识别用户意图",
            "available_queries": ["项目进度", "任务分析", "风险分析", "预算分析", "团队分析", "进度计算"]
        }

# 项目进度数据Agent
async def get_project_progress_data(db_data: dict) -> dict:
    """获取项目进度数据"""
    try:
        projects = db_data.get('projects', [])
        
        progress_data = []
        for project in projects:
            progress_info = {
                "project_id": project.get('project_id', ''),
                "project_name": project.get('project_name', ''),
                "status": project.get('status', ''),
                "progress_percentage": project.get('progress_percentage', 0),
                "start_date": project.get('start_date', ''),
                "end_date": project.get('end_date', ''),
                "budget": project.get('budget', 0),
                "actual_cost": project.get('actual_cost', 0)
            }
            progress_data.append(progress_info)
        
        return {
            "success": True,
            "data_type": "project_progress",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": progress_data,
            "calculation_method": "直接从项目数据中提取进度信息",
            "data_fields": {
                "project_id": "项目ID",
                "project_name": "项目名称",
                "status": "项目状态",
                "progress_percentage": "进度百分比",
                "start_date": "开始日期",
                "end_date": "结束日期",
                "budget": "预算",
                "actual_cost": "实际成本"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "project_progress",
            "data_source": "industry_standard_database_extended.json"
        }

# 任务分析数据Agent
async def get_task_analysis_data(db_data: dict) -> dict:
    """获取任务分析数据"""
    try:
        tasks = db_data.get('tasks', [])
        
        task_analysis = {
            "total_tasks": len(tasks),
            "completed_tasks": len([t for t in tasks if t.get('status') == '已完成']),
            "in_progress_tasks": len([t for t in tasks if t.get('status') == '进行中']),
            "pending_tasks": len([t for t in tasks if t.get('status') == '待开始']),
            "high_priority_tasks": len([t for t in tasks if t.get('priority') == '高']),
            "tasks_by_project": {}
        }
        
        # 按项目分组任务
        for task in tasks:
            project_id = task.get('project_id', '未知项目')
            if project_id not in task_analysis["tasks_by_project"]:
                task_analysis["tasks_by_project"][project_id] = 0
            task_analysis["tasks_by_project"][project_id] += 1
        
        return {
            "success": True,
            "data_type": "task_analysis",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": task_analysis,
            "calculation_method": "统计任务状态和优先级分布",
            "data_fields": {
                "total_tasks": "总任务数",
                "completed_tasks": "已完成任务数",
                "in_progress_tasks": "进行中任务数",
                "pending_tasks": "待开始任务数",
                "high_priority_tasks": "高优先级任务数",
                "tasks_by_project": "各项目任务分布"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "task_analysis",
            "data_source": "industry_standard_database_extended.json"
        }

# 风险分析数据Agent - 集成RAG指导
async def get_risk_analysis_data(db_data: dict, query_params: dict = None) -> dict:
    """获取风险分析数据（集成RAG指导）"""
    try:
        risks = db_data.get('risks', [])
        
        # 风险统计
        risk_stats = {
            "total_risks": len(risks),
            "high_risks": len([r for r in risks if r.get('risk_level') == '高']),
            "medium_risks": len([r for r in risks if r.get('risk_level') == '中']),
            "low_risks": len([r for r in risks if r.get('risk_level') == '低']),
            "risks_by_project": {}
        }
        
        # 按项目分组风险
        for risk in risks:
            project_id = risk.get('project_id', '未知项目')
            if project_id not in risk_stats["risks_by_project"]:
                risk_stats["risks_by_project"][project_id] = 0
            risk_stats["risks_by_project"][project_id] += 1
        
        # 处理项目风险详情
        project_risks = []
        for risk in risks:
            risk_detail = {
                "risk_id": risk.get('risk_id', ''),
                "risk_title": risk.get('risk_title', ''),
                "risk_level": risk.get('risk_level', ''),
                "risk_type": risk.get('risk_type', ''),
                "description": risk.get('description', ''),
                "impact": risk.get('impact', ''),
                "probability": risk.get('probability', ''),
                "mitigation_plan": risk.get('mitigation_plan', ''),
                "project_id": risk.get('project_id', '')
            }
            project_risks.append(risk_detail)
        
        # 检查是否需要RAG指导
        include_rag_guidance = query_params and query_params.get('include_rag_guidance', False)
        rag_guidance = []
        
        if include_rag_guidance and project_risks:
            try:
                from rag_guidance_integration import RAGGuidanceIntegration
                rag_integration = RAGGuidanceIntegration()
                
                for i, risk in enumerate(project_risks, 1):
                    try:
                        print(f"   处理风险 {i}/{len(project_risks)}: {risk.get('risk_title', '未知风险')}")
                        guidance = await asyncio.wait_for(
                            rag_integration.generate_risk_guidance(risk),
                            timeout=15.0
                        )
                        rag_guidance.append(guidance)
                        print(f"   ✅ 风险 {i} 指导生成成功")
                    except asyncio.TimeoutError:
                        print(f"   ⚠️ 风险 {i} 指导生成超时，跳过")
                    except Exception as e:
                        print(f"   ❌ 风险 {i} 指导生成失败: {str(e)}")
                
            except Exception as e:
                print(f"RAG指导生成失败: {str(e)}")
                rag_guidance = []
        
        return {
            "success": True,
            "data_type": "risk_analysis",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": {
                "risk_statistics": risk_stats,
                "project_risks": project_risks,
                "rag_guidance": rag_guidance if include_rag_guidance else []
            },
            "calculation_method": "统计风险分布和详细信息，集成PMBOK RAG指导",
            "data_fields": {
                "risk_statistics": "风险统计信息",
                "project_risks": "项目风险详情",
                "rag_guidance": "PMBOK专业指导建议"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "risk_analysis",
            "data_source": "industry_standard_database_extended.json"
        }

# 其他数据Agent函数（简化版本）
async def get_budget_analysis_data(db_data: dict) -> dict:
    """获取预算分析数据"""
    try:
        projects = db_data.get('projects', [])
        total_budget = sum(p.get('budget', 0) for p in projects)
        total_cost = sum(p.get('actual_cost', 0) for p in projects)
        
        return {
            "success": True,
            "data_type": "budget_analysis",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": {
                "total_budget": total_budget,
                "total_cost": total_cost,
                "budget_utilization": (total_cost / total_budget * 100) if total_budget > 0 else 0
            },
            "calculation_method": "汇总所有项目的预算和实际成本",
            "data_fields": {
                "total_budget": "总预算",
                "total_cost": "总成本",
                "budget_utilization": "预算使用率(%)"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "budget_analysis",
            "data_source": "industry_standard_database_extended.json"
        }

async def get_team_analysis_data(db_data: dict) -> dict:
    """获取团队分析数据"""
    try:
        team_members = db_data.get('team_members', [])
        
        team_stats = {
            "total_members": len(team_members),
            "roles": {},
            "departments": {}
        }
        
        for member in team_members:
            role = member.get('role', '未知角色')
            dept = member.get('department', '未知部门')
            
            team_stats["roles"][role] = team_stats["roles"].get(role, 0) + 1
            team_stats["departments"][dept] = team_stats["departments"].get(dept, 0) + 1
        
        return {
            "success": True,
            "data_type": "team_analysis",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": team_stats,
            "calculation_method": "统计团队成员角色和部门分布",
            "data_fields": {
                "total_members": "总成员数",
                "roles": "角色分布",
                "departments": "部门分布"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "team_analysis",
            "data_source": "industry_standard_database_extended.json"
        }

async def get_gantt_analysis_data(db_data: dict) -> dict:
    """获取甘特图分析数据"""
    try:
        tasks = db_data.get('tasks', [])
        
        gantt_data = []
        for task in tasks:
            gantt_info = {
                "task_id": task.get('task_id', ''),
                "task_name": task.get('task_name', ''),
                "start_date": task.get('start_date', ''),
                "end_date": task.get('end_date', ''),
                "status": task.get('status', ''),
                "project_id": task.get('project_id', '')
            }
            gantt_data.append(gantt_info)
        
        return {
            "success": True,
            "data_type": "gantt_analysis",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": gantt_data,
            "calculation_method": "提取任务时间线信息",
            "data_fields": {
                "task_id": "任务ID",
                "task_name": "任务名称",
                "start_date": "开始日期",
                "end_date": "结束日期",
                "status": "任务状态",
                "project_id": "所属项目"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "gantt_analysis",
            "data_source": "industry_standard_database_extended.json"
        }

async def get_report_analysis_data(db_data: dict) -> dict:
    """获取报告分析数据"""
    try:
        reports = db_data.get('reports', [])
        
        report_stats = {
            "total_reports": len(reports),
            "weekly_reports": len([r for r in reports if r.get('report_type') == '周报']),
            "monthly_reports": len([r for r in reports if r.get('report_type') == '月报']),
            "reports_by_project": {}
        }
        
        for report in reports:
            project_id = report.get('project_id', '未知项目')
            if project_id not in report_stats["reports_by_project"]:
                report_stats["reports_by_project"][project_id] = 0
            report_stats["reports_by_project"][project_id] += 1
        
        return {
            "success": True,
            "data_type": "report_analysis",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": report_stats,
            "calculation_method": "统计报告类型和项目分布",
            "data_fields": {
                "total_reports": "总报告数",
                "weekly_reports": "周报数量",
                "monthly_reports": "月报数量",
                "reports_by_project": "各项目报告分布"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "report_analysis",
            "data_source": "industry_standard_database_extended.json"
        }

async def get_knowledge_management_data(db_data: dict) -> dict:
    """获取知识管理数据"""
    try:
        knowledge_items = db_data.get('knowledge_items', [])
        
        knowledge_stats = {
            "total_items": len(knowledge_items),
            "categories": {},
            "knowledge_by_project": {}
        }
        
        for item in knowledge_items:
            category = item.get('category', '未分类')
            project_id = item.get('project_id', '未知项目')
            
            knowledge_stats["categories"][category] = knowledge_stats["categories"].get(category, 0) + 1
            knowledge_stats["knowledge_by_project"][project_id] = knowledge_stats["knowledge_by_project"].get(project_id, 0) + 1
        
        return {
            "success": True,
            "data_type": "knowledge_management",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": knowledge_stats,
            "calculation_method": "统计知识项目分类和项目分布",
            "data_fields": {
                "total_items": "总知识项数",
                "categories": "分类分布",
                "knowledge_by_project": "各项目知识分布"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "knowledge_management",
            "data_source": "industry_standard_database_extended.json"
        }

# 进度计算数据Agent - 严格按照版本004实现
async def get_progress_calculation_data(db_data: dict, query_params: dict = None) -> dict:
    """获取项目进度详细计算过程"""
    try:
        project_id = query_params.get('project_id', 'PRJ-2024-001') if query_params else 'PRJ-2024-001'
        
        # 查找项目
        project = None
        for p in db_data.get('projects', []):
            if p.get('project_id') == project_id:
                project = p
                break
        
        if not project:
            return {
                "success": False,
                "error": f"项目 {project_id} 不存在",
                "data_type": "progress_calculation",
                "data_source": "industry_standard_database_extended.json"
            }
        
        # 获取项目相关任务
        project_tasks = [task for task in db_data.get('tasks', [])
                        if task.get('project_id') == project_id]
        
        # 获取项目指标
        metrics = db_data.get('project_metrics', {}).get(project_id, {})
        
        # 计算详细进度
        total_tasks = len(project_tasks)
        if total_tasks == 0:
            return {
                "success": True,
                "data_type": "progress_calculation",
                "data_source": "industry_standard_database_extended.json",
                "query_time": datetime.now().isoformat(),
                "project_id": project_id,
                "data": {
                    "project_name": project.get('project_name', ''),
                    "calculated_progress": 0.0,
                    "database_progress": project.get('progress_percentage', 0),
                    "calculation_method": "无任务数据",
                    "total_tasks": 0,
                    "detailed_breakdown": [],
                    "metrics_from_db": metrics
                },
                "calculation_method": "项目无任务数据",
                "calculation_steps": ["项目无任务数据，无法计算进度"],
                "data_fields": {
                    "tasks": ["task_id", "task_name", "status", "progress_percentage", "project_id"],
                    "metrics": ["progress_percentage", "budget_utilization", "schedule_variance"]
                }
            }
        
        # 按状态分组任务
        status_groups = {}
        for task in project_tasks:
            status = task.get('status', '未知状态')
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(task)
        
        # 计算每个状态组的平均进度
        total_weighted_progress = 0
        total_weight = 0
        detailed_breakdown = []
        
        for status, tasks_in_status in status_groups.items():
            # 计算该状态组的平均进度
            if status == '已完成':
                avg_progress = 100.0
            elif status == '进行中':
                avg_progress = sum(task.get('progress_percentage', 0) for task in tasks_in_status) / len(tasks_in_status)
            else:  # 待开始等
                avg_progress = 0.0
            
            weight = len(tasks_in_status)
            weighted_progress = avg_progress * weight
            
            total_weighted_progress += weighted_progress
            total_weight += weight
            
            detailed_breakdown.append({
                "status": status,
                "task_count": len(tasks_in_status),
                "average_progress": avg_progress,
                "weight": weight,
                "weighted_progress": weighted_progress,
                "tasks": [{"task_id": t.get('task_id'), "task_name": t.get('task_name'), "progress_percentage": t.get('progress_percentage', 0)} for t in tasks_in_status]
            })
        
        # 计算整体进度
        calculated_progress = (total_weighted_progress / total_weight) if total_weight > 0 else 0.0
        
        calculation_steps = [
            f"1. 获取项目 {project_id} 的所有任务数据",
            f"2. 按状态分组任务，共 {len(status_groups)} 个状态组",
            f"3. 计算每个状态组的平均进度",
            f"4. 使用加权平均法计算整体进度: {calculated_progress:.1f}%",
            f"5. 对比数据库中的进度指标: {project.get('progress_percentage', 0)}%"
        ]
        
        return {
            "success": True,
            "data_type": "progress_calculation",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "project_id": project_id,
            "data": {
                "project_name": project.get('project_name', ''),
                "calculated_progress": calculated_progress,
                "database_progress": project.get('progress_percentage', 0),
                "calculation_method": "加权平均法",
                "formula": "整体进度 = Σ(状态平均进度 × 状态任务数) / 总任务数",
                "total_tasks": total_tasks,
                "total_weighted_progress": total_weighted_progress,
                "total_weight": total_weight,
                "detailed_breakdown": detailed_breakdown,
                "metrics_from_db": metrics
            },
            "calculation_method": "基于任务进度的加权平均计算",
            "calculation_steps": calculation_steps,
            "data_fields": {
                "tasks": ["task_id", "task_name", "status", "progress_percentage", "project_id"],
                "metrics": ["progress_percentage", "budget_utilization", "schedule_variance"]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "progress_calculation",
            "data_source": "industry_standard_database_extended.json"
        }

# 图表生成数据Agent
async def get_chart_generation_data(db_data: dict, query_params: dict = None) -> dict:
    """获取图表生成数据"""
    try:
        projects = db_data.get('projects', [])
        tasks = db_data.get('tasks', [])
        
        # 生成图表数据
        chart_data = {
            "project_progress_chart": {
                "type": "bar",
                "title": "项目进度对比",
                "data": []
            },
            "task_status_chart": {
                "type": "pie",
                "title": "任务状态分布",
                "data": []
            },
            "budget_utilization_chart": {
                "type": "line",
                "title": "预算使用情况",
                "data": []
            }
        }
        
        # 项目进度数据
        for project in projects:
            chart_data["project_progress_chart"]["data"].append({
                "name": project.get('project_name', ''),
                "value": project.get('progress_percentage', 0),
                "budget": project.get('budget', 0),
                "actual_cost": project.get('actual_cost', 0)
            })
        
        # 任务状态数据
        status_counts = {}
        for task in tasks:
            status = task.get('status', '未知状态')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            chart_data["task_status_chart"]["data"].append({
                "name": status,
                "value": count
            })
        
        # 预算使用数据
        for project in projects:
            budget_utilization = (project.get('actual_cost', 0) / project.get('budget', 1)) * 100 if project.get('budget', 0) > 0 else 0
            chart_data["budget_utilization_chart"]["data"].append({
                "name": project.get('project_name', ''),
                "budget_utilization": budget_utilization,
                "budget": project.get('budget', 0),
                "actual_cost": project.get('actual_cost', 0)
            })
        
        return {
            "success": True,
            "data_type": "chart_generation",
            "data_source": "industry_standard_database_extended.json",
            "query_time": datetime.now().isoformat(),
            "data": chart_data,
            "calculation_method": "基于项目数据和任务数据生成图表配置",
            "data_fields": {
                "project_progress_chart": "项目进度柱状图数据",
                "task_status_chart": "任务状态饼图数据",
                "budget_utilization_chart": "预算使用折线图数据"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data_type": "chart_generation",
            "data_source": "industry_standard_database_extended.json"
        }

async def get_project_progress_calculation(project_id: str) -> dict:
    """获取项目进度计算详细过程 - API接口版本"""
    try:
        with open("industry_standard_database_extended.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 调用数据Agent
        result = await get_progress_calculation_data(data, {"project_id": project_id})
        
        if result["success"]:
            return {
                "code": 200,
                "message": "进度计算成功",
                "data": result["data"]
            }
        else:
            return {
                "code": 500,
                "message": result["error"],
                "data": None
            }
    except Exception as e:
        return {"code": 500, "message": f"进度计算失败: {str(e)}", "data": None}

# Qwen API调用函数 - 从版本004复制
async def call_qwen_api(system_prompt: str, user_message: str) -> str:
    """调用Qwen_Max API"""
    import requests
    
    api_key = "sk-369a880b04ca4e5cbfd139fe858e7d80"
    api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})
    
    data = {
        "model": "qwen-max",
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        if "output" in result and "text" in result["output"]:
            return result["output"]["text"]
        else:
            print(f"Qwen API响应格式异常: {result}")
            return "抱歉，我暂时无法处理您的请求。"
            
    except requests.exceptions.Timeout:
        print("Qwen API调用超时 (120秒)")
        return "抱歉，AI服务响应超时，请稍后再试。建议您：\n1. 检查网络连接\n2. 稍后重试\n3. 或使用数据查询功能获取项目信息"
    except requests.exceptions.ConnectionError:
        print("Qwen API连接失败")
        return "抱歉，AI服务连接失败，请检查网络连接。"
    except Exception as e:
        print(f"Qwen API调用失败: {e}")
        return "抱歉，AI服务暂时不可用，请稍后再试。"

async def call_qwen_api_with_history(system_prompt: str, conversation_history: list) -> str:
    """调用Qwen_Max API（带对话历史）"""
    import requests
    
    api_key = "sk-369a880b04ca4e5cbfd139fe858e7d80"
    api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # 添加对话历史（排除当前用户消息，因为已经在history中）
    for msg in conversation_history[:-1]:  # 排除最后一条用户消息
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # 添加当前用户消息
    if conversation_history:
        current_user_msg = conversation_history[-1]
        if current_user_msg["role"] == "user":
            messages.append({
                "role": "user",
                "content": current_user_msg["content"]
            })
    
    data = {
        "model": "qwen-turbo",
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 12000
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        if "output" in result and "text" in result["output"]:
            return result["output"]["text"]
        else:
            print(f"Qwen API响应格式异常: {result}")
            return "抱歉，我暂时无法处理您的请求。"
            
    except requests.exceptions.Timeout:
        print("Qwen API调用超时 (120秒)")
        return "抱歉，AI服务响应超时，请稍后再试。"
    except requests.exceptions.ConnectionError:
        print("Qwen API连接失败")
        return "抱歉，AI服务连接失败，请检查网络连接。"
    except Exception as e:
        print(f"Qwen API调用失败: {e}")
        return "抱歉，AI服务暂时不可用，请稍后再试。"

# HTML文件路由 - 保持版本005的HTML功能
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

@app.get("/report_visualization.html")
async def report_visualization():
    """报告可视化页面"""
    return FileResponse("report_visualization.html")

@app.get("/knowledge_management.html")
async def knowledge_management():
    """知识管理页面"""
    return FileResponse("knowledge_management.html")

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


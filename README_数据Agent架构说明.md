# 🤖 数据Agent架构说明

## 🎯 架构概述

根据您的要求，我设计了一个专门的数据获取Agent系统，由主LLM调用来获取相关数据，并提供数据来源和计算过程来支撑结论。

## 🏗️ 系统架构

### 🧠 **主LLM + 数据Agent 架构**

```
用户问题 → 主LLM (Qwen_Max) → 数据Agent → 结构化数据 → 主LLM → 用户友好回答
```

#### 核心组件
1. **主LLM (Qwen_Max)** - 负责意图分析和结果输出
2. **数据Agent** - 专门负责数据获取和计算
3. **结构化数据** - 包含数据来源、计算过程、具体数据

## 🔧 数据Agent设计

### 1️⃣ **数据Agent核心功能**

#### 主要职责
- ✅ **数据获取** - 从数据库获取原始数据
- ✅ **数据计算** - 执行各种计算和分析
- ✅ **数据验证** - 确保数据准确性和完整性
- ✅ **元数据提供** - 提供数据来源、计算过程等信息

#### 支持的数据类型
```python
# 可用的数据Agent类型
data_agent_types = [
    "project_progress",      # 项目进度数据
    "task_analysis",         # 任务分析数据
    "risk_analysis",         # 风险分析数据
    "budget_analysis",       # 预算分析数据
    "team_analysis",         # 团队分析数据
    "progress_calculation"   # 进度计算详细过程
]
```

### 2️⃣ **数据Agent返回格式**

#### 标准化返回结构
```json
{
    "success": true,
    "data_type": "progress_calculation",
    "data_source": "industry_standard_database.json",
    "query_time": "2025-09-24T11:38:23.104747",
    "project_id": "PRJ-2024-001",
    "data": {
        "project_name": "智能管理系统开发项目",
        "calculated_progress": 47.0,
        "database_progress": 65.0,
        "calculation_method": "加权平均法",
        "formula": "整体进度 = Σ(状态平均进度 × 状态任务数) / 总任务数",
        "total_tasks": 5,
        "total_weighted_progress": 235.0,
        "total_weight": 5,
        "detailed_breakdown": [...],
        "metrics_from_db": {...}
    },
    "calculation_method": "基于任务进度的加权平均计算",
    "calculation_steps": [
        "1. 获取项目 PRJ-2024-001 的所有任务数据",
        "2. 按状态分组任务，共 3 个状态组",
        "3. 计算每个状态组的平均进度",
        "4. 使用加权平均法计算整体进度: 47.0%",
        "5. 对比数据库中的进度指标: 65.0%"
    ],
    "data_fields": {
        "tasks": ["task_id", "task_name", "status", "progress_percentage", "project_id"],
        "metrics": ["progress_percentage", "budget_utilization", "schedule_variance", ...]
    }
}
```

#### 关键字段说明
- **success**: 数据获取是否成功
- **data_type**: 数据类型标识
- **data_source**: 数据来源文件
- **query_time**: 查询时间戳
- **data**: 具体的数据内容
- **calculation_method**: 计算方法说明
- **calculation_steps**: 详细计算步骤
- **data_fields**: 数据字段说明

## 🚀 具体实现

### 1️⃣ **数据Agent调用流程**

#### 主LLM调用数据Agent
```python
# 主LLM分析用户意图
if "计算" in user_message:
    # 调用进度计算数据Agent
    api_result = await data_agent("progress_calculation", {"project_id": "PRJ-2024-001"})
elif "进度" in user_message:
    # 调用项目进度数据Agent
    api_result = await data_agent("project_progress")
```

#### 数据Agent处理流程
```python
async def data_agent(query_type: str, query_params: dict = None) -> dict:
    """数据获取Agent - 专门负责获取和计算数据"""
    try:
        # 1. 读取数据源
        with open("industry_standard_database.json", 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        # 2. 根据查询类型调用相应的处理函数
        if query_type == "progress_calculation":
            return await get_progress_calculation_data(db_data, query_params)
        elif query_type == "project_progress":
            return await get_project_progress_data(db_data, query_params)
        # ... 其他类型
        
    except Exception as e:
        return {
            "success": False,
            "error": f"数据获取失败: {str(e)}",
            "data_source": "industry_standard_database.json"
        }
```

### 2️⃣ **进度计算数据Agent示例**

#### 详细计算过程
```python
async def get_progress_calculation_data(db_data: dict, query_params: dict = None) -> dict:
    """获取进度计算详细数据"""
    # 1. 获取项目信息
    project = get_project_by_id(project_id)
    
    # 2. 获取项目相关任务
    project_tasks = get_tasks_by_project_id(project_id)
    
    # 3. 按状态分组任务
    status_groups = group_tasks_by_status(project_tasks)
    
    # 4. 计算各状态任务进度
    detailed_breakdown = []
    total_weighted_progress = 0
    total_weight = 0
    
    for status, tasks_in_status in status_groups.items():
        # 计算状态平均进度
        avg_status_progress = calculate_average_progress(tasks_in_status)
        # 计算加权进度
        weighted_progress = avg_status_progress * len(tasks_in_status)
        
        total_weighted_progress += weighted_progress
        total_weight += len(tasks_in_status)
        
        detailed_breakdown.append({
            "status": status,
            "task_count": len(tasks_in_status),
            "average_progress": round(avg_status_progress, 2),
            "weighted_progress": round(weighted_progress, 2),
            "tasks": tasks_in_status
        })
    
    # 5. 计算整体进度
    calculated_progress = total_weighted_progress / total_weight if total_weight > 0 else 0
    
    # 6. 返回结构化数据
    return {
        "success": True,
        "data_type": "progress_calculation",
        "data_source": "industry_standard_database.json",
        "calculation_method": "基于任务进度的加权平均计算",
        "calculation_steps": [
            f"1. 获取项目 {project_id} 的所有任务数据",
            f"2. 按状态分组任务，共 {len(status_groups)} 个状态组",
            f"3. 计算每个状态组的平均进度",
            f"4. 使用加权平均法计算整体进度: {round(calculated_progress, 2)}%",
            f"5. 对比数据库中的进度指标: {db_progress}%"
        ],
        "data": {
            "calculated_progress": round(calculated_progress, 2),
            "database_progress": db_progress,
            "detailed_breakdown": detailed_breakdown
        }
    }
```

### 3️⃣ **预算分析数据Agent示例**

#### 预算计算过程
```python
async def get_budget_analysis_data(db_data: dict, query_params: dict = None) -> dict:
    """获取预算分析数据"""
    project = get_project_by_id(project_id)
    budget = project.get('budget', 0)
    actual_cost = project.get('actual_cost', 0)
    
    # 计算预算使用率
    utilization_rate = (actual_cost / budget * 100) if budget > 0 else 0
    
    return {
        "success": True,
        "data_type": "budget_analysis",
        "data_source": "industry_standard_database.json",
        "calculation_method": "预算使用率 = (实际成本 / 预算) × 100%",
        "calculation_steps": [
            f"1. 获取项目 {project_id} 的预算数据: ¥{budget:,.2f}",
            f"2. 获取项目 {project_id} 的实际成本: ¥{actual_cost:,.2f}",
            f"3. 计算使用率: ({actual_cost:,.2f} / {budget:,.2f}) × 100% = {utilization_rate:.2f}%",
            f"4. 计算剩余预算: {budget:,.2f} - {actual_cost:,.2f} = ¥{budget - actual_cost:,.2f}"
        ],
        "data": {
            "budget": budget,
            "actual_cost": actual_cost,
            "utilization_rate": round(utilization_rate, 2),
            "remaining_budget": budget - actual_cost
        }
    }
```

## 🎯 主LLM集成

### 1️⃣ **系统提示词优化**

#### 数据Agent使用指南
```python
system_prompt = """你是一个智能项目管理助手，专门帮助用户管理项目。你有以下能力：

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

## 回答要求：
1. 必须明确说明数据来源
2. 必须提供详细的计算过程
3. 必须用具体数据支撑结论
4. 必须保持对话的连贯性
5. 如果数据Agent返回失败，要说明原因
"""
```

### 2️⃣ **主LLM调用流程**

#### 智能调用逻辑
```python
# 主LLM分析用户意图
qwen_response = await call_qwen_api_with_history(system_prompt, conversation_history)

# 如果主LLM判断需要调用数据Agent
if "需要调用" in qwen_response or "工具" in qwen_response:
    # 分析用户意图并调用数据Agent
    api_result = await analyze_intent_and_call_api(user_message)
    
    if api_result and api_result.get("success"):
        # 将数据Agent结果发送给主LLM进行最终处理
        final_prompt = f"""
        用户问题：{user_message}
        
        数据Agent返回结果：
        - 数据来源：{api_result.get('data_source')}
        - 数据类型：{api_result.get('data_type')}
        - 计算方法：{api_result.get('calculation_method')}
        - 计算步骤：{api_result.get('calculation_steps', [])}
        - 具体数据：{json.dumps(api_result.get('data'), ensure_ascii=False)}
        
        请基于这些数据给出用户友好的回答，特别要详细解释数据来源和计算过程。
        """
        
        final_response = await call_qwen_api("", final_prompt)
        qwen_response = final_response
```

## 📊 实际效果

### 1️⃣ **数据来源透明化**

#### 之前（无数据Agent）
```
用户：项目进度如何计算的？
AI：项目进度是通过综合考虑各个任务和里程碑的完成情况来计算的...
```

#### 现在（有数据Agent）
```
用户：项目进度如何计算的？
AI：基于数据Agent的详细分析：

📊 **数据来源**
- 数据文件：industry_standard_database.json
- 查询时间：2025-09-24T11:38:23
- 项目ID：PRJ-2024-001

🧮 **计算过程**
1. 获取项目 PRJ-2024-001 的所有任务数据
2. 按状态分组任务，共 3 个状态组
3. 计算每个状态组的平均进度
4. 使用加权平均法计算整体进度: 47.0%
5. 对比数据库中的进度指标: 65.0%

📈 **具体数据**
- 已完成任务：1个，平均进度100%
- 进行中任务：2个，平均进度67.5%
- 待开始任务：2个，平均进度0%
- 计算得出进度：47.0%
- 数据库记录进度：65.0%

💡 **结论**
项目进度47%是基于任务加权平均计算得出，而数据库中的65%可能包含了其他评估因素。
```

### 2️⃣ **计算过程详细化**

#### 预算分析示例
```
用户：智能管理系统的预算使用情况如何？
AI：基于数据Agent的预算分析：

💰 **数据来源**
- 数据文件：industry_standard_database.json
- 项目：智能管理系统开发项目 (PRJ-2024-001)

🧮 **计算过程**
1. 获取项目预算数据: ¥500,000.00
2. 获取项目实际成本: ¥225,000.00
3. 计算使用率: (¥225,000.00 / ¥500,000.00) × 100% = 45.0%
4. 计算剩余预算: ¥500,000.00 - ¥225,000.00 = ¥275,000.00

📊 **预算使用情况**
- 总预算：¥500,000.00
- 已使用：¥225,000.00
- 使用率：45.0%
- 剩余预算：¥275,000.00

💡 **分析结论**
项目预算使用率较低，还有55%的预算未使用，预算控制良好。
```

## 🌟 核心优势

### 1️⃣ **数据透明度**
- ✅ **明确数据来源** - 每个数据都有明确的来源文件
- ✅ **详细计算过程** - 提供完整的计算步骤
- ✅ **可验证性** - 用户可以验证计算过程

### 2️⃣ **系统可靠性**
- ✅ **专门化处理** - 数据Agent专门负责数据获取和计算
- ✅ **错误处理** - 完善的错误处理和异常情况处理
- ✅ **数据验证** - 确保数据的准确性和完整性

### 3️⃣ **用户体验**
- ✅ **详细解释** - 提供详细的数据来源和计算过程
- ✅ **数据支撑** - 所有结论都有具体数据支撑
- ✅ **可理解性** - 将复杂计算转换为易懂的解释

### 4️⃣ **系统扩展性**
- ✅ **模块化设计** - 易于添加新的数据Agent类型
- ✅ **标准化接口** - 统一的数据Agent调用接口
- ✅ **灵活配置** - 支持不同的查询参数和选项

## 🔮 未来扩展

### 1️⃣ **更多数据Agent类型**
- 时间分析Agent
- 质量分析Agent
- 资源利用率Agent
- 趋势预测Agent

### 2️⃣ **数据可视化**
- 图表生成Agent
- 报表生成Agent
- 仪表板数据Agent

### 3️⃣ **实时数据**
- 实时监控Agent
- 告警数据Agent
- 性能指标Agent

---

**🎉 数据Agent架构完成！现在系统可以提供透明、详细、可验证的数据分析！**

**从模糊回答到精确数据，从无来源到可追溯！** 🚀

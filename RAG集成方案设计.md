# RAG与Agent集成方案设计

## 🎯 设计目标

将RAG系统与现有的风险分析Agent集成，当发现风险项或问题时，自动提供PMBOK的专业指导建议。

## 🏗️ 系统架构

### 当前架构
```
用户问题 → 主LLM → 数据Agent → 结构化数据 → 主LLM → 用户回答
```

### 增强架构
```
用户问题 → 主LLM → 数据Agent → 结构化数据 + RAG指导 → 主LLM → 用户回答
```

## 🔧 实现方案

### 方案1: 增强现有数据Agent

在现有的`get_risk_analysis_data`函数中集成RAG指导功能：

```python
async def get_risk_analysis_data_with_rag_guidance(db_data: dict, query_params: dict = None) -> dict:
    """获取风险分析数据并集成RAG指导"""
    try:
        # 1. 获取原有风险分析数据
        risk_data = await get_risk_analysis_data(db_data, query_params)
        
        if not risk_data.get("success"):
            return risk_data
        
        # 2. 为每个风险项生成RAG指导
        risks = risk_data["data"]["risks"]
        rag_guidance = []
        
        for risk in risks:
            # 构建风险相关的查询
            risk_query = f"如何处理{risk.get('risk_level', '')}级别的{risk.get('risk_title', '')}风险"
            
            # 调用RAG系统获取PMBOK指导
            rag_results = rag_system.search_pmbok_knowledge(risk_query, top_k=3)
            
            # 验证页码引用
            claimed_pages = [r['page_number'] for r in rag_results]
            validated_pages = rag_system.validate_page_references(claimed_pages, rag_results)
            
            rag_guidance.append({
                "risk_id": risk.get('risk_id'),
                "risk_title": risk.get('risk_title'),
                "rag_query": risk_query,
                "pmbok_guidance": rag_results,
                "validated_pages": validated_pages,
                "guidance_summary": generate_guidance_summary(rag_results)
            })
        
        # 3. 返回增强的数据结构
        risk_data["data"]["rag_guidance"] = rag_guidance
        risk_data["rag_integration"] = {
            "enabled": True,
            "guidance_count": len(rag_guidance),
            "pmbok_source": "PMBOK第七版中文版"
        }
        
        return risk_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取风险分析数据失败: {str(e)}",
            "data_source": "industry_standard_database.json"
        }
```

### 方案2: 创建专门的RAG指导Agent

创建一个新的Agent专门负责提供PMBOK指导：

```python
async def get_rag_guidance_agent(risk_data: dict, guidance_type: str = "risk_management") -> dict:
    """RAG指导Agent - 为风险项提供PMBOK指导"""
    try:
        guidance_results = []
        
        for risk in risk_data.get("risks", []):
            # 根据风险类型生成不同的查询
            if guidance_type == "risk_management":
                query = generate_risk_guidance_query(risk)
            elif guidance_type == "issue_management":
                query = generate_issue_guidance_query(risk)
            else:
                query = f"项目管理中如何处理{risk.get('risk_title', '')}"
            
            # 调用RAG系统
            rag_results = rag_system.search_pmbok_knowledge(query, top_k=3)
            
            # 生成指导摘要
            guidance_summary = generate_guidance_summary(rag_results)
            
            guidance_results.append({
                "risk_id": risk.get('risk_id'),
                "risk_title": risk.get('risk_title'),
                "risk_level": risk.get('risk_level'),
                "rag_query": query,
                "pmbok_guidance": rag_results,
                "guidance_summary": guidance_summary,
                "actionable_advice": extract_actionable_advice(rag_results)
            })
        
        return {
            "success": True,
            "data_type": "rag_guidance",
            "data_source": "PMBOK第七版中文版",
            "query_time": datetime.now().isoformat(),
            "guidance_type": guidance_type,
            "data": {
                "total_guidance_items": len(guidance_results),
                "guidance_items": guidance_results
            },
            "calculation_method": "基于PMBOK第七版的风险管理最佳实践",
            "data_fields": {
                "guidance_items": ["risk_id", "rag_query", "pmbok_guidance", "guidance_summary", "actionable_advice"]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取RAG指导失败: {str(e)}",
            "data_source": "PMBOK第七版中文版"
        }
```

### 方案3: 智能指导生成器

创建一个智能指导生成器，根据风险特征自动生成个性化指导：

```python
class IntelligentGuidanceGenerator:
    """智能指导生成器"""
    
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.risk_patterns = {
            "技术风险": ["技术不确定性", "技术难题", "技术选型"],
            "进度风险": ["进度延迟", "时间不够", "里程碑"],
            "成本风险": ["预算超支", "成本控制", "资金不足"],
            "质量风险": ["质量问题", "验收标准", "测试"],
            "团队风险": ["人员流失", "技能不足", "沟通问题"]
        }
    
    def generate_risk_guidance(self, risk: dict) -> dict:
        """为单个风险生成个性化指导"""
        risk_title = risk.get('risk_title', '')
        risk_level = risk.get('risk_level', '')
        risk_description = risk.get('description', '')
        
        # 1. 识别风险类型
        risk_type = self.identify_risk_type(risk_title, risk_description)
        
        # 2. 生成针对性查询
        query = self.generate_targeted_query(risk_type, risk_level, risk_title)
        
        # 3. 获取PMBOK指导
        rag_results = self.rag_system.search_pmbok_knowledge(query, top_k=3)
        
        # 4. 生成可执行的建议
        actionable_advice = self.generate_actionable_advice(rag_results, risk)
        
        return {
            "risk_id": risk.get('risk_id'),
            "risk_type": risk_type,
            "risk_level": risk_level,
            "rag_query": query,
            "pmbok_guidance": rag_results,
            "actionable_advice": actionable_advice,
            "priority_actions": self.extract_priority_actions(rag_results),
            "pmbok_references": [r['page_number'] for r in rag_results]
        }
    
    def identify_risk_type(self, title: str, description: str) -> str:
        """识别风险类型"""
        text = f"{title} {description}".lower()
        
        for risk_type, keywords in self.risk_patterns.items():
            if any(keyword in text for keyword in keywords):
                return risk_type
        
        return "一般风险"
    
    def generate_targeted_query(self, risk_type: str, risk_level: str, risk_title: str) -> str:
        """生成针对性查询"""
        queries = {
            "技术风险": f"如何处理{risk_level}级别的技术风险，特别是{risk_title}",
            "进度风险": f"项目进度风险应对策略，{risk_level}级别的时间管理",
            "成本风险": f"成本控制和预算管理，{risk_level}级别的财务风险",
            "质量风险": f"质量管理和风险控制，{risk_level}级别的质量保证",
            "团队风险": f"团队管理和沟通，{risk_level}级别的人力资源风险"
        }
        
        return queries.get(risk_type, f"项目管理中如何处理{risk_level}级别的{risk_title}")
    
    def generate_actionable_advice(self, rag_results: list, risk: dict) -> list:
        """生成可执行的建议"""
        advice = []
        
        for result in rag_results:
            content = result['content']
            
            # 提取关键建议
            if "应对" in content or "策略" in content:
                advice.append({
                    "type": "应对策略",
                    "content": extract_key_sentences(content, ["应对", "策略", "方法"]),
                    "source_page": result['page_number']
                })
            
            if "预防" in content or "识别" in content:
                advice.append({
                    "type": "预防措施",
                    "content": extract_key_sentences(content, ["预防", "识别", "监控"]),
                    "source_page": result['page_number']
                })
        
        return advice
```

## 🚀 集成实现

### 1. 修改现有数据Agent

在`simple_app.py`中修改`get_risk_analysis_data`函数：

```python
async def get_risk_analysis_data(db_data: dict, query_params: dict = None) -> dict:
    """获取风险分析数据（集成RAG指导）"""
    try:
        # 原有逻辑...
        risks = db_data.get('risks', [])
        # ... 现有代码 ...
        
        # 新增：集成RAG指导
        rag_guidance = []
        for risk in project_risks:
            guidance = await generate_risk_guidance(risk)
            rag_guidance.append(guidance)
        
        return {
            "success": True,
            "data_type": "risk_analysis",
            "data_source": "industry_standard_database.json",
            "query_time": datetime.now().isoformat(),
            "data": {
                "total_risks": len(project_risks),
                "level_breakdown": level_stats,
                "risks": project_risks,
                "rag_guidance": rag_guidance  # 新增RAG指导
            },
            "calculation_method": "按风险等级分组统计 + PMBOK指导集成",
            "rag_integration": {
                "enabled": True,
                "guidance_count": len(rag_guidance),
                "pmbok_source": "PMBOK第七版中文版"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取风险分析数据失败: {str(e)}",
            "data_source": "industry_standard_database.json"
        }
```

### 2. 添加RAG指导生成函数

```python
async def generate_risk_guidance(risk: dict) -> dict:
    """为单个风险生成RAG指导"""
    try:
        # 初始化RAG系统
        from app.services.rag_system import rag_system
        
        # 构建查询
        risk_title = risk.get('risk_title', '')
        risk_level = risk.get('risk_level', '')
        query = f"如何处理{risk_level}级别的{risk_title}风险"
        
        # 搜索PMBOK指导
        rag_results = rag_system.search_pmbok_knowledge(query, top_k=3)
        
        # 验证页码引用
        claimed_pages = [r['page_number'] for r in rag_results]
        validated_pages = rag_system.validate_page_references(claimed_pages, rag_results)
        
        return {
            "risk_id": risk.get('risk_id'),
            "risk_title": risk_title,
            "risk_level": risk_level,
            "rag_query": query,
            "pmbok_guidance": rag_results,
            "validated_pages": validated_pages,
            "guidance_summary": generate_guidance_summary(rag_results),
            "actionable_advice": extract_actionable_advice(rag_results)
        }
        
    except Exception as e:
        return {
            "risk_id": risk.get('risk_id'),
            "error": f"生成RAG指导失败: {str(e)}"
        }

def generate_guidance_summary(rag_results: list) -> str:
    """生成指导摘要"""
    if not rag_results:
        return "暂无相关PMBOK指导"
    
    # 提取关键信息
    key_points = []
    for result in rag_results:
        content = result['content']
        # 提取关键句子
        sentences = content.split('。')
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:2]
        key_points.extend(key_sentences)
    
    return "。".join(key_points[:3]) + "。"

def extract_actionable_advice(rag_results: list) -> list:
    """提取可执行的建议"""
    advice = []
    
    for result in rag_results:
        content = result['content']
        
        # 查找包含行动建议的内容
        if any(keyword in content for keyword in ["应该", "建议", "需要", "可以", "应当"]):
            advice.append({
                "advice": content[:200] + "..." if len(content) > 200 else content,
                "source_page": result['page_number'],
                "similarity": result['similarity']
            })
    
    return advice
```

### 3. 更新系统提示词

在系统提示词中添加RAG指导的说明：

```python
system_prompt = f"""你是一个智能项目管理助手，专门帮助用户管理项目。你有以下能力：

1. 意图分析：理解用户想要了解什么
2. 数据Agent调用：通过专门的数据Agent获取准确的数据
3. RAG指导集成：为风险项和问题提供PMBOK专业指导
4. 结果输出：将数据转换为用户友好的回答，并提供数据来源和计算过程

## RAG指导功能说明

当调用risk_analysis数据Agent时，系统会自动：
1. 分析项目中的风险项
2. 为每个风险项搜索PMBOK相关指导
3. 提供可执行的建议和应对策略
4. 包含页码引用，确保指导的可追溯性

## 数据Agent返回格式说明

风险分析数据现在包含以下字段：
- success：是否成功
- data_type：数据类型
- data：具体数据（包含risks和rag_guidance）
- rag_integration：RAG集成信息
- calculation_method：计算方法

其中rag_guidance包含：
- risk_id：风险ID
- rag_query：RAG查询
- pmbok_guidance：PMBOK指导内容
- validated_pages：验证后的页码引用
- guidance_summary：指导摘要
- actionable_advice：可执行建议

## 回答要求

当展示风险分析结果时，必须：
1. 明确说明数据来源
2. 提供详细的风险统计
3. 为每个风险项提供PMBOK指导建议
4. 包含页码引用，确保可追溯性
5. 提供可执行的应对策略

当前项目数据上下文：
{project_context}

请根据用户的问题，分析意图，调用相应的数据Agent，并基于返回的数据提供详细的回答。
"""
```

## 📊 预期效果

### 用户查询示例
```
用户：分析项目风险
```

### 系统响应示例
```
## 项目风险分析报告

### 📊 风险统计
- 总风险数：5个
- 高风险：2个
- 中风险：2个  
- 低风险：1个

### ⚠️ 高风险项及PMBOK指导

#### 1. 技术选型风险
**风险描述**：新技术框架学习成本高，可能影响开发进度

**PMBOK指导**：
- 建议采用渐进式技术引入策略，先在小模块中验证技术可行性
- 建立技术培训计划，确保团队具备必要的技术能力
- 设置技术风险缓冲时间，预留20%的额外开发时间

**参考页码**：第244页（不确定性绩效域）

#### 2. 需求变更风险  
**风险描述**：客户需求频繁变更，可能导致项目范围蔓延

**PMBOK指导**：
- 建立需求变更控制流程，所有变更必须经过正式审批
- 实施敏捷开发方法，通过短迭代快速响应变更
- 与客户建立定期沟通机制，确保需求理解一致

**参考页码**：第217页（整体项目风险）

### 🎯 可执行建议
1. 立即启动技术培训计划
2. 建立需求变更控制委员会
3. 设置项目风险监控机制
4. 定期进行风险回顾和评估

**数据来源**：industry_standard_database.json + PMBOK第七版中文版
```

## 🔧 实施步骤

1. **第一步**：修改`get_risk_analysis_data`函数，集成RAG指导
2. **第二步**：添加RAG指导生成函数
3. **第三步**：更新系统提示词，说明RAG指导功能
4. **第四步**：测试集成效果
5. **第五步**：扩展到其他数据Agent（如问题分析）

这个方案可以让您的系统在发现风险或问题时，自动提供PMBOK的专业指导，大大提升系统的实用价值！

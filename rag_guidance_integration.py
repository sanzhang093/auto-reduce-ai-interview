#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG指导集成实现示例
将RAG系统与风险分析Agent集成，提供PMBOK专业指导
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from test_rag_direct import SimpleRAGSystem

class RAGGuidanceIntegration:
    """RAG指导集成类"""
    
    def __init__(self):
        """初始化RAG指导集成"""
        self.rag_system = SimpleRAGSystem()
        self.rag_system.load_pmbok_documents()
        print("✅ RAG指导集成初始化完成")
    
    async def get_risk_analysis_with_rag_guidance(self, db_data: dict, query_params: dict = None) -> dict:
        """获取风险分析数据并集成RAG指导"""
        try:
            # 1. 获取原有风险分析数据
            risk_data = await self.get_risk_analysis_data(db_data, query_params)
            
            if not risk_data.get("success"):
                return risk_data
            
            # 2. 为每个风险项生成RAG指导
            risks = risk_data["data"]["risks"]
            rag_guidance = []
            
            print(f"🔍 为{len(risks)}个风险项生成RAG指导...")
            
            for i, risk in enumerate(risks, 1):
                print(f"   处理风险 {i}/{len(risks)}: {risk.get('risk_title', '未知风险')}")
                
                # 生成RAG指导
                guidance = await self.generate_risk_guidance(risk)
                rag_guidance.append(guidance)
            
            # 3. 返回增强的数据结构
            risk_data["data"]["rag_guidance"] = rag_guidance
            risk_data["rag_integration"] = {
                "enabled": True,
                "guidance_count": len(rag_guidance),
                "pmbok_source": "PMBOK第七版中文版",
                "integration_time": datetime.now().isoformat()
            }
            
            print(f"✅ 成功为{len(rag_guidance)}个风险项生成RAG指导")
            return risk_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取风险分析数据失败: {str(e)}",
                "data_source": "industry_standard_database.json"
            }
    
    async def get_risk_analysis_data(self, db_data: dict, query_params: dict = None) -> dict:
        """获取风险分析数据（原有逻辑）"""
        try:
            risks = db_data.get('risks', [])
            
            # 如果指定了项目ID，只返回该项目的风险
            if query_params and query_params.get('project_id'):
                project_id = query_params['project_id']
                project_risks = [risk for risk in risks if risk.get('project_id') == project_id]
            else:
                project_risks = risks
            
            # 按风险等级统计
            level_stats = {}
            for risk in project_risks:
                level = risk.get('risk_level', '未知')
                if level not in level_stats:
                    level_stats[level] = {'count': 0, 'risks': []}
                level_stats[level]['count'] += 1
                level_stats[level]['risks'].append(risk)
            
            return {
                "success": True,
                "data_type": "risk_analysis",
                "data_source": "industry_standard_database.json",
                "query_time": datetime.now().isoformat(),
                "project_id": query_params.get('project_id') if query_params else None,
                "data": {
                    "total_risks": len(project_risks),
                    "level_breakdown": level_stats,
                    "risks": project_risks
                },
                "calculation_method": "按风险等级分组统计",
                "data_fields": {
                    "risks": ["risk_id", "risk_title", "risk_level", "probability", "impact", "description", "mitigation_plan", "project_id"]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取风险分析数据失败: {str(e)}",
                "data_source": "industry_standard_database.json"
            }
    
    async def generate_risk_guidance(self, risk: dict) -> dict:
        """为单个风险生成RAG指导"""
        try:
            risk_title = risk.get('risk_title', '')
            risk_level = risk.get('risk_level', '')
            risk_description = risk.get('description', '')
            
            # 1. 识别风险类型
            risk_type = self.identify_risk_type(risk_title, risk_description)
            
            # 2. 生成针对性查询
            query = self.generate_targeted_query(risk_type, risk_level, risk_title)
            
            # 3. 搜索PMBOK指导
            rag_results = self.rag_system.search_pmbok_knowledge(query, top_k=3)
            
            # 4. 验证页码引用
            claimed_pages = [r['page_number'] for r in rag_results]
            validated_pages = self.rag_system.validate_page_references(claimed_pages, rag_results)
            
            # 5. 生成指导摘要和可执行建议
            guidance_summary = self.generate_guidance_summary(rag_results)
            actionable_advice = self.extract_actionable_advice(rag_results)
            
            return {
                "risk_id": risk.get('risk_id'),
                "risk_title": risk_title,
                "risk_level": risk_level,
                "risk_type": risk_type,
                "rag_query": query,
                "pmbok_guidance": rag_results,
                "validated_pages": validated_pages,
                "guidance_summary": guidance_summary,
                "actionable_advice": actionable_advice,
                "priority_actions": self.extract_priority_actions(rag_results)
            }
            
        except Exception as e:
            return {
                "risk_id": risk.get('risk_id'),
                "error": f"生成RAG指导失败: {str(e)}"
            }
    
    def identify_risk_type(self, title: str, description: str) -> str:
        """识别风险类型"""
        text = f"{title} {description}".lower()
        
        risk_patterns = {
            "技术风险": ["技术", "开发", "代码", "系统", "架构", "框架"],
            "进度风险": ["进度", "时间", "延迟", "延期", "里程碑", "deadline"],
            "成本风险": ["成本", "预算", "费用", "资金", "超支"],
            "质量风险": ["质量", "测试", "bug", "缺陷", "验收"],
            "团队风险": ["人员", "团队", "技能", "沟通", "流失"],
            "需求风险": ["需求", "变更", "范围", "客户", "用户"]
        }
        
        for risk_type, keywords in risk_patterns.items():
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
            "团队风险": f"团队管理和沟通，{risk_level}级别的人力资源风险",
            "需求风险": f"需求管理和变更控制，{risk_level}级别的范围管理"
        }
        
        return queries.get(risk_type, f"项目管理中如何处理{risk_level}级别的{risk_title}")
    
    def generate_guidance_summary(self, rag_results: list) -> str:
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
        
        summary = "。".join(key_points[:3])
        return summary + "。" if summary else "暂无相关PMBOK指导"
    
    def extract_actionable_advice(self, rag_results: list) -> list:
        """提取可执行的建议"""
        advice = []
        
        for result in rag_results:
            content = result['content']
            
            # 查找包含行动建议的内容
            if any(keyword in content for keyword in ["应该", "建议", "需要", "可以", "应当", "采取", "实施"]):
                advice.append({
                    "advice": content[:200] + "..." if len(content) > 200 else content,
                    "source_page": result['page_number'],
                    "similarity": result['similarity']
                })
        
        return advice[:3]  # 最多返回3条建议
    
    def extract_priority_actions(self, rag_results: list) -> list:
        """提取优先行动项"""
        actions = []
        
        for result in rag_results:
            content = result['content']
            
            # 查找包含具体行动的内容
            if any(keyword in content for keyword in ["立即", "首先", "优先", "紧急", "关键"]):
                actions.append({
                    "action": content[:150] + "..." if len(content) > 150 else content,
                    "source_page": result['page_number'],
                    "priority": "高" if "立即" in content or "紧急" in content else "中"
                })
        
        return actions[:2]  # 最多返回2个优先行动

def format_risk_analysis_with_rag_guidance(risk_data: dict) -> str:
    """格式化风险分析结果（包含RAG指导）"""
    if not risk_data.get("success"):
        return f"❌ 风险分析失败: {risk_data.get('error', '未知错误')}"
    
    data = risk_data["data"]
    rag_guidance = data.get("rag_guidance", [])
    
    # 构建报告
    report = []
    report.append("## 📊 项目风险分析报告（含PMBOK指导）")
    report.append("")
    
    # 风险统计
    report.append("### 📈 风险统计")
    report.append(f"- 总风险数：{data['total_risks']}个")
    
    level_breakdown = data.get("level_breakdown", {})
    for level, stats in level_breakdown.items():
        report.append(f"- {level}风险：{stats['count']}个")
    
    report.append("")
    
    # RAG指导信息
    if rag_guidance:
        report.append("### 🎯 PMBOK专业指导")
        report.append(f"- 已为{len(rag_guidance)}个风险项提供PMBOK指导")
        report.append(f"- 数据来源：PMBOK第七版中文版")
        report.append("")
        
        # 详细指导
        for i, guidance in enumerate(rag_guidance, 1):
            if "error" in guidance:
                continue
                
            report.append(f"#### {i}. {guidance['risk_title']}")
            report.append(f"**风险等级**：{guidance['risk_level']}")
            report.append(f"**风险类型**：{guidance['risk_type']}")
            report.append("")
            
            # PMBOK指导摘要
            if guidance.get('guidance_summary'):
                report.append("**PMBOK指导摘要**：")
                report.append(f"{guidance['guidance_summary']}")
                report.append("")
            
            # 可执行建议
            if guidance.get('actionable_advice'):
                report.append("**可执行建议**：")
                for j, advice in enumerate(guidance['actionable_advice'], 1):
                    report.append(f"{j}. {advice['advice']}")
                    report.append(f"   （参考页码：{advice['source_page']}）")
                report.append("")
            
            # 优先行动
            if guidance.get('priority_actions'):
                report.append("**优先行动**：")
                for action in guidance['priority_actions']:
                    report.append(f"- {action['action']}")
                report.append("")
            
            # 页码引用
            if guidance.get('validated_pages'):
                report.append(f"**PMBOK参考页码**：{', '.join(map(str, guidance['validated_pages']))}")
                report.append("")
            
            report.append("---")
            report.append("")
    
    # 数据来源
    report.append("### 📋 数据来源")
    report.append(f"- 风险数据：{risk_data['data_source']}")
    report.append(f"- PMBOK指导：PMBOK第七版中文版")
    report.append(f"- 分析时间：{risk_data['query_time']}")
    
    return "\n".join(report)

async def test_rag_guidance_integration():
    """测试RAG指导集成功能"""
    print("🚀 测试RAG指导集成功能...")
    
    # 初始化集成系统
    integration = RAGGuidanceIntegration()
    
    # 读取项目数据
    db_path = "industry_standard_database_extended.json"
    if not os.path.exists(db_path):
        print(f"❌ 数据文件不存在: {db_path}")
        return
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    # 测试风险分析（集成RAG指导）
    print("\n🔍 执行风险分析（集成RAG指导）...")
    risk_data = await integration.get_risk_analysis_with_rag_guidance(db_data)
    
    if risk_data.get("success"):
        print("✅ 风险分析成功")
        
        # 格式化输出
        formatted_report = format_risk_analysis_with_rag_guidance(risk_data)
        print("\n" + "="*80)
        print(formatted_report)
        print("="*80)
        
        # 保存报告
        with open("risk_analysis_with_rag_guidance.md", "w", encoding="utf-8") as f:
            f.write(formatted_report)
        print("\n💾 报告已保存到: risk_analysis_with_rag_guidance.md")
        
    else:
        print(f"❌ 风险分析失败: {risk_data.get('error')}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_rag_guidance_integration())
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

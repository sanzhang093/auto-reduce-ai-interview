#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专家建议功能调试测试
"""

import asyncio
import json
import os
from datetime import datetime

async def test_expert_advice():
    """测试专家建议功能"""
    print("🔍 开始测试专家建议功能...")
    
    try:
        # 1. 测试RAG系统初始化
        print("\n1. 测试RAG系统初始化...")
        from rag_guidance_integration import RAGGuidanceIntegration
        rag_integration = RAGGuidanceIntegration()
        print("✅ RAG系统初始化成功")
        
        # 2. 测试数据加载
        print("\n2. 测试数据加载...")
        db_path = "data/industry_standard_database_extended.json"
        if not os.path.exists(db_path):
            db_path = "industry_standard_database_extended.json"
        
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return
        
        with open(db_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        risks = db_data.get('risks', [])
        print(f"✅ 成功加载{len(risks)}个风险项")
        
        # 3. 测试单个风险指导生成
        print("\n3. 测试单个风险指导生成...")
        if risks:
            test_risk = risks[0]
            print(f"   测试风险: {test_risk.get('risk_title', '未知')}")
            
            # 设置超时
            try:
                guidance = await asyncio.wait_for(
                    rag_integration.generate_risk_guidance(test_risk),
                    timeout=30.0
                )
                print("✅ 风险指导生成成功")
                print(f"   指导摘要: {guidance.get('guidance_summary', '无')[:100]}...")
            except asyncio.TimeoutError:
                print("❌ 风险指导生成超时（30秒）")
            except Exception as e:
                print(f"❌ 风险指导生成失败: {str(e)}")
        
        # 4. 测试完整风险分析
        print("\n4. 测试完整风险分析...")
        try:
            result = await asyncio.wait_for(
                rag_integration.get_risk_analysis_with_rag_guidance(
                    db_data, 
                    {"include_rag_guidance": True}
                ),
                timeout=60.0
            )
            
            if result.get("success"):
                print("✅ 完整风险分析成功")
                rag_guidance = result.get("data", {}).get("rag_guidance", [])
                print(f"   生成了{len(rag_guidance)}个RAG指导")
            else:
                print(f"❌ 完整风险分析失败: {result.get('error')}")
                
        except asyncio.TimeoutError:
            print("❌ 完整风险分析超时（60秒）")
        except Exception as e:
            print(f"❌ 完整风险分析失败: {str(e)}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_expert_advice())

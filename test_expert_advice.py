#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试专家建议功能
"""

import requests
import json

def test_expert_advice():
    """测试专家建议功能"""
    print("🎯 测试专家建议功能...")
    
    # API端点
    url = "http://localhost:8000/api/v1/auto-reduce/intelligent-chat/chat"
    
    # 测试数据
    test_cases = [
        {
            "message": "获取专家建议",
            "session_id": "test_expert_advice_1"
        },
        {
            "message": "扫描项目风险并提供专家建议",
            "session_id": "test_expert_advice_2"
        },
        {
            "message": "智能管理系统开发项目的专业指导",
            "session_id": "test_expert_advice_3"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['message']}")
        
        try:
            response = requests.post(url, json=test_case, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 响应状态: {data.get('code', 'N/A')}")
                
                if data.get('code') == 200 and data.get('data', {}).get('response'):
                    response_text = data['data']['response']
                    print(f"📝 响应长度: {len(response_text)} 字符")
                    print(f"📄 响应预览: {response_text[:200]}...")
                    
                    # 检查是否包含专家建议相关内容
                    if any(keyword in response_text for keyword in ['PMBOK', '专家建议', '专业指导', '页码', '风险指导']):
                        print("🎯 包含专家建议内容")
                    else:
                        print("⚠️ 未检测到专家建议内容")
                else:
                    print(f"❌ 响应错误: {data.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"错误详情: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {str(e)}")
        except Exception as e:
            print(f"❌ 其他错误: {str(e)}")
        
        print("-" * 50)

async def test_rag_guidance_integration():
    """测试RAG指导集成"""
    print("\n🔍 测试RAG指导集成...")
    
    try:
        from rag_guidance_integration import RAGGuidanceIntegration
        import json
        
        # 初始化RAG指导集成
        integration = RAGGuidanceIntegration()
        
        # 读取测试数据
        with open('industry_standard_database_extended.json', 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        # 测试风险分析+RAG指导
        print("📊 执行风险分析+RAG指导...")
        result = await integration.get_risk_analysis_with_rag_guidance(db_data)
        
        if result.get("success"):
            print("✅ RAG指导集成成功")
            print(f"📈 风险数量: {result['data']['total_risks']}")
            print(f"🎯 RAG指导数量: {len(result['data'].get('rag_guidance', []))}")
            
            if result.get('rag_integration', {}).get('enabled'):
                print("✅ RAG集成已启用")
                print(f"📚 PMBOK来源: {result['rag_integration']['pmbok_source']}")
            else:
                print("⚠️ RAG集成未启用")
        else:
            print(f"❌ RAG指导集成失败: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ RAG指导集成测试失败: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    # 测试API接口
    test_expert_advice()
    
    # 测试RAG指导集成
    try:
        asyncio.run(test_rag_guidance_integration())
    except Exception as e:
        print(f"❌ 异步测试失败: {str(e)}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG系统对风险管理问题的检索效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_rag_direct import SimpleRAGSystem

def test_risk_management_query():
    """测试风险管理相关查询"""
    print("🔍 测试RAG系统风险管理检索功能...")
    
    # 创建RAG系统实例
    rag = SimpleRAGSystem()
    
    # 加载PMBOK文档
    print("\n📚 加载PMBOK文档...")
    success = rag.load_pmbok_documents()
    if not success:
        print("❌ 文档加载失败")
        return
    
    print(f"✅ 成功加载{len(rag.pmbok_documents)}个PMBOK文档块")
    
    # 测试查询
    query = "研发项目出现结果不可控的风险应如何做好应对"
    print(f"\n🔎 查询: '{query}'")
    print("=" * 80)
    
    # 执行检索
    results = rag.search_pmbok_knowledge(query, top_k=5)
    
    if results:
        print(f"✅ 找到{len(results)}个相关结果:")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"📄 结果 {i}:")
            print(f"   相似度: {result['similarity']:.3f}")
            print(f"   页码: {result['page_number']}")
            print(f"   章节: {result['section']}")
            print(f"   来源: {result['source']}")
            print(f"   内容长度: {len(result['content'])}字符")
            print()
            print("📝 内容预览:")
            print("   " + "="*60)
            # 显示内容的前500字符
            content_preview = result['content'][:500]
            # 按行显示，每行前面加缩进
            for line in content_preview.split('\n'):
                print(f"   {line}")
            if len(result['content']) > 500:
                print("   ...")
            print("   " + "="*60)
            print()
    else:
        print("❌ 未找到相关结果")
    
    # 测试相关查询
    print("\n🔍 测试相关查询:")
    related_queries = [
        "风险管理的基本原则",
        "不确定性绩效域",
        "风险应对策略",
        "项目风险识别",
        "风险缓解措施"
    ]
    
    for related_query in related_queries:
        print(f"\n🔎 相关查询: '{related_query}'")
        related_results = rag.search_pmbok_knowledge(related_query, top_k=3)
        
        if related_results:
            print(f"✅ 找到{len(related_results)}个相关结果:")
            for j, result in enumerate(related_results, 1):
                print(f"   {j}. {result['section']} (相似度: {result['similarity']:.3f}, 页码: {result['page_number']})")
        else:
            print("❌ 未找到相关结果")
    
    # 测试页码验证
    print(f"\n✅ 测试页码验证功能:")
    claimed_pages = [1, 5, 10, 15, 20, 999]  # 包含一些可能不存在的页码
    validated_pages = rag.validate_page_references(claimed_pages, results)
    print(f"原始页码: {claimed_pages}")
    print(f"验证后页码: {validated_pages}")
    
    # 分析检索质量
    print(f"\n📊 检索质量分析:")
    if results:
        high_similarity = [r for r in results if r['similarity'] > 0.7]
        medium_similarity = [r for r in results if 0.5 <= r['similarity'] <= 0.7]
        low_similarity = [r for r in results if r['similarity'] < 0.5]
        
        print(f"   高相似度结果 (>0.7): {len(high_similarity)}个")
        print(f"   中等相似度结果 (0.5-0.7): {len(medium_similarity)}个")
        print(f"   低相似度结果 (<0.5): {len(low_similarity)}个")
        
        if high_similarity:
            print(f"   最佳匹配: {high_similarity[0]['section']} (相似度: {high_similarity[0]['similarity']:.3f})")
    
    print(f"\n🎉 RAG系统风险管理检索测试完成！")

if __name__ == "__main__":
    try:
        test_risk_management_query()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()





#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的PMBOK RAG系统
包含页码验证和父页面检索功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_system import RAGSystem, PMBOKDocument
import json

def test_pmbok_rag_system():
    """测试PMBOK RAG系统"""
    print("🚀 开始测试增强后的PMBOK RAG系统...")
    
    # 创建RAG系统实例
    rag = RAGSystem()
    
    # 1. 加载PMBOK文档
    print("\n📚 步骤1: 加载PMBOK文档...")
    success = rag.load_pmbok_documents()
    if success:
        print(f"✅ 成功加载PMBOK文档，共{len(rag.pmbok_documents)}个文档块")
        
        # 显示前几个文档块的信息
        print("\n📋 文档块信息预览:")
        for i, doc in enumerate(rag.pmbok_documents[:3]):
            print(f"  {i+1}. 章节: {doc.section}")
            print(f"     页码: {doc.page_number}")
            print(f"     内容长度: {len(doc.content)}字符")
            print(f"     内容预览: {doc.content[:100]}...")
            print()
    else:
        print("❌ 加载PMBOK文档失败")
        return
    
    # 2. 测试知识检索
    print("\n🔍 步骤2: 测试知识检索...")
    test_queries = [
        "项目管理的基本原则是什么？",
        "什么是项目绩效域？",
        "敏捷项目管理的特点",
        "项目干系人管理",
        "风险管理的最佳实践"
    ]
    
    for query in test_queries:
        print(f"\n🔎 查询: '{query}'")
        results = rag.search_pmbok_knowledge(query, top_k=3)
        
        if results:
            print(f"✅ 找到{len(results)}个相关结果:")
            for i, result in enumerate(results):
                print(f"  {i+1}. 相似度: {result['similarity']:.3f}")
                print(f"     页码: {result['page_number']}")
                print(f"     章节: {result['section']}")
                print(f"     内容预览: {result['content'][:150]}...")
                print()
        else:
            print("❌ 未找到相关结果")
    
    # 3. 测试页码验证功能
    print("\n✅ 步骤3: 测试页码验证功能...")
    
    # 模拟LLM声称的页码
    claimed_pages = [1, 5, 10, 15, 20]  # 一些页码
    search_results = rag.search_pmbok_knowledge("项目管理原则", top_k=5)
    
    print(f"📄 声称的页码: {claimed_pages}")
    print(f"📄 检索结果中的页码: {[r['page_number'] for r in search_results]}")
    
    # 验证页码引用
    validated_pages = rag.validate_page_references(claimed_pages, search_results)
    print(f"✅ 验证后的页码: {validated_pages}")
    
    # 4. 测试幻觉页码检测
    print("\n🎭 步骤4: 测试幻觉页码检测...")
    
    # 模拟包含幻觉页码的情况
    hallucinated_pages = [1, 999, 1000, 5]  # 包含不存在的页码
    print(f"📄 包含幻觉的页码: {hallucinated_pages}")
    
    validated_pages = rag.validate_page_references(hallucinated_pages, search_results)
    print(f"✅ 验证后的页码: {validated_pages}")
    
    # 5. 测试完整检索流程
    print("\n🔄 步骤5: 测试完整检索流程...")
    
    query = "项目管理的12项原则"
    print(f"🔎 查询: '{query}'")
    
    # 检索相关文档
    results = rag.search_pmbok_knowledge(query, top_k=3)
    
    if results:
        print(f"✅ 检索到{len(results)}个相关文档:")
        
        # 提取页码信息
        retrieved_pages = [r['page_number'] for r in results]
        print(f"📄 检索到的页码: {retrieved_pages}")
        
        # 模拟LLM生成的答案和页码引用
        llm_claimed_pages = [1, 2, 3, 999]  # 包含一个幻觉页码
        
        # 验证页码引用
        validated_pages = rag.validate_page_references(llm_claimed_pages, results)
        
        print(f"📝 LLM声称的页码: {llm_claimed_pages}")
        print(f"✅ 验证后的页码: {validated_pages}")
        
        # 生成最终答案格式
        print(f"\n📋 最终答案格式:")
        print(f"问题: {query}")
        print(f"答案: 基于PMBOK第七版，项目管理的12项原则包括...")
        print(f"引用页码: {validated_pages}")
        print(f"来源: PMBOK第七版中文版")
    
    print("\n🎉 PMBOK RAG系统测试完成！")

def test_embedding_performance():
    """测试嵌入性能"""
    print("\n⚡ 测试嵌入性能...")
    
    rag = RAGSystem()
    
    # 测试文本
    test_texts = [
        "项目管理的基本原则",
        "项目绩效域",
        "敏捷开发方法",
        "风险管理",
        "干系人管理"
    ]
    
    print("🔍 测试单个文本嵌入...")
    for text in test_texts:
        embedding = rag._generate_embedding(text)
        print(f"  '{text}' -> 向量维度: {len(embedding)}")
    
    print("\n🔍 测试批量文本嵌入...")
    embeddings = rag._generate_batch_embeddings(test_texts)
    print(f"  批量处理{len(test_texts)}个文本，生成{len(embeddings)}个嵌入向量")
    
    # 测试相似度计算
    print("\n🔍 测试相似度计算...")
    if len(embeddings) >= 2:
        similarity = rag._cosine_similarity(embeddings[0], embeddings[1])
        print(f"  '{test_texts[0]}' 与 '{test_texts[1]}' 的相似度: {similarity:.3f}")

if __name__ == "__main__":
    try:
        # 测试PMBOK RAG系统
        test_pmbok_rag_system()
        
        # 测试嵌入性能
        test_embedding_performance()
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

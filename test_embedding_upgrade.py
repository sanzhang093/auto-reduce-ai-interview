#!/usr/bin/env python3
"""
测试RAG系统升级后的向量化功能
"""
import os
import sys
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_system import RAGSystem, RAGDocument

def test_embedding_generation():
    """测试向量化生成功能"""
    print("=== 测试向量化生成功能 ===")
    
    # 初始化RAG系统
    rag_system = RAGSystem()
    
    # 测试文本
    test_texts = [
        "项目管理知识体系指南第七版介绍了12项项目管理原则",
        "干系人绩效域涉及与干系人相关的活动和功能",
        "敏捷开发方法强调迭代和增量交付",
        "风险管理是项目管理的重要组成部分"
    ]
    
    print(f"使用模型: {rag_system.embedding_model}")
    print(f"向量维度: {rag_system.embedding_dim}")
    print()
    
    # 测试单个向量化
    print("1. 测试单个文本向量化:")
    for i, text in enumerate(test_texts[:2], 1):
        print(f"   文本 {i}: {text[:30]}...")
        try:
            embedding = rag_system._generate_embedding(text)
            print(f"   向量维度: {len(embedding)}")
            print(f"   向量前5个值: {embedding[:5]}")
            print()
        except Exception as e:
            print(f"   错误: {str(e)}")
            print()
    
    # 测试批量向量化
    print("2. 测试批量文本向量化:")
    try:
        embeddings = rag_system._generate_batch_embeddings(test_texts)
        print(f"   批量处理 {len(test_texts)} 个文本")
        print(f"   生成 {len(embeddings)} 个向量")
        for i, embedding in enumerate(embeddings):
            print(f"   向量 {i+1} 维度: {len(embedding)}")
        print()
    except Exception as e:
        print(f"   错误: {str(e)}")
        print()

def test_rag_document_operations():
    """测试RAG文档操作"""
    print("=== 测试RAG文档操作 ===")
    
    rag_system = RAGSystem()
    
    # 创建测试文档
    test_doc = RAGDocument(
        doc_id="test_doc_001",
        title="测试文档：项目管理原则",
        content="项目管理知识体系指南第七版介绍了12项项目管理原则，包括成为勤勉、尊重和关心他人的管家，营造协作的项目团队环境等。",
        doc_type="knowledge",
        project_id="test_project",
        metadata={"source": "PMBOK第七版", "category": "项目管理原则"}
    )
    
    print("1. 添加文档到RAG系统:")
    try:
        success = rag_system.add_document(test_doc)
        print(f"   添加结果: {'成功' if success else '失败'}")
        print()
    except Exception as e:
        print(f"   错误: {str(e)}")
        print()
    
    # 测试文档搜索
    print("2. 测试文档搜索:")
    search_queries = [
        "项目管理原则",
        "干系人管理",
        "团队协作"
    ]
    
    for query in search_queries:
        try:
            results = rag_system.search_documents(query, top_k=3)
            print(f"   查询: '{query}'")
            print(f"   找到 {len(results)} 个相关文档")
            for i, result in enumerate(results, 1):
                print(f"     {i}. {result.title} (相似度: {result.relevance_score:.3f})")
            print()
        except Exception as e:
            print(f"   查询 '{query}' 错误: {str(e)}")
            print()

def test_similarity_calculation():
    """测试相似度计算"""
    print("=== 测试相似度计算 ===")
    
    rag_system = RAGSystem()
    
    # 测试文本对
    text_pairs = [
        ("项目管理", "项目管理工作"),
        ("风险管理", "风险控制"),
        ("敏捷开发", "传统瀑布模型"),
        ("干系人管理", "利益相关者管理")
    ]
    
    print("文本相似度测试:")
    for text1, text2 in text_pairs:
        try:
            # 生成向量
            vec1 = rag_system._generate_embedding(text1)
            vec2 = rag_system._generate_embedding(text2)
            
            # 计算相似度
            similarity = rag_system._cosine_similarity(vec1, vec2)
            
            print(f"   '{text1}' vs '{text2}': {similarity:.3f}")
        except Exception as e:
            print(f"   计算 '{text1}' vs '{text2}' 相似度时错误: {str(e)}")

def main():
    """主测试函数"""
    print("RAG系统向量化升级测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 测试向量化生成
        test_embedding_generation()
        
        # 测试RAG文档操作
        test_rag_document_operations()
        
        # 测试相似度计算
        test_similarity_calculation()
        
        print("=" * 50)
        print("测试完成！")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

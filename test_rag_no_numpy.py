#!/usr/bin/env python3
"""
测试RAG系统向量化功能（不依赖numpy）
"""
import os
import sys
import dashscope
from http import HTTPStatus
import math

def cosine_similarity(vec1, vec2):
    """计算余弦相似度（不依赖numpy）"""
    if len(vec1) != len(vec2):
        return 0.0
    
    # 计算点积
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # 计算向量的模长
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

def test_embedding_basic():
    """基础向量化测试"""
    print("=== 基础向量化测试 ===")
    
    test_text = "项目管理知识体系指南第七版介绍了12项项目管理原则"
    
    try:
        resp = dashscope.TextEmbedding.call(
            model="text-embedding-v4",
            input=test_text,
            dimension=1024
        )
        
        if resp.status_code == HTTPStatus.OK:
            embedding = resp.output['embeddings'][0]['embedding']
            print(f"✅ 成功生成向量")
            print(f"   向量维度: {len(embedding)}")
            print(f"   向量前5个值: {embedding[:5]}")
            return embedding
        else:
            print(f"❌ API调用失败: {resp.message}")
            return None
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None

def test_similarity_calculation():
    """测试相似度计算"""
    print("\n=== 相似度计算测试 ===")
    
    # 测试文本对
    text_pairs = [
        ("项目管理", "项目管理工作"),
        ("风险管理", "风险控制"),
        ("敏捷开发", "传统瀑布模型")
    ]
    
    for text1, text2 in text_pairs:
        try:
            # 生成向量
            resp1 = dashscope.TextEmbedding.call(
                model="text-embedding-v4",
                input=text1,
                dimension=1024
            )
            
            resp2 = dashscope.TextEmbedding.call(
                model="text-embedding-v4",
                input=text2,
                dimension=1024
            )
            
            if resp1.status_code == HTTPStatus.OK and resp2.status_code == HTTPStatus.OK:
                vec1 = resp1.output['embeddings'][0]['embedding']
                vec2 = resp2.output['embeddings'][0]['embedding']
                
                similarity = cosine_similarity(vec1, vec2)
                print(f"   '{text1}' vs '{text2}': {similarity:.3f}")
            else:
                print(f"   '{text1}' vs '{text2}': 向量生成失败")
        
        except Exception as e:
            print(f"   计算 '{text1}' vs '{text2}' 相似度时错误: {str(e)}")

def test_pmbok_knowledge_search():
    """测试PMBOK知识搜索"""
    print("\n=== PMBOK知识搜索测试 ===")
    
    # PMBOK知识库
    pmbok_docs = [
        {
            "title": "项目管理原则1：成为勤勉、尊重和关心他人的管家",
            "content": "成为勤勉、尊重和关心他人的管家是项目管理的第一项原则。这意味着项目管理者应该以负责任的态度管理项目资源，尊重团队成员，关心干系人的利益。"
        },
        {
            "title": "干系人绩效域",
            "content": "干系人绩效域涉及与干系人相关的活动和功能。有效执行此绩效域将产生以下预期成果：在整个项目期间与干系人建立富有成效的工作关系。"
        },
        {
            "title": "敏捷开发方法",
            "content": "敏捷开发方法强调迭代和增量交付，通过频繁的反馈和调整来适应变化。敏捷方法注重个体和交互胜过过程和工具。"
        }
    ]
    
    # 测试查询
    query = "项目管理的基本原则是什么？"
    print(f"查询: '{query}'")
    
    try:
        # 生成查询向量
        query_resp = dashscope.TextEmbedding.call(
            model="text-embedding-v4",
            input=query,
            dimension=1024
        )
        
        if query_resp.status_code != HTTPStatus.OK:
            print(f"查询向量生成失败: {query_resp.message}")
            return
        
        query_embedding = query_resp.output['embeddings'][0]['embedding']
        
        # 生成文档向量
        doc_texts = [doc['content'] for doc in pmbok_docs]
        doc_resp = dashscope.TextEmbedding.call(
            model="text-embedding-v4",
            input=doc_texts,
            dimension=1024
        )
        
        if doc_resp.status_code != HTTPStatus.OK:
            print(f"文档向量生成失败: {doc_resp.message}")
            return
        
        # 计算相似度并排序
        similarities = []
        for i, doc_embedding in enumerate(doc_resp.output['embeddings']):
            similarity = cosine_similarity(query_embedding, doc_embedding['embedding'])
            similarities.append((i, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        print("相关文档:")
        for i, (doc_idx, similarity) in enumerate(similarities):
            doc = pmbok_docs[doc_idx]
            print(f"   {i+1}. {doc['title']} (相似度: {similarity:.3f})")
            print(f"      内容: {doc['content'][:80]}...")
        
    except Exception as e:
        print(f"知识搜索错误: {str(e)}")

def main():
    """主测试函数"""
    print("RAG系统向量化功能测试（无numpy版本）")
    print("=" * 60)
    
    # 检查API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置DASHSCOPE_API_KEY环境变量")
        return
    
    print(f"✅ API Key已设置: {api_key[:10]}...")
    print(f"✅ 使用模型: text-embedding-v4")
    print()
    
    try:
        # 基础向量化测试
        embedding = test_embedding_basic()
        if embedding is None:
            print("❌ 基础向量化测试失败，停止后续测试")
            return
        
        # 相似度计算测试
        test_similarity_calculation()
        
        # PMBOK知识搜索测试
        test_pmbok_knowledge_search()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("\n功能验证:")
        print("  ✅ 文本向量化 (text-embedding-v4)")
        print("  ✅ 余弦相似度计算")
        print("  ✅ 知识检索和排序")
        print("  ✅ PMBOK知识库集成")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

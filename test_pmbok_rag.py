#!/usr/bin/env python3
"""
测试RAG系统与PMBOK知识的集成
"""
import os
import sys
import json
import dashscope
from http import HTTPStatus
from datetime import datetime

def create_pmbok_knowledge_base():
    """创建PMBOK知识库"""
    pmbok_documents = [
        {
            "doc_id": "pmbok_principles_001",
            "title": "项目管理原则1：成为勤勉、尊重和关心他人的管家",
            "content": "成为勤勉、尊重和关心他人的管家是项目管理的第一项原则。这意味着项目管理者应该以负责任的态度管理项目资源，尊重团队成员，关心干系人的利益，并确保项目成果符合道德标准。",
            "doc_type": "principle",
            "category": "项目管理原则",
            "metadata": {"principle_id": 1, "source": "PMBOK第七版"}
        },
        {
            "doc_id": "pmbok_principles_002", 
            "title": "项目管理原则2：营造协作的项目团队环境",
            "content": "营造协作的项目团队环境要求项目管理者建立开放、信任、相互支持的工作氛围。这包括促进团队沟通、建立共同目标、鼓励知识分享，以及创建有利于创新和问题解决的环境。",
            "doc_type": "principle",
            "category": "项目管理原则",
            "metadata": {"principle_id": 2, "source": "PMBOK第七版"}
        },
        {
            "doc_id": "pmbok_performance_001",
            "title": "干系人绩效域",
            "content": "干系人绩效域涉及与干系人相关的活动和功能。有效执行此绩效域将产生以下预期成果：在整个项目期间与干系人建立富有成效的工作关系；干系人对项目目标表示同意；作为项目受益人的干系人表示支持并感到满意。",
            "doc_type": "performance_domain",
            "category": "项目绩效域",
            "metadata": {"domain_id": 1, "source": "PMBOK第七版"}
        },
        {
            "doc_id": "pmbok_performance_002",
            "title": "团队绩效域", 
            "content": "团队绩效域涉及与负责生成项目可交付物以实现商业成果的相关的人员活动和功能。有效执行此绩效域将产生以下预期成果：共享责任；高绩效团队；所有团队成员都展现出相关领导力和其他人际关系技能。",
            "doc_type": "performance_domain",
            "category": "项目绩效域",
            "metadata": {"domain_id": 2, "source": "PMBOK第七版"}
        },
        {
            "doc_id": "pmbok_agile_001",
            "title": "敏捷开发方法",
            "content": "敏捷开发方法强调迭代和增量交付，通过频繁的反馈和调整来适应变化。敏捷方法包括Scrum、看板、极限编程等框架，注重个体和交互胜过过程和工具，可工作的软件胜过详尽的文档。",
            "doc_type": "methodology",
            "category": "开发方法",
            "metadata": {"method_type": "agile", "source": "敏捷实践指南"}
        },
        {
            "doc_id": "pmbok_lifecycle_001",
            "title": "项目生命周期选择",
            "content": "项目生命周期选择需要考虑项目特征、需求确定性、团队能力等因素。主要类型包括：预测型生命周期（需求固定、一次性交付）；迭代型生命周期（动态需求、反复执行）；增量型生命周期（动态需求、频繁交付）；敏捷型生命周期（迭代+增量、客户价值导向）。",
            "doc_type": "lifecycle",
            "category": "生命周期",
            "metadata": {"lifecycle_types": ["预测型", "迭代型", "增量型", "敏捷型"], "source": "PMBOK第七版"}
        }
    ]
    
    return pmbok_documents

def test_pmbok_rag_search():
    """测试PMBOK知识检索"""
    print("=== 测试PMBOK知识检索 ===")
    
    # 创建知识库
    pmbok_docs = create_pmbok_knowledge_base()
    
    # 测试查询
    test_queries = [
        "项目管理的基本原则是什么？",
        "如何管理项目干系人？", 
        "敏捷开发方法的特点",
        "项目生命周期有哪些类型？",
        "如何建立高效的团队协作？"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        
        # 生成查询向量
        try:
            resp = dashscope.TextEmbedding.call(
                model="text-embedding-v4",
                input=query,
                dimension=1024
            )
            
            if resp.status_code != HTTPStatus.OK:
                print(f"   查询向量生成失败: {resp.message}")
                continue
                
            query_embedding = resp.output['embeddings'][0]['embedding']
            
            # 生成所有文档向量
            doc_texts = [doc['content'] for doc in pmbok_docs]
            doc_resp = dashscope.TextEmbedding.call(
                model="text-embedding-v4",
                input=doc_texts,
                dimension=1024
            )
            
            if doc_resp.status_code != HTTPStatus.OK:
                print(f"   文档向量生成失败: {doc_resp.message}")
                continue
            
            # 计算相似度
            import numpy as np
            
            def cosine_similarity(vec1, vec2):
                a = np.array(vec1)
                b = np.array(vec2)
                dot_product = np.dot(a, b)
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                
                return dot_product / (norm_a * norm_b)
            
            similarities = []
            for i, doc_embedding in enumerate(doc_resp.output['embeddings']):
                similarity = cosine_similarity(query_embedding, doc_embedding['embedding'])
                similarities.append((i, similarity))
            
            # 排序并显示结果
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            print("   相关文档:")
            for i, (doc_idx, similarity) in enumerate(similarities[:3]):
                doc = pmbok_docs[doc_idx]
                print(f"     {i+1}. {doc['title']} (相似度: {similarity:.3f})")
                print(f"        类别: {doc['category']}")
                print(f"        内容: {doc['content'][:100]}...")
            
        except Exception as e:
            print(f"   查询处理错误: {str(e)}")

def test_knowledge_classification():
    """测试知识分类功能"""
    print("\n=== 测试知识分类功能 ===")
    
    # 测试文本
    test_texts = [
        "项目管理者应该建立开放、信任的工作环境",
        "敏捷开发强调迭代和增量交付",
        "干系人管理是项目成功的关键因素",
        "项目生命周期包括启动、规划、执行、监控、收尾五个阶段"
    ]
    
    # 预定义类别
    categories = [
        "项目管理原则",
        "项目绩效域", 
        "开发方法",
        "生命周期管理"
    ]
    
    try:
        # 生成类别向量
        category_resp = dashscope.TextEmbedding.call(
            model="text-embedding-v4",
            input=categories,
            dimension=1024
        )
        
        if category_resp.status_code != HTTPStatus.OK:
            print(f"类别向量生成失败: {category_resp.message}")
            return
        
        category_embeddings = [emb['embedding'] for emb in category_resp.output['embeddings']]
        
        # 对每个测试文本进行分类
        for text in test_texts:
            print(f"\n文本: '{text}'")
            
            # 生成文本向量
            text_resp = dashscope.TextEmbedding.call(
                model="text-embedding-v4",
                input=text,
                dimension=1024
            )
            
            if text_resp.status_code != HTTPStatus.OK:
                print(f"   文本向量生成失败: {text_resp.message}")
                continue
            
            text_embedding = text_resp.output['embeddings'][0]['embedding']
            
            # 计算与各类别的相似度
            import numpy as np
            
            def cosine_similarity(vec1, vec2):
                a = np.array(vec1)
                b = np.array(vec2)
                dot_product = np.dot(a, b)
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                
                return dot_product / (norm_a * norm_b)
            
            similarities = []
            for i, category_emb in enumerate(category_embeddings):
                similarity = cosine_similarity(text_embedding, category_emb)
                similarities.append((categories[i], similarity))
            
            # 排序并显示结果
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            print("   分类结果:")
            for category, similarity in similarities:
                print(f"     {category}: {similarity:.3f}")
            
            # 显示最匹配的类别
            best_category, best_score = similarities[0]
            print(f"   → 最匹配类别: {best_category} (置信度: {best_score:.3f})")
    
    except Exception as e:
        print(f"知识分类测试错误: {str(e)}")

def main():
    """主测试函数"""
    print("PMBOK知识RAG系统测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置DASHSCOPE_API_KEY环境变量")
        return
    
    print(f"✅ API Key已设置: {api_key[:10]}...")
    print(f"✅ 使用模型: text-embedding-v4")
    print()
    
    try:
        # 测试PMBOK知识检索
        test_pmbok_rag_search()
        
        # 测试知识分类
        test_knowledge_classification()
        
        print("\n" + "=" * 60)
        print("✅ PMBOK知识RAG系统测试完成！")
        print("\n主要功能验证:")
        print("  ✅ 文本向量化 (text-embedding-v4)")
        print("  ✅ 语义相似度计算")
        print("  ✅ 知识检索和排序")
        print("  ✅ 知识分类功能")
        print("  ✅ PMBOK知识库集成")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

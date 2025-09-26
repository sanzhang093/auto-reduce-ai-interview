#!/usr/bin/env python3
"""
简单测试RAG系统向量化功能
"""
import os
import sys
import dashscope
from http import HTTPStatus

# 设置API Key（如果环境变量中没有）
# os.environ["DASHSCOPE_API_KEY"] = "your_api_key_here"

def test_dashscope_embedding():
    """测试DashScope向量化功能"""
    print("=== 测试DashScope向量化功能 ===")
    
    # 测试文本
    test_text = "项目管理知识体系指南第七版介绍了12项项目管理原则"
    
    try:
        print(f"测试文本: {test_text}")
        print(f"使用模型: text-embedding-v4")
        
        # 调用DashScope API
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
            print(f"   向量后5个值: {embedding[-5:]}")
            return True
        else:
            print(f"❌ API调用失败: {resp.message}")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

def test_batch_embedding():
    """测试批量向量化"""
    print("\n=== 测试批量向量化 ===")
    
    test_texts = [
        "项目管理知识体系指南第七版",
        "干系人绩效域涉及与干系人相关的活动",
        "敏捷开发方法强调迭代和增量交付",
        "风险管理是项目管理的重要组成部分"
    ]
    
    try:
        print(f"批量处理 {len(test_texts)} 个文本")
        
        resp = dashscope.TextEmbedding.call(
            model="text-embedding-v4",
            input=test_texts,
            dimension=1024
        )
        
        if resp.status_code == HTTPStatus.OK:
            embeddings = resp.output['embeddings']
            print(f"✅ 成功批量生成 {len(embeddings)} 个向量")
            
            for i, emb in enumerate(embeddings):
                embedding = emb['embedding']
                print(f"   文本 {i+1}: 维度 {len(embedding)}, 前3个值: {embedding[:3]}")
            
            return True
        else:
            print(f"❌ 批量API调用失败: {resp.message}")
            return False
            
    except Exception as e:
        print(f"❌ 批量处理发生错误: {str(e)}")
        return False

def test_similarity():
    """测试相似度计算"""
    print("\n=== 测试相似度计算 ===")
    
    import numpy as np
    
    def cosine_similarity(vec1, vec2):
        """计算余弦相似度"""
        a = np.array(vec1)
        b = np.array(vec2)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    # 测试文本对
    text_pairs = [
        ("项目管理", "项目管理工作"),
        ("风险管理", "风险控制"),
        ("敏捷开发", "传统瀑布模型")
    ]
    
    try:
        for text1, text2 in text_pairs:
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
        
        return True
        
    except Exception as e:
        print(f"❌ 相似度计算发生错误: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("DashScope向量化功能测试")
    print("=" * 50)
    
    # 检查API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置DASHSCOPE_API_KEY环境变量")
        print("   请设置API Key: export DASHSCOPE_API_KEY='your_api_key'")
        print("   或取消注释代码中的API Key设置")
        return
    
    print(f"✅ API Key已设置: {api_key[:10]}...")
    print()
    
    # 运行测试
    tests = [
        ("单个向量化", test_dashscope_embedding),
        ("批量向量化", test_batch_embedding),
        ("相似度计算", test_similarity)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # 输出测试结果
    print("=" * 50)
    print("测试结果汇总:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 个测试通过")

if __name__ == "__main__":
    main()

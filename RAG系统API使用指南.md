# RAG系统API使用指南

## 🚀 快速开始

### 1. 基本初始化

```python
from app.services.rag_system import RAGSystem

# 创建RAG系统实例
rag = RAGSystem()

# 加载PMBOK文档
rag.load_pmbok_documents()
```

### 2. 知识检索

```python
# 搜索项目管理知识
results = rag.search_pmbok_knowledge("项目管理的基本原则", top_k=5)

# 查看结果
for result in results:
    print(f"相似度: {result['similarity']:.3f}")
    print(f"页码: {result['page_number']}")
    print(f"章节: {result['section']}")
    print(f"内容: {result['content'][:200]}...")
    print("-" * 50)
```

### 3. 页码验证

```python
# 模拟LLM声称的页码
claimed_pages = [1, 5, 10, 15, 20]

# 验证页码引用
validated_pages = rag.validate_page_references(claimed_pages, results)
print(f"验证后的页码: {validated_pages}")
```

## 📋 常用查询示例

### 项目管理原则

```python
queries = [
    "项目管理的基本原则是什么？",
    "12项项目管理原则包括哪些？",
    "如何成为勤勉的项目管理者？"
]

for query in queries:
    results = rag.search_pmbok_knowledge(query, top_k=3)
    print(f"查询: {query}")
    print(f"找到 {len(results)} 个相关结果")
    print()
```

### 项目绩效域

```python
queries = [
    "什么是项目绩效域？",
    "8个项目绩效域包括哪些？",
    "干系人绩效域如何管理？"
]

for query in queries:
    results = rag.search_pmbok_knowledge(query, top_k=3)
    print(f"查询: {query}")
    print(f"找到 {len(results)} 个相关结果")
    print()
```

### 敏捷管理

```python
queries = [
    "敏捷项目管理的特点",
    "预测型vs适应型方法",
    "混合型开发方法"
]

for query in queries:
    results = rag.search_pmbok_knowledge(query, top_k=3)
    print(f"查询: {query}")
    print(f"找到 {len(results)} 个相关结果")
    print()
```

## 🧩 文本分块(Chunk)说明

### 分块机制

RAG系统将PMBOK文档分割成359个chunks，每个chunk代表一个完整的章节：

```python
# 查看分块信息
rag = RAGSystem()
rag.load_pmbok_documents()

print(f"总chunk数量: {len(rag.pmbok_documents)}")

# 查看前几个chunk的信息
for i, chunk in enumerate(rag.pmbok_documents[:3]):
    print(f"Chunk {i+1}:")
    print(f"  章节: {chunk.section}")
    print(f"  页码: {chunk.page_number}")
    print(f"  长度: {len(chunk.content)} 字符")
    print(f"  内容预览: {chunk.content[:100]}...")
    print()
```

### 分块特点

- **章节级分割**: 以`# 标题`为分界点
- **语义完整**: 保持章节内容的完整性
- **页码映射**: 每个chunk都有对应的页码
- **大小适中**: 大多数chunk在1-8K字符范围内

### 超长chunk处理

系统会自动处理超过8192字符的chunk：

```python
# 检查超长chunk
long_chunks = [chunk for chunk in rag.pmbok_documents if len(chunk.content) > 8192]
print(f"超长chunk数量: {len(long_chunks)}")

for chunk in long_chunks:
    print(f"章节: {chunk.section}")
    print(f"长度: {len(chunk.content)} 字符")
    print(f"超出: {len(chunk.content) - 8192} 字符")
```

## 🔧 高级功能

### 批量处理

```python
# 批量生成嵌入向量
texts = ["项目管理", "敏捷开发", "风险管理"]
embeddings = rag._generate_batch_embeddings(texts)
print(f"生成了 {len(embeddings)} 个嵌入向量")
```

### 相似度计算

```python
# 计算两个文本的相似度
text1 = "项目管理基本原则"
text2 = "项目管理核心原则"
embedding1 = rag._generate_embedding(text1)
embedding2 = rag._generate_embedding(text2)
similarity = rag._cosine_similarity(embedding1, embedding2)
print(f"相似度: {similarity:.3f}")
```

### 系统统计

```python
# 获取系统统计信息
stats = rag.get_system_statistics()
print(f"总文档数: {stats['total_documents']}")
print(f"类型分布: {stats['type_distribution']}")
print(f"项目分布: {stats['project_distribution']}")
```

## ⚠️ 注意事项

### 文本长度限制

```python
# 系统会自动处理超长文本
long_text = "很长的文本内容..." * 1000  # 超过8192字符
embedding = rag._generate_embedding(long_text)  # 自动截断
```

### 错误处理

```python
try:
    results = rag.search_pmbok_knowledge("查询内容")
    if not results:
        print("未找到相关结果")
except Exception as e:
    print(f"检索失败: {str(e)}")
```

### 性能优化

```python
# 使用批量处理提高效率
texts = ["文本1", "文本2", "文本3"]
embeddings = rag._generate_batch_embeddings(texts)  # 比单个处理更高效
```

## 📊 返回数据格式

### 检索结果格式

```python
{
    "content": "文档内容",
    "page_number": 47,
    "section": "项目管理原则", 
    "similarity": 0.720,
    "source": "PMBOK第七版中文版"
}
```

### 系统统计格式

```python
{
    "total_documents": 359,
    "type_distribution": {"PMBOK": 359},
    "project_distribution": {"PMBOK": 359},
    "embedding_dimension": 1024,
    "last_updated": "2024-09-24T23:00:00"
}
```

## 🧪 测试代码

### 完整测试示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.services.rag_system import RAGSystem

def test_rag_system():
    """测试RAG系统功能"""
    
    # 1. 初始化
    rag = RAGSystem()
    print("✅ RAG系统初始化完成")
    
    # 2. 加载文档
    success = rag.load_pmbok_documents()
    if not success:
        print("❌ 文档加载失败")
        return
    print("✅ PMBOK文档加载完成")
    
    # 3. 测试检索
    test_queries = [
        "项目管理的基本原则",
        "什么是项目绩效域",
        "敏捷项目管理特点"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        results = rag.search_pmbok_knowledge(query, top_k=3)
        
        if results:
            print(f"✅ 找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. 相似度: {result['similarity']:.3f}")
                print(f"     页码: {result['page_number']}")
                print(f"     章节: {result['section']}")
        else:
            print("❌ 未找到相关结果")
    
    # 4. 测试页码验证
    print(f"\n✅ 测试页码验证功能")
    claimed_pages = [1, 5, 10, 999]  # 包含幻觉页码
    search_results = rag.search_pmbok_knowledge("项目管理原则", top_k=5)
    validated_pages = rag.validate_page_references(claimed_pages, search_results)
    print(f"原始页码: {claimed_pages}")
    print(f"验证后页码: {validated_pages}")
    
    print("\n🎉 RAG系统测试完成！")

if __name__ == "__main__":
    test_rag_system()
```

## 📞 技术支持

### 常见问题

1. **Q: 如何提高检索精度？**
   A: 使用更具体的查询词，调整top_k参数，确保查询与PMBOK内容相关。

2. **Q: 为什么有些页码被移除了？**
   A: 系统会自动移除不在检索结果中的页码，这是幻觉检测功能。

3. **Q: 如何处理超长文本？**
   A: 系统会自动截断超过8192字符的文本，无需手动处理。

### 联系方式

- **技术文档**: 查看完整说明文档
- **问题反馈**: 通过系统日志查看详细错误信息
- **功能建议**: 联系开发团队

---

**版本**: 1.0.0  
**更新时间**: 2024年9月24日

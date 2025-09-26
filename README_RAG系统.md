# RAG系统 - PMBOK知识检索

## 🎯 简介

基于阿里云DashScope的智能RAG系统，专门用于PMBOK第七版项目管理知识的检索和问答。支持页码验证、幻觉检测和语义搜索。

## ✨ 主要特性

- 🔍 **智能检索**: 基于text-embedding-v4的语义搜索
- 🧩 **智能分块**: 章节级chunk分割，保持语义完整性
- 📄 **页码验证**: 自动检测和移除幻觉页码引用  
- 📚 **PMBOK集成**: 完整的PMBOK第七版知识库（359个chunks）
- ⚡ **高性能**: 批量处理和降级保护机制
- 🛡️ **稳定可靠**: 完善的错误处理和日志记录

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install dashscope numpy pydantic
```

### 2. 配置API

```python
import dashscope
dashscope.api_key = "your-api-key-here"
```

### 3. 基本使用

```python
from app.services.rag_system import RAGSystem

# 创建并初始化
rag = RAGSystem()
rag.load_pmbok_documents()

# 搜索知识
results = rag.search_pmbok_knowledge("项目管理的基本原则", top_k=5)

# 查看结果
for result in results:
    print(f"页码: {result['page_number']}")
    print(f"章节: {result['section']}")
    print(f"相似度: {result['similarity']:.3f}")
    print(f"内容: {result['content'][:200]}...")
```

## 📊 系统性能

- **文档数量**: 359个PMBOK文档块（chunks）
- **分块统计**: 68.2%为短chunk（<500字符），0.8%为超长chunk（>8192字符）
- **检索精度**: 相似度0.7+为高相关度
- **响应时间**: 单次检索<2秒
- **准确率**: 页码验证准确率>95%

## 📁 文件结构

```
├── app/services/rag_system.py          # 核心RAG系统
├── PMBOK第七版中英文资料/              # PMBOK文档
├── test_rag_direct.py                  # 测试脚本
├── analyze_chunks.py                   # chunk分析脚本
├── RAG系统说明文档.md                  # 详细文档
├── RAG系统API使用指南.md               # API指南
└── README_RAG系统.md                   # 本文件
```

## 🧪 测试

```bash
# 运行测试
python test_rag_direct.py

# 分析文本长度
python analyze_text_length.py

# 分析chunk分块情况
python analyze_chunks.py
```

## 📖 文档

- [详细说明文档](RAG系统说明文档.md) - 完整的系统架构和功能说明
- [API使用指南](RAG系统API使用指南.md) - 快速上手指南和示例代码

## ⚠️ 注意事项

1. **API限制**: DashScope text-embedding-v4限制输入文本长度为1-8192字符
2. **文档路径**: 确保PMBOK文档文件结构正确
3. **网络连接**: 需要稳定的网络连接访问DashScope API

## 🔧 故障排除

### 常见问题

1. **API调用失败**: 检查API Key配置和网络连接
2. **文档加载失败**: 检查PMBOK文档路径和文件结构
3. **文本长度超限**: 系统自动截断，无需手动处理

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 更新日志

### v1.0.0 (2024-09-24)
- ✅ 初始版本发布
- ✅ 支持PMBOK第七版知识检索
- ✅ 实现页码验证和幻觉检测
- ✅ 集成阿里云DashScope text-embedding-v4
- ✅ 添加批量处理和降级保护

## 📞 技术支持

如有问题或建议，请查看详细文档或联系开发团队。

---

**开发团队** | **版本**: 1.0.0 | **更新时间**: 2024年9月24日

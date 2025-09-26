# RAG项目代码结构分析：页码引用与父页面检索机制

## 项目概述

这是一个RAG挑战赛的获胜解决方案，专注于企业年报问答系统。项目通过以下技术实现了高质量的检索和透明度：

- 自定义PDF解析（使用Docling）
- 向量搜索与父文档检索
- LLM重排序提升上下文相关性
- 结构化输出提示与链式思维推理
- 多公司比较的查询路由

## 核心架构：增强检索质量与透明度

### 1. 页码引用机制实现

#### 1.1 内容提取阶段的页码存储

**文件位置**: `src/pdf_parsing.py`

```python
# 在PDF解析过程中，每个页面都被分配了页码
def _normalize_page_sequence(self, data: dict) -> dict:
    """确保内容中的页码是连续的，通过填充空白页面来填补间隙"""
    # 创建新内容数组，包含所有页面
    new_content = []
    for page_num in range(1, max_page + 1):
        page_content = next(
            (page for page in data['content'] if page['page'] == page_num),
            {"page": page_num, **empty_page_template}
        )
        new_content.append(page_content)
```

**关键特点**:
- 每个文本块都存储了其父页面编号
- 通过`_normalize_page_sequence`确保页码连续性
- 在元数据中保存页面信息，便于快速回溯

#### 1.2 文本分块时的页码保留

**文件位置**: `src/text_splitter.py`

```python
def _split_page(self, page: Dict[str, any], chunk_size: int = 300, chunk_overlap: int = 50):
    """将页面文本分割成块，原始文本包含markdown表格"""
    chunks = text_splitter.split_text(page['text'])
    chunks_with_meta = []
    for chunk in chunks:
        chunks_with_meta.append({
            "page": page['page'],  # 保留页码信息
            "length_tokens": self.count_tokens(chunk),
            "text": chunk
        })
    return chunks_with_meta
```

**关键特点**:
- 每个文本块都保留了原始页码信息
- 分块过程中页码作为元数据被完整保存
- 支持后续的页码验证和引用

### 2. 父页面检索机制

#### 2.1 检索器中的父页面选项

**文件位置**: `src/retrieval.py`

```python
def retrieve_by_company_name(self, company_name: str, query: str, 
                           top_n: int = 3, return_parent_pages: bool = False):
    """根据公司名称检索相关文档"""
    # ... 检索逻辑 ...
    
    for distance, index in zip(distances[0], indices[0]):
        chunk = chunks[index]
        parent_page = next(page for page in pages if page["page"] == chunk["page"])
        
        if return_parent_pages:
            # 返回完整页面而不是小块
            if parent_page["page"] not in seen_pages:
                seen_pages.add(parent_page["page"])
                result = {
                    "distance": distance,
                    "page": parent_page["page"],
                    "text": parent_page["text"]  # 完整页面内容
                }
                retrieval_results.append(result)
        else:
            # 返回小块
            result = {
                "distance": distance,
                "page": chunk["page"],
                "text": chunk["text"]  # 小块内容
            }
            retrieval_results.append(result)
```

**关键特点**:
- `return_parent_pages`参数控制是否返回完整页面
- 检索出的最相关文本块作为"指针"定位对应完整页面
- 去重机制确保每个页面只返回一次

#### 2.2 混合检索器的父页面支持

**文件位置**: `src/retrieval.py` - `HybridRetriever`类

```python
def retrieve_by_company_name(self, company_name: str, query: str, 
                           return_parent_pages: bool = False):
    """使用混合方法检索和重排序文档"""
    # 从向量检索器获取初始结果
    vector_results = self.vector_retriever.retrieve_by_company_name(
        company_name=company_name,
        query=query,
        top_n=llm_reranking_sample_size,
        return_parent_pages=return_parent_pages  # 支持父页面检索
    )
    
    # 使用LLM重排序结果
    reranked_results = self.reranker.rerank_documents(
        query=query,
        documents=vector_results,
        documents_batch_size=documents_batch_size,
        llm_weight=llm_weight
    )
    
    return reranked_results[:top_n]
```

### 3. 页码验证与引用系统

#### 3.1 页码验证机制

**文件位置**: `src/questions_processing.py`

```python
def _validate_page_references(self, claimed_pages: list, retrieval_results: list, 
                            min_pages: int = 2, max_pages: int = 8) -> list:
    """验证LLM答案中提到的所有页码是否都来自检索结果"""
    retrieved_pages = [result['page'] for result in retrieval_results]
    
    # 验证页码是否在检索结果中
    validated_pages = [page for page in claimed_pages if page in retrieved_pages]
    
    # 移除幻觉页码引用
    if len(validated_pages) < len(claimed_pages):
        removed_pages = set(claimed_pages) - set(validated_pages)
        print(f"Warning: Removed {len(removed_pages)} hallucinated page references: {removed_pages}")
    
    # 如果有效页码太少，从检索结果中添加
    if len(validated_pages) < min_pages and retrieval_results:
        for result in retrieval_results:
            page = result['page']
            if page not in existing_pages:
                validated_pages.append(page)
                existing_pages.add(page)
                if len(validated_pages) >= min_pages:
                    break
    
    return validated_pages
```

**关键特点**:
- 验证LLM声称的页码是否真实存在于检索结果中
- 自动移除"幻觉"页码引用
- 确保至少包含最小数量的有效页码引用

#### 3.2 引用提取与格式化

```python
def _extract_references(self, pages_list: list, company_name: str) -> list:
    """从页码列表提取引用信息"""
    # 从CSV文件中查找公司的SHA1
    matching_rows = self.companies_df[self.companies_df['company_name'] == company_name]
    company_sha1 = matching_rows.iloc[0]['sha1'] if not matching_rows.empty else ""
    
    refs = []
    for page in pages_list:
        refs.append({
            "pdf_sha1": company_sha1,  # PDF文件的唯一标识
            "page_index": page         # 页码（1-based）
        })
    return refs
```

### 4. 提示工程中的页码要求

#### 4.1 结构化输出中的页码字段

**文件位置**: `src/prompts.py`

```python
class AnswerSchema(BaseModel):
    relevant_pages: List[int] = Field(description="""
    包含直接用于回答问题信息的页码列表。仅包括：
    - 包含直接答案或明确声明的页面
    - 包含强烈支持答案的关键信息的页面
    不要包括仅包含相关信息的页面或与答案有弱连接的页面。
    至少应包含一个页面。
    """)
```

**关键特点**:
- 明确要求LLM提供相关页码
- 详细说明什么类型的页面应该被引用
- 确保至少包含一个页码引用

#### 4.2 提交格式的页码转换

```python
def _post_process_submission_answers(self, processed_questions: List[dict]) -> List[dict]:
    """后处理提交格式的答案"""
    for ref in references:
        # 将页码从1-based转换为0-based（比赛要求0-based页码索引）
        references = [
            {
                "pdf_sha1": ref["pdf_sha1"],
                "page_index": ref["page_index"] - 1  # 转换为0-based
            }
            for ref in references
        ]
```

### 5. 数据流与透明度

#### 5.1 完整的RAG流水线

1. **PDF解析** (`src/pdf_parsing.py`)
   - 使用Docling解析PDF
   - 保留页码信息
   - 生成结构化JSON

2. **报告合并** (`src/parsed_reports_merging.py`)
   - 将复杂JSON转换为简单页面列表
   - 保持页码连续性
   - 处理表格和列表

3. **文本分块** (`src/text_splitter.py`)
   - 将页面分割为小块
   - 保留每个块的页码元数据
   - 支持序列化表格

4. **向量化** (`src/ingestion.py`)
   - 创建向量数据库
   - 保持块与页码的映射关系
   - 支持BM25索引

5. **检索** (`src/retrieval.py`)
   - 支持父页面检索
   - 混合检索（向量+重排序）
   - 返回带页码的结果

6. **问答处理** (`src/questions_processing.py`)
   - 验证页码引用
   - 生成结构化答案
   - 提取引用信息

#### 5.2 透明度机制

- **页码验证**: 确保所有引用的页码都来自实际检索结果
- **幻觉检测**: 自动移除LLM生成的虚假页码引用
- **引用追踪**: 从页码到PDF文件的完整追踪链
- **调试信息**: 详细的答案细节和推理过程

## 配置选项

### 父页面检索配置

```python
# 在pipeline.py中的配置
parent_document_retrieval_config = RunConfig(
    parent_document_retrieval=True,  # 启用父页面检索
    parallel_requests=20,
    submission_name="Ilia Ris v.1",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + SO CoT"
)
```

### 重排序配置

```python
max_config = RunConfig(
    use_serialized_tables=True,
    parent_document_retrieval=True,
    llm_reranking=True,              # 启用LLM重排序
    llm_reranking_sample_size=30,    # 重排序样本大小
    top_n_retrieval=10,              # 最终检索数量
)
```

## 总结

这个RAG项目通过以下机制实现了增强的检索质量与透明度：

1. **页码引用系统**: 从PDF解析到最终答案，每个步骤都保留和验证页码信息
2. **父页面检索**: 使用小块作为指针，检索完整页面提供更丰富的上下文
3. **幻觉检测**: 自动验证和移除虚假的页码引用
4. **结构化输出**: 通过提示工程确保LLM提供可验证的页码引用
5. **完整追踪**: 从页码到PDF文件的完整引用链

这些机制确保了系统的透明度，使用户能够验证模型的答案是否基于真实的源材料，而不是虚假信息。

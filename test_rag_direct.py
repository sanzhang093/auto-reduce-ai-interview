#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试RAG系统，不依赖应用框架
"""

import json
import os
import math
import dashscope
from http import HTTPStatus
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import re

# 简化的RAG系统类
@dataclass
class PMBOKDocument:
    """PMBOK文档块"""
    content: str
    page_number: int
    section: str
    document_type: str = "PMBOK"
    source_file: str = "PMBOK第七版中文版"

class SimpleRAGSystem:
    """简化的RAG系统"""
    
    def __init__(self):
        """初始化RAG系统"""
        self.embedding_dim = 1024
        self.embedding_model = "text-embedding-v4"
        self.pmbok_documents = []
        print("RAG检索系统初始化完成，使用text-embedding-v4模型")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入"""
        try:
            # 检查文本长度，如果超过8192字符则截断
            if len(text) > 8192:
                text = text[:8192]
                print(f"⚠️ 文本长度超过8192字符，已截断到8192字符")
            
            resp = dashscope.TextEmbedding.call(
                model=self.embedding_model,
                input=text
            )
            
            if resp.status_code == HTTPStatus.OK:
                embedding = resp.output['embeddings'][0]['embedding']
                return embedding
            else:
                print(f"DashScope API调用失败: {resp.message}")
                return self._fallback_embedding(text)
                
        except Exception as e:
            print(f"生成文本嵌入时发生错误: {str(e)}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """降级嵌入生成"""
        # 简化的字符频率向量化
        char_freq = {}
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        # 创建固定长度的向量
        embedding = [0.0] * self.embedding_dim
        for i, (char, freq) in enumerate(char_freq.items()):
            if i < self.embedding_dim:
                embedding[i] = float(freq)
        
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        try:
            # 计算点积
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # 计算模长
            norm_a = math.sqrt(sum(a * a for a in vec1))
            norm_b = math.sqrt(sum(b * b for b in vec2))
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
        except Exception as e:
            print(f"计算余弦相似度失败: {str(e)}")
            return 0.0
    
    def load_pmbok_documents(self, pmbok_dir: str = "PMBOK第七版中英文资料") -> bool:
        """加载PMBOK文档并解析页码信息"""
        try:
            # 构建文件路径
            full_md_path = os.path.join(pmbok_dir, "0- PMBOK指南 第七版_中文版.pdf-3bf8755e-73b1-4670-863e-8a3846f244be", "full.md")
            layout_json_path = os.path.join(pmbok_dir, "0- PMBOK指南 第七版_中文版.pdf-3bf8755e-73b1-4670-863e-8a3846f244be", "layout.json")
            
            if not os.path.exists(full_md_path) or not os.path.exists(layout_json_path):
                print(f"PMBOK文档文件不存在: {full_md_path} 或 {layout_json_path}")
                return False
            
            # 读取布局信息
            with open(layout_json_path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            # 构建页码到内容的映射
            page_content_map = {}
            for page_info in layout_data.get("pdf_info", []):
                page_idx = page_info.get("page_idx", 0)
                for block in page_info.get("para_blocks", []):
                    if block.get("type") == "text":
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                content = span.get("content", "").strip()
                                if content:
                                    if page_idx not in page_content_map:
                                        page_content_map[page_idx] = []
                                    page_content_map[page_idx].append(content)
            
            # 读取完整文档内容
            with open(full_md_path, 'r', encoding='utf-8') as f:
                full_content = f.read()
            
            # 按章节分割内容
            sections = self._split_pmbok_sections(full_content)
            
            # 为每个章节创建文档块
            self.pmbok_documents = []
            for section_name, section_content in sections.items():
                # 尝试匹配页码
                page_number = self._extract_page_number_from_section(section_content, page_content_map)
                
                # 创建PMBOK文档块
                pmbok_doc = PMBOKDocument(
                    content=section_content,
                    page_number=page_number,
                    section=section_name,
                    document_type="PMBOK",
                    source_file="PMBOK第七版中文版"
                )
                self.pmbok_documents.append(pmbok_doc)
            
            print(f"成功加载{len(self.pmbok_documents)}个PMBOK文档块")
            return True
            
        except Exception as e:
            print(f"加载PMBOK文档失败: {str(e)}")
            return False
    
    def _split_pmbok_sections(self, content: str) -> Dict[str, str]:
        """分割PMBOK文档为章节"""
        sections = {}
        current_section = "前言"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测章节标题
            if line.startswith('# ') and len(line) > 2:
                # 保存前一章节
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # 开始新章节
                current_section = line[2:].strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        # 保存最后一章节
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_page_number_from_section(self, section_content: str, page_content_map: Dict[int, List[str]]) -> int:
        """从章节内容中提取页码信息"""
        try:
            # 简单的页码匹配逻辑
            section_words = section_content.split()[:10]  # 取前10个词进行匹配
            
            best_match_page = 1
            max_matches = 0
            
            for page_num, page_contents in page_content_map.items():
                matches = 0
                for word in section_words:
                    for content in page_contents:
                        if word in content:
                            matches += 1
                            break
                
                if matches > max_matches:
                    max_matches = matches
                    best_match_page = page_num
            
            return best_match_page
        except Exception as e:
            print(f"提取页码失败: {str(e)}")
            return 1
    
    def search_pmbok_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索PMBOK知识库"""
        try:
            if not self.pmbok_documents:
                print("PMBOK文档未加载，请先调用load_pmbok_documents()")
                return []
            
            # 生成查询向量
            query_embedding = self._generate_embedding(query)
            
            # 计算相似度
            results = []
            for doc in self.pmbok_documents:
                doc_embedding = self._generate_embedding(doc.content)
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                results.append({
                    "content": doc.content,
                    "page_number": doc.page_number,
                    "section": doc.section,
                    "similarity": similarity,
                    "source": doc.source_file
                })
            
            # 按相似度排序
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            print(f"搜索PMBOK知识库失败: {str(e)}")
            return []
    
    def validate_page_references(self, claimed_pages: List[int], search_results: List[Dict[str, Any]]) -> List[int]:
        """验证页码引用，防止幻觉页码"""
        try:
            # 获取检索结果中的实际页码
            retrieved_pages = [result.get("page_number", 0) for result in search_results]
            retrieved_pages = [p for p in retrieved_pages if p > 0]  # 过滤无效页码
            
            # 验证声称的页码是否在检索结果中
            validated_pages = [page for page in claimed_pages if page in retrieved_pages]
            
            # 移除幻觉页码引用
            if len(validated_pages) < len(claimed_pages):
                removed_pages = set(claimed_pages) - set(validated_pages)
                print(f"移除了{len(removed_pages)}个幻觉页码引用: {removed_pages}")
            
            # 如果有效页码太少，从检索结果中添加
            if len(validated_pages) < 2 and retrieved_pages:
                for page in retrieved_pages:
                    if page not in validated_pages:
                        validated_pages.append(page)
                        if len(validated_pages) >= 2:
                            break
            
            return validated_pages
            
        except Exception as e:
            print(f"验证页码引用失败: {str(e)}")
            return claimed_pages

def test_rag_system():
    """测试RAG系统"""
    print("🚀 开始测试PMBOK RAG系统...")
    
    # 创建RAG系统实例
    rag = SimpleRAGSystem()
    
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
        "敏捷项目管理的特点"
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
    
    print("\n🎉 PMBOK RAG系统测试完成！")

if __name__ == "__main__":
    try:
        test_rag_system()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

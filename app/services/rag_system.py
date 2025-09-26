"""
RAG检索系统
"""
import json
import numpy as np
import dashscope
from http import HTTPStatus
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import re
import os
from app.utils.logger import get_logger
from app.services.database_service import database_service
from app.services.qwen_agent import RAGDocument, RAGSearchResult

logger = get_logger(__name__)


@dataclass
class VectorEmbedding:
    """向量嵌入"""
    doc_id: str
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class PMBOKDocument:
    """PMBOK文档块"""
    content: str
    page_number: int
    section: str
    document_type: str = "PMBOK"
    source_file: str = "PMBOK第七版中文版"


class RAGSystem:
    """RAG检索系统"""
    
    def __init__(self):
        """初始化RAG系统"""
        self.db = database_service.get_database()
        self.vector_db = {}  # 简化版向量数据库
        self.embedding_dim = 1024  # text-embedding-v4的默认维度
        self.embedding_model = "text-embedding-v4"  # 使用阿里云text-embedding-v4模型
        self.pmbok_documents = []  # PMBOK文档存储
        logger.info("RAG检索系统初始化完成，使用text-embedding-v4模型")
    
    def add_document(self, document: RAGDocument) -> bool:
        """添加文档到RAG系统"""
        try:
            # 生成文档嵌入（简化版，实际应该使用真实的嵌入模型）
            embedding = self._generate_embedding(document.content)
            
            # 创建向量嵌入对象
            vector_embedding = VectorEmbedding(
                doc_id=document.doc_id,
                embedding=embedding,
                metadata={
                    "title": document.title,
                    "content": document.content,
                    "doc_type": document.doc_type,
                    "project_id": document.project_id,
                    "metadata": document.metadata
                },
                created_at=datetime.now()
            )
            
            # 存储到向量数据库
            self.vector_db[document.doc_id] = vector_embedding
            
            # 保存到持久化存储
            self._save_embedding(vector_embedding)
            
            logger.info(f"文档 {document.doc_id} 已添加到RAG系统")
            return True
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            return False
    
    def search_documents(self, query: str, top_k: int = 5, 
                        project_id: Optional[str] = None,
                        doc_types: Optional[List[str]] = None) -> List[RAGSearchResult]:
        """搜索相关文档"""
        try:
            # 生成查询嵌入
            query_embedding = self._generate_embedding(query)
            
            # 计算相似度
            similarities = []
            for doc_id, vector_embedding in self.vector_db.items():
                # 过滤条件
                if project_id and vector_embedding.metadata.get("project_id") != project_id:
                    continue
                if doc_types and vector_embedding.metadata.get("doc_type") not in doc_types:
                    continue
                
                # 计算余弦相似度
                similarity = self._cosine_similarity(query_embedding, vector_embedding.embedding)
                
                similarities.append({
                    "doc_id": doc_id,
                    "similarity": similarity,
                    "vector_embedding": vector_embedding
                })
            
            # 按相似度排序
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # 返回前k个结果
            results = []
            for item in similarities[:top_k]:
                vector_embedding = item["vector_embedding"]
                result = RAGSearchResult(
                    doc_id=item["doc_id"],
                    title=vector_embedding.metadata["title"],
                    content=vector_embedding.metadata["content"],
                    doc_type=vector_embedding.metadata["doc_type"],
                    relevance_score=item["similarity"],
                    metadata=vector_embedding.metadata["metadata"]
                )
                results.append(result)
            
            logger.info(f"搜索查询 '{query}' 返回 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"搜索文档失败: {str(e)}")
            return []
    
    def _generate_embedding(self, text: str) -> List[float]:
        """使用阿里云text-embedding-v4模型生成文本嵌入"""
        try:
            # 检查文本长度，如果超过8192字符则截断
            if len(text) > 8192:
                text = text[:8192]
                logger.warning(f"文本长度超过8192字符，已截断到8192字符")
            
            # 调用阿里云DashScope的text-embedding-v4模型
            resp = dashscope.TextEmbedding.call(
                model=self.embedding_model,
                input=text,
                dimension=self.embedding_dim  # 使用1024维度
            )
            
            if resp.status_code == HTTPStatus.OK:
                # 提取嵌入向量
                embedding = resp.output['embeddings'][0]['embedding']
                logger.debug(f"成功生成文本嵌入，维度: {len(embedding)}")
                return embedding
            else:
                logger.error(f"DashScope API调用失败: {resp.message}")
                # 降级到简化版向量化
                return self._fallback_embedding(text)
                
        except Exception as e:
            logger.error(f"生成文本嵌入时发生错误: {str(e)}")
            # 降级到简化版向量化
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """降级方案：简化版文本向量化"""
        logger.warning("使用降级方案生成文本嵌入")
        
        # 文本预处理
        text = text.lower().strip()
        
        # 基于字符频率的简单向量化
        char_freq = {}
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        # 生成固定维度的向量
        embedding = [0.0] * self.embedding_dim
        
        # 基于字符频率填充向量
        for i, (char, freq) in enumerate(char_freq.items()):
            if i < self.embedding_dim:
                embedding[i] = freq / len(text)  # 归一化
        
        # 添加一些基于文本长度的特征
        embedding[0] = len(text) / 1000.0  # 文本长度特征
        embedding[1] = len(text.split()) / 100.0  # 词数特征
        
        # 确保向量长度一致
        if len(embedding) < self.embedding_dim:
            embedding.extend([0.0] * (self.embedding_dim - len(embedding)))
        elif len(embedding) > self.embedding_dim:
            embedding = embedding[:self.embedding_dim]
        
        return embedding
    
    def _generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入，提高效率"""
        try:
            # 检查并截断过长的文本
            processed_texts = []
            for text in texts:
                if len(text) > 8192:
                    text = text[:8192]
                    logger.warning(f"批量处理中截断过长文本到8192字符")
                processed_texts.append(text)
            
            # 调用阿里云DashScope的text-embedding-v4模型进行批量处理
            resp = dashscope.TextEmbedding.call(
                model=self.embedding_model,
                input=processed_texts,
                dimension=self.embedding_dim
            )
            
            if resp.status_code == HTTPStatus.OK:
                # 提取所有嵌入向量
                embeddings = [item['embedding'] for item in resp.output['embeddings']]
                logger.debug(f"成功批量生成{len(embeddings)}个文本嵌入")
                return embeddings
            else:
                logger.error(f"DashScope批量API调用失败: {resp.message}")
                # 降级到单个处理
                return [self._fallback_embedding(text) for text in processed_texts]
                
        except Exception as e:
            logger.error(f"批量生成文本嵌入时发生错误: {str(e)}")
            # 降级到单个处理
            return [self._fallback_embedding(text) for text in texts]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        try:
            # 转换为numpy数组
            a = np.array(vec1)
            b = np.array(vec2)
            
            # 计算余弦相似度
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
        except Exception as e:
            logger.error(f"计算余弦相似度失败: {str(e)}")
            return 0.0
    
    def _save_embedding(self, vector_embedding: VectorEmbedding):
        """保存嵌入到数据库"""
        try:
            embedding_data = {
                "doc_id": vector_embedding.doc_id,
                "embedding": vector_embedding.embedding,
                "metadata": vector_embedding.metadata,
                "created_at": vector_embedding.created_at.isoformat()
            }
            
            # 保存到数据库
            self.db.create("vector_embeddings", embedding_data)
        except Exception as e:
            logger.error(f"保存嵌入失败: {str(e)}")
    
    def load_embeddings(self):
        """从数据库加载嵌入"""
        try:
            embeddings = self.db.read("vector_embeddings")
            
            for embedding_data in embeddings:
                vector_embedding = VectorEmbedding(
                    doc_id=embedding_data["doc_id"],
                    embedding=embedding_data["embedding"],
                    metadata=embedding_data["metadata"],
                    created_at=datetime.fromisoformat(embedding_data["created_at"])
                )
                
                self.vector_db[vector_embedding.doc_id] = vector_embedding
            
            logger.info(f"加载了 {len(embeddings)} 个嵌入向量")
        except Exception as e:
            logger.error(f"加载嵌入失败: {str(e)}")
    
    def index_project_data(self, project_id: str) -> int:
        """索引项目数据（使用批量向量化优化）"""
        try:
            indexed_count = 0
            documents_to_index = []
            
            # 收集项目信息
            project = self.db.read("projects", project_id)
            if project:
                doc = RAGDocument(
                    doc_id=f"project_{project_id}",
                    title=f"项目: {project.get('project_name', '')}",
                    content=f"项目名称: {project.get('project_name', '')}\n项目描述: {project.get('description', '')}\n项目状态: {project.get('status', '')}\n项目经理: {project.get('project_manager', '')}",
                    doc_type="project",
                    project_id=project_id,
                    metadata=project
                )
                documents_to_index.append(doc)
            
            # 收集任务信息
            tasks = self.db.get_by_field("tasks", "project_id", project_id)
            for task in tasks:
                doc = RAGDocument(
                    doc_id=f"task_{task.get('task_id', '')}",
                    title=f"任务: {task.get('task_name', '')}",
                    content=f"任务名称: {task.get('task_name', '')}\n任务描述: {task.get('description', '')}\n任务状态: {task.get('status', '')}\n负责人: {task.get('assigned_to', '')}\n优先级: {task.get('priority', '')}",
                    doc_type="task",
                    project_id=project_id,
                    metadata=task
                )
                documents_to_index.append(doc)
            
            # 收集风险信息
            risks = self.db.get_by_field("risks", "project_id", project_id)
            for risk in risks:
                doc = RAGDocument(
                    doc_id=f"risk_{risk.get('risk_id', '')}",
                    title=f"风险: {risk.get('risk_title', '')}",
                    content=f"风险标题: {risk.get('risk_title', '')}\n风险描述: {risk.get('description', '')}\n风险等级: {risk.get('risk_level', '')}\n负责人: {risk.get('owner', '')}\n缓解计划: {risk.get('mitigation_plan', '')}",
                    doc_type="risk",
                    project_id=project_id,
                    metadata=risk
                )
                documents_to_index.append(doc)
            
            # 收集问题信息
            issues = self.db.get_by_field("issues", "project_id", project_id)
            for issue in issues:
                doc = RAGDocument(
                    doc_id=f"issue_{issue.get('issue_id', '')}",
                    title=f"问题: {issue.get('issue_title', '')}",
                    content=f"问题标题: {issue.get('issue_title', '')}\n问题描述: {issue.get('description', '')}\n严重程度: {issue.get('severity', '')}\n分配给: {issue.get('assigned_to', '')}\n解决方案: {issue.get('resolution', '')}",
                    doc_type="issue",
                    project_id=project_id,
                    metadata=issue
                )
                documents_to_index.append(doc)
            
            # 批量处理文档索引
            if documents_to_index:
                indexed_count = self._batch_index_documents(documents_to_index)
            
            logger.info(f"项目 {project_id} 索引完成，共索引 {indexed_count} 个文档")
            return indexed_count
        except Exception as e:
            logger.error(f"索引项目数据失败: {str(e)}")
            return 0
    
    def _batch_index_documents(self, documents: List[RAGDocument]) -> int:
        """批量索引文档，使用批量向量化提高效率"""
        try:
            if not documents:
                return 0
            
            # 提取所有文档的文本内容
            texts = [doc.content for doc in documents]
            
            # 批量生成向量嵌入
            embeddings = self._generate_batch_embeddings(texts)
            
            indexed_count = 0
            for i, doc in enumerate(documents):
                try:
                    # 创建向量嵌入对象
                    vector_embedding = VectorEmbedding(
                        doc_id=doc.doc_id,
                        embedding=embeddings[i],
                        metadata={
                            "title": doc.title,
                            "content": doc.content,
                            "doc_type": doc.doc_type,
                            "project_id": doc.project_id,
                            "metadata": doc.metadata
                        },
                        created_at=datetime.now()
                    )
                    
                    # 存储到向量数据库
                    self.vector_db[doc.doc_id] = vector_embedding
                    
                    # 保存到持久化存储
                    self._save_embedding(vector_embedding)
                    
                    indexed_count += 1
                    logger.debug(f"文档 {doc.doc_id} 已添加到RAG系统")
                    
                except Exception as e:
                    logger.error(f"添加文档 {doc.doc_id} 失败: {str(e)}")
            
            logger.info(f"批量索引完成，成功索引 {indexed_count}/{len(documents)} 个文档")
            return indexed_count
            
        except Exception as e:
            logger.error(f"批量索引文档失败: {str(e)}")
            return 0
    
    def get_document(self, doc_id: str) -> Optional[RAGDocument]:
        """获取文档"""
        try:
            if doc_id in self.vector_db:
                vector_embedding = self.vector_db[doc_id]
                return RAGDocument(
                    doc_id=vector_embedding.doc_id,
                    title=vector_embedding.metadata["title"],
                    content=vector_embedding.metadata["content"],
                    doc_type=vector_embedding.metadata["doc_type"],
                    project_id=vector_embedding.metadata["project_id"],
                    metadata=vector_embedding.metadata["metadata"],
                    embedding=vector_embedding.embedding,
                    created_at=vector_embedding.created_at
                )
            return None
        except Exception as e:
            logger.error(f"获取文档失败: {str(e)}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            if doc_id in self.vector_db:
                del self.vector_db[doc_id]
                
                # 从数据库删除
                self.db.delete("vector_embeddings", doc_id)
                
                logger.info(f"文档 {doc_id} 已删除")
                return True
            return False
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        try:
            total_documents = len(self.vector_db)
            
            # 按类型统计
            type_stats = {}
            for vector_embedding in self.vector_db.values():
                doc_type = vector_embedding.metadata.get("doc_type", "unknown")
                type_stats[doc_type] = type_stats.get(doc_type, 0) + 1
            
            # 按项目统计
            project_stats = {}
            for vector_embedding in self.vector_db.values():
                project_id = vector_embedding.metadata.get("project_id", "unknown")
                project_stats[project_id] = project_stats.get(project_id, 0) + 1
            
            return {
                "total_documents": total_documents,
                "type_distribution": type_stats,
                "project_distribution": project_stats,
                "embedding_dimension": self.embedding_dim,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取系统统计信息失败: {str(e)}")
            return {}
    
    def load_pmbok_documents(self, pmbok_dir: str = "PMBOK第七版中英文资料") -> bool:
        """加载PMBOK文档并解析页码信息"""
        try:
            # 构建文件路径
            full_md_path = os.path.join(pmbok_dir, "0- PMBOK指南 第七版_中文版.pdf-3bf8755e-73b1-4670-863e-8a3846f244be", "full.md")
            layout_json_path = os.path.join(pmbok_dir, "0- PMBOK指南 第七版_中文版.pdf-3bf8755e-73b1-4670-863e-8a3846f244be", "layout.json")
            
            if not os.path.exists(full_md_path) or not os.path.exists(layout_json_path):
                logger.error(f"PMBOK文档文件不存在: {full_md_path} 或 {layout_json_path}")
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
            
            logger.info(f"成功加载{len(self.pmbok_documents)}个PMBOK文档块")
            return True
            
        except Exception as e:
            logger.error(f"加载PMBOK文档失败: {str(e)}")
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
            # 查找章节内容在哪个页面中出现
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
            logger.error(f"提取页码失败: {str(e)}")
            return 1
    
    def search_pmbok_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索PMBOK知识库"""
        try:
            if not self.pmbok_documents:
                logger.warning("PMBOK文档未加载，请先调用load_pmbok_documents()")
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
            logger.error(f"搜索PMBOK知识库失败: {str(e)}")
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
                logger.warning(f"移除了{len(removed_pages)}个幻觉页码引用: {removed_pages}")
            
            # 如果有效页码太少，从检索结果中添加
            if len(validated_pages) < 2 and retrieved_pages:
                for page in retrieved_pages:
                    if page not in validated_pages:
                        validated_pages.append(page)
                        if len(validated_pages) >= 2:
                            break
            
            return validated_pages
            
        except Exception as e:
            logger.error(f"验证页码引用失败: {str(e)}")
            return claimed_pages


# 创建全局服务实例
rag_system = RAGSystem()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析RAG系统的chunk分块情况
"""

import json
import os
from typing import Dict, List
from collections import Counter

def analyze_chunks():
    """分析RAG系统的chunk分块情况"""
    print("🧩 分析RAG系统chunk分块情况...")
    
    # 构建文件路径
    pmbok_dir = "PMBOK第七版中英文资料"
    full_md_path = os.path.join(pmbok_dir, "0- PMBOK指南 第七版_中文版.pdf-3bf8755e-73b1-4670-863e-8a3846f244be", "full.md")
    
    if not os.path.exists(full_md_path):
        print(f"❌ 文件不存在: {full_md_path}")
        return
    
    # 读取完整文档内容
    with open(full_md_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # 按章节分割内容
    sections = split_pmbok_sections(full_content)
    
    # 分析chunk统计信息
    print(f"\n📊 Chunk统计信息:")
    print(f"   总chunk数量: {len(sections)}")
    
    # 长度分析
    lengths = [len(content) for content in sections.values()]
    lengths.sort()
    
    print(f"   最短chunk: {min(lengths)} 字符")
    print(f"   最长chunk: {max(lengths)} 字符")
    print(f"   平均长度: {sum(lengths)/len(lengths):.0f} 字符")
    print(f"   中位数长度: {lengths[len(lengths)//2]} 字符")
    
    # 长度分布
    print(f"\n📈 长度分布:")
    length_ranges = [
        (0, 500, "很短"),
        (500, 1000, "短"),
        (1000, 2000, "中等"),
        (2000, 5000, "长"),
        (5000, 8192, "很长"),
        (8192, float('inf'), "超长")
    ]
    
    for min_len, max_len, label in length_ranges:
        count = sum(1 for length in lengths if min_len <= length < max_len)
        percentage = count / len(lengths) * 100
        max_len_str = '∞' if max_len == float('inf') else str(max_len)
        print(f"   {label:4s} ({min_len:4d}-{max_len_str:>4s}字符): {count:3d}个 ({percentage:5.1f}%)")
    
    # 超长chunk详情
    print(f"\n⚠️ 超长chunk详情 (>8192字符):")
    long_chunks = [(name, len(content)) for name, content in sections.items() if len(content) > 8192]
    long_chunks.sort(key=lambda x: x[1], reverse=True)
    
    for name, length in long_chunks:
        print(f"   {name[:50]:<50} {length:>6}字符 (超出{length-8192:>4}字符)")
    
    # 最短chunk详情
    print(f"\n📝 最短chunk详情 (<500字符):")
    short_chunks = [(name, len(content)) for name, content in sections.items() if len(content) < 500]
    short_chunks.sort(key=lambda x: x[1])
    
    for name, length in short_chunks[:10]:  # 只显示前10个
        print(f"   {name[:50]:<50} {length:>6}字符")
    
    # 章节类型分析
    print(f"\n📚 章节类型分析:")
    chapter_types = analyze_chapter_types(sections)
    for chapter_type, count in chapter_types.most_common():
        print(f"   {chapter_type:<20} {count:>3}个")
    
    # 页码分布
    print(f"\n📄 页码分布分析:")
    page_ranges = analyze_page_ranges(sections)
    for page_range, count in page_ranges.items():
        print(f"   {page_range:<15} {count:>3}个chunk")
    
    # 内容质量分析
    print(f"\n🔍 内容质量分析:")
    quality_stats = analyze_content_quality(sections)
    print(f"   包含表格的chunk: {quality_stats['has_tables']}个")
    print(f"   包含列表的chunk: {quality_stats['has_lists']}个")
    print(f"   包含代码的chunk: {quality_stats['has_code']}个")
    print(f"   纯文本chunk: {quality_stats['plain_text']}个")

def split_pmbok_sections(content: str) -> Dict[str, str]:
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

def analyze_chapter_types(sections: Dict[str, str]) -> Counter:
    """分析章节类型"""
    chapter_types = Counter()
    
    for section_name in sections.keys():
        if section_name.startswith('X'):
            chapter_types['附录'] += 1
        elif section_name.startswith('3.'):
            chapter_types['定义'] += 1
        elif section_name.startswith('4.'):
            chapter_types['方法工具'] += 1
        elif '原则' in section_name:
            chapter_types['原则'] += 1
        elif '绩效域' in section_name:
            chapter_types['绩效域'] += 1
        elif '敏捷' in section_name or '适应' in section_name:
            chapter_types['敏捷管理'] += 1
        elif '风险' in section_name:
            chapter_types['风险管理'] += 1
        elif '干系人' in section_name:
            chapter_types['干系人管理'] += 1
        else:
            chapter_types['其他'] += 1
    
    return chapter_types

def analyze_page_ranges(sections: Dict[str, str]) -> Dict[str, int]:
    """分析页码分布"""
    # 这里简化处理，实际应该从layout.json中获取真实页码
    page_ranges = {
        "1-50页": 0,
        "51-100页": 0,
        "101-200页": 0,
        "201-300页": 0,
        "300页以上": 0
    }
    
    # 由于没有真实页码，这里用chunk索引模拟
    for i, (name, content) in enumerate(sections.items()):
        if i < 50:
            page_ranges["1-50页"] += 1
        elif i < 100:
            page_ranges["51-100页"] += 1
        elif i < 200:
            page_ranges["101-200页"] += 1
        elif i < 300:
            page_ranges["201-300页"] += 1
        else:
            page_ranges["300页以上"] += 1
    
    return page_ranges

def analyze_content_quality(sections: Dict[str, str]) -> Dict[str, int]:
    """分析内容质量"""
    stats = {
        'has_tables': 0,
        'has_lists': 0,
        'has_code': 0,
        'plain_text': 0
    }
    
    for content in sections.values():
        if '<table>' in content or '|' in content:
            stats['has_tables'] += 1
        elif content.count('- ') > 3 or content.count('* ') > 3:
            stats['has_lists'] += 1
        elif '```' in content or '`' in content:
            stats['has_code'] += 1
        else:
            stats['plain_text'] += 1
    
    return stats

if __name__ == "__main__":
    try:
        analyze_chunks()
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

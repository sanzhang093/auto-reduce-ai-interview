#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析PMBOK文档中哪些章节内容超过了8192字符限制
"""

import json
import os
from typing import Dict, List

def analyze_pmbok_text_length():
    """分析PMBOK文档的文本长度"""
    print("🔍 分析PMBOK文档文本长度...")
    
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
    
    # 分析每个章节的长度
    long_sections = []
    total_sections = len(sections)
    
    print(f"\n📊 总共{total_sections}个章节，分析文本长度...")
    
    for section_name, section_content in sections.items():
        content_length = len(section_content)
        
        if content_length > 8192:
            long_sections.append({
                'section': section_name,
                'length': content_length,
                'preview': section_content[:200] + "..." if len(section_content) > 200 else section_content
            })
    
    # 显示结果
    if long_sections:
        print(f"\n⚠️ 发现{len(long_sections)}个章节超过8192字符限制:")
        print("=" * 80)
        
        for i, section in enumerate(long_sections, 1):
            print(f"\n{i}. 章节: {section['section']}")
            print(f"   长度: {section['length']} 字符 (超出 {section['length'] - 8192} 字符)")
            print(f"   内容预览: {section['preview']}")
            print("-" * 60)
    else:
        print("✅ 所有章节都在8192字符限制内")
    
    # 统计信息
    print(f"\n📈 统计信息:")
    print(f"   总章节数: {total_sections}")
    print(f"   超长章节数: {len(long_sections)}")
    print(f"   超长比例: {len(long_sections)/total_sections*100:.1f}%")
    
    # 显示最长的几个章节
    all_sections = [(name, len(content)) for name, content in sections.items()]
    all_sections.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📋 最长的10个章节:")
    for i, (name, length) in enumerate(all_sections[:10], 1):
        status = "⚠️ 超长" if length > 8192 else "✅ 正常"
        print(f"   {i:2d}. {name[:50]:<50} {length:>6}字符 {status}")

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

if __name__ == "__main__":
    try:
        analyze_pmbok_text_length()
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

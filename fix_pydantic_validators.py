#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复Pydantic v2兼容性问题
将@validator替换为@field_validator并添加@classmethod
"""

import os
import re

def fix_validator_in_file(file_path):
    """修复单个文件中的validator"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换@validator为@field_validator
        content = re.sub(r'@validator\(', '@field_validator(', content)
        
        # 在@field_validator后面添加@classmethod
        # 匹配@field_validator(...)后面跟着def的情况
        pattern = r'(@field_validator\([^)]+\))\n(\s+)def\s+(\w+)\s*\(cls,'
        replacement = r'\1\n\2@classmethod\n\2def \3(cls,'
        content = re.sub(pattern, replacement, content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已修复: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {str(e)}")
        return False

def main():
    """主函数"""
    models_dir = "app/models"
    
    # 需要修复的文件列表
    files_to_fix = [
        "resource.py",
        "change_request.py", 
        "user.py",
        "project_metrics.py",
        "issue.py",
        "risk.py",
        "milestone.py",
        "task.py",
        "project.py"
    ]
    
    print("🔧 开始批量修复Pydantic v2兼容性问题...")
    
    success_count = 0
    for filename in files_to_fix:
        file_path = os.path.join(models_dir, filename)
        if os.path.exists(file_path):
            if fix_validator_in_file(file_path):
                success_count += 1
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print(f"\n🎉 修复完成！成功修复 {success_count}/{len(files_to_fix)} 个文件")

if __name__ == "__main__":
    main()

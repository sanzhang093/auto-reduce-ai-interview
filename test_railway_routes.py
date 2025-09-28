#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Railway路由配置
"""

import os
import sys

def test_file_existence():
    """测试文件是否存在"""
    html_files = [
        "gantt_visualization.html",
        "project_report_visualization.html", 
        "knowledge_management.html",
        "report_visualization.html",
        "test_connection.html",
        "ai_chat_interface_railway.html"
    ]
    
    print("🔍 检查HTML文件是否存在:")
    for file in html_files:
        exists = os.path.exists(file)
        size = os.path.getsize(file) if exists else 0
        print(f"  {file}: {'✅' if exists else '❌'} ({size} bytes)")
    
    print(f"\n📁 当前工作目录: {os.getcwd()}")
    print(f"📁 目录内容:")
    for item in os.listdir("."):
        if item.endswith('.html'):
            print(f"  📄 {item}")

def test_import_deploy():
    """测试deploy_railway_v002.py导入"""
    try:
        print("\n🔍 测试deploy_railway_v002.py导入:")
        import deploy_railway_v002
        print("  ✅ 导入成功")
        
        # 检查app对象
        app = deploy_railway_v002.app
        print(f"  ✅ FastAPI应用对象: {app}")
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"  📋 注册的路由:")
        for route in routes:
            print(f"    {route}")
            
    except Exception as e:
        print(f"  ❌ 导入失败: {str(e)}")

if __name__ == "__main__":
    test_file_existence()
    test_import_deploy()


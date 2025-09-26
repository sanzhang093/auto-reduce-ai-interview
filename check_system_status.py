#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查系统启动状态
"""

import requests
import time
import subprocess
import sys

def check_api_service():
    """检查API服务状态"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API服务运行正常")
            print(f"   状态: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ API服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API服务连接失败: {str(e)}")
        return False

def check_web_service():
    """检查Web服务状态"""
    try:
        response = requests.get("http://localhost:8081/ai_chat_interface.html", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务运行正常")
            return True
        else:
            print(f"❌ Web服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Web服务连接失败: {str(e)}")
        return False

def check_ports():
    """检查端口占用情况"""
    try:
        # 检查8000端口
        result_8000 = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':8000' in result_8000.stdout:
            print("✅ 端口8000已占用（API服务）")
        else:
            print("❌ 端口8000未占用")
        
        # 检查8081端口
        if ':8081' in result_8000.stdout:
            print("✅ 端口8081已占用（Web服务）")
        else:
            print("❌ 端口8081未占用")
            
    except Exception as e:
        print(f"❌ 端口检查失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 AI管理辅助系统 - 启动状态检查")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 检查端口
    print("\n📡 检查端口占用情况:")
    check_ports()
    
    # 检查API服务
    print("\n🔧 检查API服务:")
    api_ok = check_api_service()
    
    # 检查Web服务
    print("\n🌐 检查Web服务:")
    web_ok = check_web_service()
    
    # 总结
    print("\n" + "=" * 50)
    if api_ok and web_ok:
        print("🎉 系统启动成功！")
        print("\n📍 访问地址:")
        print("   🤖 AI聊天界面: http://localhost:8081/ai_chat_interface.html")
        print("   📊 项目管理界面: http://localhost:8081/web_interface.html")
        print("   📚 API文档: http://localhost:8000/docs")
        print("\n💡 功能特色:")
        print("   🎯 专家建议 - 基于PMBOK第七版的专业指导")
        print("   🧠 知识管理 - 智能知识提取和分类")
        print("   📊 数据分析 - 9个专业数据Functions")
        print("   🔍 RAG检索 - PMBOK专业知识检索")
    else:
        print("❌ 系统启动失败，请检查服务状态")
        if not api_ok:
            print("   - API服务未正常启动")
        if not web_ok:
            print("   - Web服务未正常启动")

if __name__ == "__main__":
    main()




"""
启动Web界面服务器
"""
import http.server
import socketserver
import webbrowser
import os
import threading
import time

def start_web_server():
    """启动Web服务器"""
    PORT = 8081
    
    # 切换到包含HTML文件的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Web界面服务器启动成功!")
        print(f"📍 AI聊天界面: http://localhost:{PORT}/ai_chat_interface.html")
        print(f"📍 甘特图可视化: http://localhost:{PORT}/gantt_visualization.html")
        print(f"📍 项目报告可视化: http://localhost:{PORT}/project_report_visualization.html")
        print(f"📍 周报月报可视化: http://localhost:{PORT}/report_visualization.html")
        print(f"📍 知识管理系统: http://localhost:{PORT}/knowledge_management.html")
        print(f"📍 传统界面: http://localhost:{PORT}/web_interface_fixed.html")
        print(f"📱 移动端: http://localhost:{PORT}/ai_chat_interface.html")
        print("=" * 50)
        print("💡 提示: 请确保API服务正在运行 (http://localhost:8000)")
        print("🔄 按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 自动打开浏览器
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{PORT}/ai_chat_interface.html')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    start_web_server()

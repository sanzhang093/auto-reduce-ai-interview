"""
简化的测试启动脚本
"""
import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("🚀 启动自动减负AI应用架构...")
    print("📋 应用名称: 自动减负AI应用架构")
    print("📋 应用版本: 1.0.0")
    print("🌐 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("请检查依赖是否正确安装")

if __name__ == "__main__":
    main()

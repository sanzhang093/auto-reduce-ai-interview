"""
测试运行脚本
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_root)
        end_time = time.time()
        
        print(f"⏱️  执行时间: {end_time - start_time:.2f} 秒")
        print(f"📊 返回码: {result.returncode}")
        
        if result.stdout:
            print(f"📤 输出:\n{result.stdout}")
        
        if result.stderr:
            print(f"⚠️  错误:\n{result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ {description} 成功完成")
        else:
            print(f"❌ {description} 失败")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行 {description} 时发生异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🧪 自动减负AI应用架构 - 测试套件")
    print("=" * 60)
    
    # 检查pytest是否安装
    try:
        import pytest
        print("✅ pytest 已安装")
    except ImportError:
        print("❌ pytest 未安装，请运行: pip install pytest")
        return False
    
    # 检查其他测试依赖
    try:
        import requests
        print("✅ requests 已安装")
    except ImportError:
        print("❌ requests 未安装，请运行: pip install requests")
        return False
    
    test_results = []
    
    # 1. 运行单元测试
    success = run_command(
        "python -m pytest tests/test_models.py -v --tb=short",
        "单元测试 - 数据模型测试"
    )
    test_results.append(("单元测试", success))
    
    # 2. 运行服务测试
    success = run_command(
        "python -m pytest tests/test_services.py -v --tb=short",
        "服务测试 - 服务层测试"
    )
    test_results.append(("服务测试", success))
    
    # 3. 运行集成测试
    success = run_command(
        "python -m pytest tests/test_integration.py -v --tb=short",
        "集成测试 - 集成功能测试"
    )
    test_results.append(("集成测试", success))
    
    # 4. 运行性能测试
    success = run_command(
        "python -m pytest tests/test_performance.py -v --tb=short",
        "性能测试 - 性能和并发测试"
    )
    test_results.append(("性能测试", success))
    
    # 5. 运行所有测试
    success = run_command(
        "python -m pytest tests/ -v --tb=short --durations=10",
        "完整测试套件 - 所有测试"
    )
    test_results.append(("完整测试", success))
    
    # 6. 生成测试报告
    success = run_command(
        "python -m pytest tests/ --html=test_report.html --self-contained-html",
        "生成HTML测试报告"
    )
    test_results.append(("测试报告", success))
    
    # 7. 运行代码覆盖率测试
    try:
        import coverage
        success = run_command(
            "coverage run -m pytest tests/ && coverage report && coverage html",
            "代码覆盖率测试"
        )
        test_results.append(("覆盖率测试", success))
    except ImportError:
        print("⚠️  coverage 未安装，跳过覆盖率测试")
        test_results.append(("覆盖率测试", False))
    
    # 8. 运行阶段测试
    print(f"\n{'='*60}")
    print("🎯 运行阶段测试")
    print(f"{'='*60}")
    
    # 第一阶段测试
    success = run_command(
        "python test_phase1.py",
        "第一阶段测试 - 基础架构测试"
    )
    test_results.append(("第一阶段测试", success))
    
    # 第二阶段测试
    success = run_command(
        "python test_phase2.py",
        "第二阶段测试 - 核心功能测试"
    )
    test_results.append(("第二阶段测试", success))
    
    # 第三阶段测试
    success = run_command(
        "python test_phase3.py",
        "第三阶段测试 - AI集成测试"
    )
    test_results.append(("第三阶段测试", success))
    
    # 显示测试结果总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print(f"{'='*60}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
第四阶段功能测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cache_service import cache_service
from app.services.concurrency_service import concurrency_service
from app.services.monitoring_service import monitoring_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_cache_service():
    """测试缓存服务"""
    print("=== 测试缓存服务 ===")
    
    try:
        # 测试基本缓存操作
        print("测试基本缓存操作...")
        
        # 设置缓存
        cache_service.set("test_key", "test_value", ttl=60)
        print("✅ 缓存设置成功")
        
        # 获取缓存
        value = cache_service.get("test_key")
        assert value == "test_value"
        print("✅ 缓存获取成功")
        
        # 测试缓存统计
        stats = cache_service.get_stats()
        print(f"缓存统计: {stats}")
        
        # 测试缓存清理
        cache_service.cleanup_expired()
        print("✅ 缓存清理完成")
        
        # 测试缓存清空
        cache_service.clear()
        print("✅ 缓存清空完成")
        
        print("✅ 缓存服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 缓存服务测试失败: {str(e)}")
        return False


def test_concurrency_service():
    """测试并发服务"""
    print("\n=== 测试并发服务 ===")
    
    try:
        # 测试并发执行
        print("测试并发执行...")
        
        def test_function(x):
            import time
            time.sleep(0.1)  # 模拟耗时操作
            return x * 2
        
        # 测试并发执行
        args_list = [(i,) for i in range(10)]
        results = concurrency_service.execute_concurrent(test_function, args_list)
        
        assert len(results) == 10
        assert results[0] == 0
        assert results[5] == 10
        print("✅ 并发执行测试通过")
        
        # 测试批量处理
        print("测试批量处理...")
        items = list(range(25))
        batch_results = concurrency_service.batch_process(items, batch_size=10)
        
        assert len(batch_results) == 25
        print("✅ 批量处理测试通过")
        
        # 测试并行映射
        print("测试并行映射...")
        map_results = concurrency_service.parallel_map(lambda x: x * 3, list(range(10)))
        
        assert len(map_results) == 10
        assert map_results[0] == 0
        assert map_results[3] == 9
        print("✅ 并行映射测试通过")
        
        print("✅ 并发服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 并发服务测试失败: {str(e)}")
        return False


def test_monitoring_service():
    """测试监控服务"""
    print("\n=== 测试监控服务 ===")
    
    try:
        # 测试系统指标收集
        print("测试系统指标收集...")
        system_metrics = monitoring_service.collect_system_metrics()
        
        assert system_metrics.cpu_percent >= 0
        assert system_metrics.memory_percent >= 0
        assert system_metrics.disk_percent >= 0
        print(f"系统指标: CPU {system_metrics.cpu_percent}%, 内存 {system_metrics.memory_percent}%, 磁盘 {system_metrics.disk_percent}%")
        
        # 测试应用指标收集
        print("测试应用指标收集...")
        app_metrics = monitoring_service.collect_application_metrics()
        
        assert app_metrics.request_count >= 0
        assert app_metrics.error_count >= 0
        assert app_metrics.response_time_avg >= 0
        print(f"应用指标: 请求 {app_metrics.request_count}, 错误 {app_metrics.error_count}, 响应时间 {app_metrics.response_time_avg}s")
        
        # 测试告警检查
        print("测试告警检查...")
        alerts = monitoring_service.check_alerts(system_metrics, app_metrics)
        print(f"发现 {len(alerts)} 个告警")
        
        # 测试健康状态
        print("测试健康状态...")
        health_status = monitoring_service.get_health_status()
        
        assert "status" in health_status
        assert "health_score" in health_status
        print(f"健康状态: {health_status['status']}, 健康分数: {health_status['health_score']}")
        
        # 测试指标摘要
        print("测试指标摘要...")
        summary = monitoring_service.get_metrics_summary(24)
        
        assert "system_metrics" in summary
        assert "application_metrics" in summary
        print("✅ 指标摘要获取成功")
        
        # 测试活跃告警
        print("测试活跃告警...")
        active_alerts = monitoring_service.get_active_alerts()
        print(f"活跃告警数量: {len(active_alerts)}")
        
        # 测试告警历史
        print("测试告警历史...")
        alert_history = monitoring_service.get_alert_history(24)
        print(f"告警历史数量: {len(alert_history)}")
        
        print("✅ 监控服务测试通过")
        return True
    except Exception as e:
        print(f"❌ 监控服务测试失败: {str(e)}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n=== 测试集成功能 ===")
    
    try:
        # 测试缓存与监控集成
        print("测试缓存与监控集成...")
        
        # 设置缓存
        cache_service.set("integration_test", "test_value", ttl=60)
        
        # 收集监控指标
        system_metrics = monitoring_service.collect_system_metrics()
        app_metrics = monitoring_service.collect_application_metrics()
        
        # 检查告警
        alerts = monitoring_service.check_alerts(system_metrics, app_metrics)
        
        # 获取健康状态
        health_status = monitoring_service.get_health_status()
        
        print(f"集成测试完成: 缓存命中率 {app_metrics.cache_hit_rate:.2%}, 健康状态 {health_status['status']}")
        
        # 测试并发与监控集成
        print("测试并发与监控集成...")
        
        def monitoring_task(x):
            # 模拟监控任务
            system_metrics = monitoring_service.collect_system_metrics()
            return system_metrics.cpu_percent
        
        # 并发执行监控任务
        args_list = [(i,) for i in range(5)]
        results = concurrency_service.execute_concurrent(monitoring_task, args_list)
        
        assert len(results) == 5
        print(f"并发监控任务完成: {len(results)} 个任务")
        
        # 测试缓存与并发集成
        print("测试缓存与并发集成...")
        
        def cache_task(x):
            # 模拟缓存操作
            cache_service.set(f"concurrent_key_{x}", f"value_{x}", ttl=60)
            return cache_service.get(f"concurrent_key_{x}")
        
        # 并发执行缓存任务
        args_list = [(i,) for i in range(10)]
        results = concurrency_service.execute_concurrent(cache_task, args_list)
        
        assert len(results) == 10
        print(f"并发缓存任务完成: {len(results)} 个任务")
        
        print("✅ 集成功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 集成功能测试失败: {str(e)}")
        return False


def test_performance():
    """测试性能"""
    print("\n=== 测试性能 ===")
    
    try:
        import time
        
        # 测试缓存性能
        print("测试缓存性能...")
        start_time = time.time()
        
        for i in range(1000):
            cache_service.set(f"perf_key_{i}", f"value_{i}", ttl=60)
        
        cache_time = time.time() - start_time
        print(f"缓存性能: 1000次设置操作耗时 {cache_time:.3f} 秒")
        
        # 测试并发性能
        print("测试并发性能...")
        start_time = time.time()
        
        def perf_task(x):
            import time
            time.sleep(0.01)  # 模拟10ms任务
            return x * 2
        
        args_list = [(i,) for i in range(100)]
        results = concurrency_service.execute_concurrent(perf_task, args_list)
        
        concurrency_time = time.time() - start_time
        print(f"并发性能: 100个任务耗时 {concurrency_time:.3f} 秒")
        
        # 测试监控性能
        print("测试监控性能...")
        start_time = time.time()
        
        for i in range(100):
            system_metrics = monitoring_service.collect_system_metrics()
            app_metrics = monitoring_service.collect_application_metrics()
            monitoring_service.check_alerts(system_metrics, app_metrics)
        
        monitoring_time = time.time() - start_time
        print(f"监控性能: 100次监控操作耗时 {monitoring_time:.3f} 秒")
        
        print("✅ 性能测试通过")
        return True
    except Exception as e:
        print(f"❌ 性能测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始第四阶段功能测试...")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_cache_service())
    test_results.append(test_concurrency_service())
    test_results.append(test_monitoring_service())
    test_results.append(test_integration())
    test_results.append(test_performance())
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 第四阶段功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

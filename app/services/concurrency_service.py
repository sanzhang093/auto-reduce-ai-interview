"""
并发优化服务
"""
import asyncio
import threading
from typing import Any, Callable, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import wraps
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConcurrencyService:
    """并发优化服务"""
    
    def __init__(self, max_workers: int = 10):
        """初始化并发服务"""
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
        logger.info(f"并发服务初始化完成，最大工作线程数: {max_workers}")
    
    def execute_concurrent(self, func: Callable, args_list: List[tuple], 
                          use_processes: bool = False) -> List[Any]:
        """并发执行函数"""
        try:
            if use_processes:
                # 使用进程池
                with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(func, *args) for args in args_list]
                    results = [future.result() for future in as_completed(futures)]
            else:
                # 使用线程池
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(func, *args) for args in args_list]
                    results = [future.result() for future in as_completed(futures)]
            
            logger.info(f"并发执行完成，共处理 {len(args_list)} 个任务")
            return results
        except Exception as e:
            logger.error(f"并发执行失败: {str(e)}")
            raise
    
    async def execute_async_concurrent(self, func: Callable, args_list: List[tuple]) -> List[Any]:
        """异步并发执行函数"""
        try:
            async def async_wrapper(args):
                async with self.semaphore:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args)
                    else:
                        # 在线程池中运行同步函数
                        loop = asyncio.get_event_loop()
                        return await loop.run_in_executor(self.thread_pool, func, *args)
            
            tasks = [async_wrapper(args) for args in args_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤异常结果
            valid_results = [r for r in results if not isinstance(r, Exception)]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            if exceptions:
                logger.warning(f"并发执行中有 {len(exceptions)} 个异常")
            
            logger.info(f"异步并发执行完成，共处理 {len(args_list)} 个任务")
            return valid_results
        except Exception as e:
            logger.error(f"异步并发执行失败: {str(e)}")
            raise
    
    def batch_process(self, items: List[Any], batch_size: int = 10, 
                     func: Optional[Callable] = None) -> List[Any]:
        """批量处理"""
        try:
            results = []
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                if func:
                    batch_results = [func(item) for item in batch]
                else:
                    batch_results = batch
                
                results.extend(batch_results)
            
            logger.info(f"批量处理完成，共处理 {len(items)} 个项目，批次大小: {batch_size}")
            return results
        except Exception as e:
            logger.error(f"批量处理失败: {str(e)}")
            raise
    
    def parallel_map(self, func: Callable, items: List[Any], 
                    max_workers: Optional[int] = None) -> List[Any]:
        """并行映射"""
        try:
            workers = max_workers or self.max_workers
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                results = list(executor.map(func, items))
            
            logger.info(f"并行映射完成，共处理 {len(items)} 个项目")
            return results
        except Exception as e:
            logger.error(f"并行映射失败: {str(e)}")
            raise
    
    def shutdown(self):
        """关闭并发服务"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logger.info("并发服务已关闭")


def concurrent_execution(max_workers: int = 10, use_processes: bool = False):
    """并发执行装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查是否有需要并发处理的数据
            if 'items' in kwargs and isinstance(kwargs['items'], list):
                items = kwargs['items']
                if len(items) > 1:
                    # 并发处理
                    concurrency_service = ConcurrencyService(max_workers=max_workers)
                    args_list = [(item,) for item in items]
                    results = concurrency_service.execute_concurrent(func, args_list, use_processes)
                    return results
            
            # 单线程执行
            return func(*args, **kwargs)
        return wrapper
    return decorator


def async_concurrent_execution(max_workers: int = 10):
    """异步并发执行装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查是否有需要并发处理的数据
            if 'items' in kwargs and isinstance(kwargs['items'], list):
                items = kwargs['items']
                if len(items) > 1:
                    # 异步并发处理
                    concurrency_service = ConcurrencyService(max_workers=max_workers)
                    args_list = [(item,) for item in items]
                    results = await concurrency_service.execute_async_concurrent(func, args_list)
                    return results
            
            # 单线程执行
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def batch_processing(batch_size: int = 10):
    """批量处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查是否有需要批量处理的数据
            if 'items' in kwargs and isinstance(kwargs['items'], list):
                items = kwargs['items']
                if len(items) > batch_size:
                    # 批量处理
                    concurrency_service = ConcurrencyService()
                    results = concurrency_service.batch_process(items, batch_size, func)
                    return results
            
            # 单次处理
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_calls: int = 100, time_window: int = 60):
        """初始化速率限制器"""
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """检查是否允许调用"""
        with self.lock:
            now = time.time()
            
            # 清理过期的调用记录
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # 检查是否超过限制
            if len(self.calls) >= self.max_calls:
                return False
            
            # 记录当前调用
            self.calls.append(now)
            return True
    
    def wait_if_needed(self):
        """如果需要则等待"""
        while not self.is_allowed():
            time.sleep(0.1)


def rate_limit(max_calls: int = 100, time_window: int = 60):
    """速率限制装饰器"""
    def decorator(func):
        limiter = RateLimiter(max_calls, time_window)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """初始化熔断器"""
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """执行函数调用"""
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("熔断器开启，拒绝调用")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _on_success(self):
        """成功回调"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """失败回调"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """熔断器装饰器"""
    def decorator(func):
        breaker = CircuitBreaker(failure_threshold, recovery_timeout)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


class ConnectionPool:
    """连接池"""
    
    def __init__(self, max_connections: int = 10):
        """初始化连接池"""
        self.max_connections = max_connections
        self.connections = []
        self.available_connections = []
        self.lock = threading.Lock()
    
    def get_connection(self):
        """获取连接"""
        with self.lock:
            if self.available_connections:
                return self.available_connections.pop()
            elif len(self.connections) < self.max_connections:
                # 创建新连接
                connection = self._create_connection()
                self.connections.append(connection)
                return connection
            else:
                # 等待可用连接
                while not self.available_connections:
                    time.sleep(0.01)
                return self.available_connections.pop()
    
    def return_connection(self, connection):
        """归还连接"""
        with self.lock:
            self.available_connections.append(connection)
    
    def _create_connection(self):
        """创建连接（子类实现）"""
        return None
    
    def close_all(self):
        """关闭所有连接"""
        with self.lock:
            for connection in self.connections:
                self._close_connection(connection)
            self.connections.clear()
            self.available_connections.clear()
    
    def _close_connection(self, connection):
        """关闭连接（子类实现）"""
        pass


# 创建全局并发服务实例
concurrency_service = ConcurrencyService(max_workers=10)

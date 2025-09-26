"""
缓存服务
"""
import json
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from functools import wraps
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CacheItem:
    """缓存项"""
    
    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl  # 生存时间（秒）
        self.access_count = 0
        self.last_accessed = datetime.now()
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl)
    
    def access(self):
        """访问缓存项"""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "ttl": self.ttl,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }


class CacheService:
    """缓存服务"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """初始化缓存服务"""
        self.cache: Dict[str, CacheItem] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
        logger.info(f"缓存服务初始化完成，最大容量: {max_size}, 默认TTL: {default_ttl}秒")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            item = self.cache[key]
            
            if item.is_expired():
                # 过期则删除
                del self.cache[key]
                self.miss_count += 1
                logger.debug(f"缓存项 {key} 已过期，已删除")
                return None
            
            # 访问缓存项
            item.access()
            self.hit_count += 1
            logger.debug(f"缓存命中: {key}")
            return item.value
        
        self.miss_count += 1
        logger.debug(f"缓存未命中: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            # 如果缓存已满，删除最旧的项
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_oldest()
            
            # 设置TTL
            cache_ttl = ttl if ttl is not None else self.default_ttl
            
            # 创建缓存项
            item = CacheItem(key, value, cache_ttl)
            self.cache[key] = item
            
            logger.debug(f"缓存设置: {key}, TTL: {cache_ttl}秒")
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {key}, 错误: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"缓存删除: {key}")
            return True
        return False
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("缓存已清空")
    
    def cleanup_expired(self):
        """清理过期缓存项"""
        expired_keys = []
        for key, item in self.cache.items():
            if item.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    def _evict_oldest(self):
        """删除最旧的缓存项"""
        if not self.cache:
            return
        
        # 找到最旧的项
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        del self.cache[oldest_key]
        logger.debug(f"删除最旧缓存项: {oldest_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def get_cache_info(self) -> List[Dict[str, Any]]:
        """获取缓存信息"""
        return [item.to_dict() for item in self.cache.values()]


def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_project_data(project_id: str, ttl: int = 1800):
    """缓存项目数据装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"project_{project_id}_{func.__name__}"
            
            # 尝试从缓存获取
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_user_data(user_id: str, ttl: int = 1800):
    """缓存用户数据装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"user_{user_id}_{func.__name__}"
            
            # 尝试从缓存获取
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_project_cache(project_id: str):
    """使项目相关缓存失效"""
    keys_to_delete = []
    for key in cache_service.cache.keys():
        if key.startswith(f"project_{project_id}_"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache_service.delete(key)
    
    logger.info(f"使项目 {project_id} 的 {len(keys_to_delete)} 个缓存项失效")


def invalidate_user_cache(user_id: str):
    """使用户相关缓存失效"""
    keys_to_delete = []
    for key in cache_service.cache.keys():
        if key.startswith(f"user_{user_id}_"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache_service.delete(key)
    
    logger.info(f"使用户 {user_id} 的 {len(keys_to_delete)} 个缓存项失效")


# 创建全局缓存服务实例
cache_service = CacheService(max_size=1000, default_ttl=3600)

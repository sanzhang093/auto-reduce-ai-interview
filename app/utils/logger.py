"""
日志配置模块
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logger():
    """设置日志配置"""
    # 移除默认处理器
    logger.remove()
    
    # 创建日志目录
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件输出格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 添加文件处理器
    logger.add(
        settings.log_file,
        format=file_format,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )
    
    # 添加错误日志文件
    error_log_file = str(Path(settings.log_file).parent / "error.log")
    logger.add(
        error_log_file,
        format=file_format,
        level="ERROR",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("日志系统初始化完成")


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger


# 初始化日志系统
setup_logger()

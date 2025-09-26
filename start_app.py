"""
应用启动脚本
"""
import uvicorn
from config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    logger.info("启动自动减负AI应用架构...")
    logger.info(f"应用名称: {settings.app_name}")
    logger.info(f"应用版本: {settings.app_version}")
    logger.info(f"服务地址: http://{settings.host}:{settings.port}")
    logger.info(f"API文档: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()

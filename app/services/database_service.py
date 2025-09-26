"""
数据库服务
"""
from typing import Any, Dict, List, Optional, Union
from app.utils.database import JSONDatabase
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        """初始化数据库服务"""
        self.db = JSONDatabase(settings.json_database_path)
        logger.info("数据库服务初始化完成")
    
    def get_database(self) -> JSONDatabase:
        """获取数据库实例"""
        return self.db
    
    def backup_database(self, backup_path: str = None) -> str:
        """备份数据库"""
        try:
            backup_file = self.db.backup(backup_path)
            logger.info(f"数据库备份完成: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"数据库备份失败: {str(e)}")
            raise
    
    def restore_database(self, backup_path: str) -> bool:
        """恢复数据库"""
        try:
            success = self.db.restore(backup_path)
            if success:
                logger.info(f"数据库恢复完成: {backup_path}")
            else:
                logger.error(f"数据库恢复失败: {backup_path}")
            return success
        except Exception as e:
            logger.error(f"数据库恢复失败: {str(e)}")
            raise
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            metadata = self.db.get_metadata()
            collections = self.db.get_collections()
            
            info = {
                "metadata": metadata,
                "collections": collections,
                "collection_counts": {}
            }
            
            # 统计各集合的记录数
            for collection in collections:
                count = self.db.count(collection)
                info["collection_counts"][collection] = count
            
            return info
        except Exception as e:
            logger.error(f"获取数据库信息失败: {str(e)}")
            raise
    
    def clear_collection(self, collection_name: str) -> bool:
        """清空集合"""
        try:
            success = self.db.clear_collection(collection_name)
            if success:
                logger.info(f"集合 {collection_name} 已清空")
            else:
                logger.warning(f"集合 {collection_name} 清空失败")
            return success
        except Exception as e:
            logger.error(f"清空集合 {collection_name} 失败: {str(e)}")
            raise
    
    def export_collection(self, collection_name: str, output_path: str = None) -> str:
        """导出集合数据"""
        try:
            export_file = self.db.export_data(collection_name, output_path)
            logger.info(f"集合 {collection_name} 数据已导出到: {export_file}")
            return export_file
        except Exception as e:
            logger.error(f"导出集合 {collection_name} 数据失败: {str(e)}")
            raise
    
    def import_collection(self, collection_name: str, items: List[Dict[str, Any]], clear_existing: bool = False) -> int:
        """导入集合数据"""
        try:
            count = self.db.import_data(collection_name, items, clear_existing)
            logger.info(f"向集合 {collection_name} 导入了 {count} 条记录")
            return count
        except Exception as e:
            logger.error(f"导入集合 {collection_name} 数据失败: {str(e)}")
            raise


# 创建全局数据库服务实例
database_service = DatabaseService()

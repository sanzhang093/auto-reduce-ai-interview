"""
JSON数据库操作类
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import threading
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JSONDatabase:
    """JSON数据库操作类"""
    
    def __init__(self, db_path: str = "./data/simulated_database.json"):
        """
        初始化JSON数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.lock = threading.RLock()  # 使用可重入锁
        self._ensure_db_file()
    
    def _ensure_db_file(self):
        """确保数据库文件存在"""
        # 创建目录
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件不存在，创建初始数据库结构
        if not self.db_path.exists():
            initial_data = {
                "projects": [],
                "tasks": [],
                "milestones": [],
                "risks": [],
                "issues": [],
                "resources": [],
                "time_tracking": [],
                "change_requests": [],
                "users": [],
                "project_metrics": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat()
                }
            }
            self._write_data(initial_data)
            logger.info(f"创建初始数据库文件: {self.db_path}")
    
    def _read_data(self) -> Dict[str, Any]:
        """读取数据库数据"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"读取数据库文件失败: {e}")
            return {}
    
    def _write_data(self, data: Dict[str, Any]):
        """写入数据库数据"""
        try:
            # 更新元数据
            if "metadata" in data:
                data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # 写入文件
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"数据库文件已更新: {self.db_path}")
        except Exception as e:
            logger.error(f"写入数据库文件失败: {e}")
            raise
    
    def _get_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """获取集合数据"""
        with self.lock:
            data = self._read_data()
            return data.get(collection_name, [])
    
    def _update_collection(self, collection_name: str, collection_data: List[Dict[str, Any]]):
        """更新集合数据"""
        with self.lock:
            data = self._read_data()
            data[collection_name] = collection_data
            self._write_data(data)
    
    def create(self, collection_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新记录
        
        Args:
            collection_name: 集合名称
            item: 要创建的记录
            
        Returns:
            创建后的记录
        """
        with self.lock:
            collection = self._get_collection(collection_name)
            
            # 添加创建时间
            item["created_at"] = datetime.now().isoformat()
            item["updated_at"] = datetime.now().isoformat()
            
            # 添加到集合
            collection.append(item)
            self._update_collection(collection_name, collection)
            
            logger.info(f"在集合 {collection_name} 中创建新记录")
            return item
    
    def read(self, collection_name: str, item_id: str = None, filters: Dict[str, Any] = None) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        读取记录
        
        Args:
            collection_name: 集合名称
            item_id: 记录ID（可选）
            filters: 过滤条件（可选）
            
        Returns:
            记录列表或单个记录
        """
        collection = self._get_collection(collection_name)
        
        if item_id:
            # 根据ID查找单个记录
            for item in collection:
                if item.get("id") == item_id or item.get(f"{collection_name[:-1]}_id") == item_id:
                    return item
            return None
        
        if filters:
            # 根据过滤条件查找记录
            filtered_items = []
            for item in collection:
                match = True
                for key, value in filters.items():
                    if item.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_items.append(item)
            return filtered_items
        
        return collection
    
    def update(self, collection_name: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新记录
        
        Args:
            collection_name: 集合名称
            item_id: 记录ID
            updates: 更新数据
            
        Returns:
            更新后的记录或None
        """
        with self.lock:
            collection = self._get_collection(collection_name)
            
            for i, item in enumerate(collection):
                if item.get("id") == item_id or item.get(f"{collection_name[:-1]}_id") == item_id:
                    # 更新记录
                    item.update(updates)
                    item["updated_at"] = datetime.now().isoformat()
                    collection[i] = item
                    self._update_collection(collection_name, collection)
                    
                    logger.info(f"更新集合 {collection_name} 中的记录 {item_id}")
                    return item
            
            logger.warning(f"在集合 {collection_name} 中未找到记录 {item_id}")
            return None
    
    def delete(self, collection_name: str, item_id: str) -> bool:
        """
        删除记录
        
        Args:
            collection_name: 集合名称
            item_id: 记录ID
            
        Returns:
            是否删除成功
        """
        with self.lock:
            collection = self._get_collection(collection_name)
            
            for i, item in enumerate(collection):
                if item.get("id") == item_id or item.get(f"{collection_name[:-1]}_id") == item_id:
                    del collection[i]
                    self._update_collection(collection_name, collection)
                    
                    logger.info(f"从集合 {collection_name} 中删除记录 {item_id}")
                    return True
            
            logger.warning(f"在集合 {collection_name} 中未找到记录 {item_id}")
            return False
    
    def count(self, collection_name: str, filters: Dict[str, Any] = None) -> int:
        """
        统计记录数量
        
        Args:
            collection_name: 集合名称
            filters: 过滤条件（可选）
            
        Returns:
            记录数量
        """
        collection = self._get_collection(collection_name)
        
        if not filters:
            return len(collection)
        
        count = 0
        for item in collection:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                count += 1
        
        return count
    
    def search(self, collection_name: str, search_term: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        搜索记录
        
        Args:
            collection_name: 集合名称
            search_term: 搜索词
            search_fields: 搜索字段列表（可选）
            
        Returns:
            匹配的记录列表
        """
        collection = self._get_collection(collection_name)
        results = []
        
        for item in collection:
            if search_fields:
                # 在指定字段中搜索
                for field in search_fields:
                    if field in item and search_term.lower() in str(item[field]).lower():
                        results.append(item)
                        break
            else:
                # 在所有字段中搜索
                for value in item.values():
                    if search_term.lower() in str(value).lower():
                        results.append(item)
                        break
        
        return results
    
    def get_by_field(self, collection_name: str, field_name: str, field_value: Any) -> List[Dict[str, Any]]:
        """
        根据字段值获取记录
        
        Args:
            collection_name: 集合名称
            field_name: 字段名
            field_value: 字段值
            
        Returns:
            匹配的记录列表
        """
        collection = self._get_collection(collection_name)
        results = []
        
        for item in collection:
            if item.get(field_name) == field_value:
                results.append(item)
        
        return results
    
    def backup(self, backup_path: str = None) -> str:
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径（可选）
            
        Returns:
            备份文件路径
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path.stem}_backup_{timestamp}.json"
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.lock:
            data = self._read_data()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据库已备份到: {backup_path}")
        return str(backup_path)
    
    def restore(self, backup_path: str) -> bool:
        """
        恢复数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否恢复成功
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self.lock:
                self._write_data(data)
            
            logger.info(f"数据库已从备份恢复: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"恢复数据库失败: {e}")
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取数据库元数据
        
        Returns:
            元数据字典
        """
        data = self._read_data()
        return data.get("metadata", {})
    
    def get_collections(self) -> List[str]:
        """
        获取所有集合名称
        
        Returns:
            集合名称列表
        """
        data = self._read_data()
        collections = []
        for key in data.keys():
            if key != "metadata":
                collections.append(key)
        return collections
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        清空集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否清空成功
        """
        with self.lock:
            data = self._read_data()
            if collection_name in data:
                data[collection_name] = []
                self._write_data(data)
                logger.info(f"已清空集合: {collection_name}")
                return True
            else:
                logger.warning(f"集合不存在: {collection_name}")
                return False
    
    def import_data(self, collection_name: str, items: List[Dict[str, Any]], clear_existing: bool = False) -> int:
        """
        导入数据到集合
        
        Args:
            collection_name: 集合名称
            items: 要导入的数据项列表
            clear_existing: 是否清空现有数据
            
        Returns:
            导入的记录数量
        """
        with self.lock:
            collection = self._get_collection(collection_name)
            
            if clear_existing:
                collection = []
            
            # 添加时间戳
            current_time = datetime.now().isoformat()
            for item in items:
                if "created_at" not in item:
                    item["created_at"] = current_time
                item["updated_at"] = current_time
            
            collection.extend(items)
            self._update_collection(collection_name, collection)
            
            logger.info(f"向集合 {collection_name} 导入了 {len(items)} 条记录")
            return len(items)
    
    def export_data(self, collection_name: str, output_path: str = None) -> str:
        """
        导出集合数据
        
        Args:
            collection_name: 集合名称
            output_path: 输出文件路径（可选）
            
        Returns:
            输出文件路径
        """
        collection = self._get_collection(collection_name)
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{collection_name}_export_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, ensure_ascii=False, indent=2)
        
        logger.info(f"集合 {collection_name} 的数据已导出到: {output_path}")
        return str(output_path)

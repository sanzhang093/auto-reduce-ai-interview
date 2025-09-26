"""
辅助工具函数
"""
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, Any, Dict
import re


def generate_id(prefix: str = "") -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一ID字符串
    """
    unique_id = str(uuid.uuid4()).replace("-", "")
    if prefix:
        return f"{prefix}-{unique_id}"
    return unique_id


def generate_hash(data: str) -> str:
    """
    生成数据哈希值
    
    Args:
        data: 要哈希的数据
        
    Returns:
        哈希值字符串
    """
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        日期时间对象或None
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def get_current_timestamp() -> str:
    """
    获取当前时间戳字符串
    
    Returns:
        ISO格式的时间戳字符串
    """
    return datetime.now(timezone.utc).isoformat()


def get_current_datetime() -> datetime:
    """
    获取当前日期时间
    
    Returns:
        当前日期时间对象
    """
    return datetime.now(timezone.utc)


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        data: 字典数据
        key: 键名，支持点号分隔的嵌套键
        default: 默认值
        
    Returns:
        获取到的值或默认值
    """
    if not isinstance(data, dict):
        return default
    
    keys = key.split('.')
    current = data
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current


def clean_string(text: str) -> str:
    """
    清理字符串，移除多余空白字符
    
    Args:
        text: 原始字符串
        
    Returns:
        清理后的字符串
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的字符串
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def convert_to_dict(obj: Any) -> Dict[str, Any]:
    """
    将对象转换为字典
    
    Args:
        obj: 要转换的对象
        
    Returns:
        字典表示
    """
    if hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, dict):
        return obj
    else:
        return {"value": str(obj)}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
        
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def extract_numbers(text: str) -> list:
    """
    从文本中提取数字
    
    Args:
        text: 文本内容
        
    Returns:
        数字列表
    """
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(match) if '.' in match else int(match) for match in matches]


def extract_dates(text: str) -> list:
    """
    从文本中提取日期
    
    Args:
        text: 文本内容
        
    Returns:
        日期列表
    """
    # 匹配常见的日期格式
    patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
    ]
    
    dates = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        dates.extend(matches)
    
    return dates

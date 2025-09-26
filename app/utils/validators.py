"""
数据验证工具
"""
import re
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ValidationError


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    if not phone:
        return False
    
    # 中国手机号格式
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串
        format_str: 日期格式
        
    Returns:
        是否有效
    """
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """
    验证日期时间格式
    
    Args:
        datetime_str: 日期时间字符串
        format_str: 日期时间格式
        
    Returns:
        是否有效
    """
    if not datetime_str:
        return False
    
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except ValueError:
        return False


def validate_id(id_str: str, prefix: str = None) -> bool:
    """
    验证ID格式
    
    Args:
        id_str: ID字符串
        prefix: 期望的前缀
        
    Returns:
        是否有效
    """
    if not id_str:
        return False
    
    # UUID格式验证
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if re.match(uuid_pattern, id_str):
        return True
    
    # 带前缀的ID格式验证
    if prefix:
        pattern = f'^{prefix}-[0-9a-f]{{32}}$'
        return bool(re.match(pattern, id_str))
    
    return False


def validate_priority(priority: str) -> bool:
    """
    验证优先级
    
    Args:
        priority: 优先级字符串
        
    Returns:
        是否有效
    """
    valid_priorities = ["低", "中", "高", "紧急"]
    return priority in valid_priorities


def validate_status(status: str, status_type: str = "task") -> bool:
    """
    验证状态
    
    Args:
        status: 状态字符串
        status_type: 状态类型 (task, project, issue, risk)
        
    Returns:
        是否有效
    """
    status_mapping = {
        "task": ["待开始", "进行中", "已完成", "已暂停", "已取消"],
        "project": ["规划中", "进行中", "暂停", "已完成", "已取消"],
        "issue": ["新建", "已分配", "进行中", "已解决", "已关闭"],
        "risk": ["已识别", "已评估", "已应对", "已关闭"]
    }
    
    valid_statuses = status_mapping.get(status_type, [])
    return status in valid_statuses


def validate_percentage(percentage: float) -> bool:
    """
    验证百分比
    
    Args:
        percentage: 百分比值
        
    Returns:
        是否有效
    """
    return 0 <= percentage <= 100


def validate_risk_level(risk_level: str) -> bool:
    """
    验证风险等级
    
    Args:
        risk_level: 风险等级字符串
        
    Returns:
        是否有效
    """
    valid_levels = ["低", "中", "高", "严重"]
    return risk_level in valid_levels


def validate_severity(severity: str) -> bool:
    """
    验证严重程度
    
    Args:
        severity: 严重程度字符串
        
    Returns:
        是否有效
    """
    valid_severities = ["低", "中", "高", "严重"]
    return severity in valid_severities


def validate_project_type(project_type: str) -> bool:
    """
    验证项目类型
    
    Args:
        project_type: 项目类型字符串
        
    Returns:
        是否有效
    """
    valid_types = ["研发项目", "实施项目", "维护项目", "咨询项目"]
    return project_type in valid_types


def validate_task_type(task_type: str) -> bool:
    """
    验证任务类型
    
    Args:
        task_type: 任务类型字符串
        
    Returns:
        是否有效
    """
    valid_types = ["开发任务", "测试任务", "文档任务", "会议任务", "评审任务"]
    return task_type in valid_types


def validate_risk_category(category: str) -> bool:
    """
    验证风险类别
    
    Args:
        category: 风险类别字符串
        
    Returns:
        是否有效
    """
    valid_categories = ["技术风险", "进度风险", "成本风险", "质量风险", "资源风险", "外部风险"]
    return category in valid_categories


def validate_issue_category(category: str) -> bool:
    """
    验证问题类别
    
    Args:
        category: 问题类别字符串
        
    Returns:
        是否有效
    """
    valid_categories = ["技术问题", "进度问题", "质量问题", "沟通问题", "资源问题", "性能问题", "外部依赖问题"]
    return category in valid_categories


def validate_resource_type(resource_type: str) -> bool:
    """
    验证资源类型
    
    Args:
        resource_type: 资源类型字符串
        
    Returns:
        是否有效
    """
    valid_types = ["人力资源", "设备资源", "材料资源", "财务资源"]
    return resource_type in valid_types


def validate_change_type(change_type: str) -> bool:
    """
    验证变更类型
    
    Args:
        change_type: 变更类型字符串
        
    Returns:
        是否有效
    """
    valid_types = ["范围变更", "时间变更", "成本变更", "质量变更", "资源变更"]
    return change_type in valid_types


def validate_pydantic_model(data: dict, model_class: BaseModel) -> tuple[bool, Optional[str]]:
    """
    验证Pydantic模型数据
    
    Args:
        data: 要验证的数据
        model_class: Pydantic模型类
        
    Returns:
        (是否有效, 错误信息)
    """
    try:
        model_class(**data)
        return True, None
    except ValidationError as e:
        error_msg = "; ".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
        return False, error_msg


def validate_required_fields(data: dict, required_fields: List[str]) -> tuple[bool, Optional[str]]:
    """
    验证必填字段
    
    Args:
        data: 要验证的数据
        required_fields: 必填字段列表
        
    Returns:
        (是否有效, 错误信息)
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, None


def validate_data_types(data: dict, field_types: dict) -> tuple[bool, Optional[str]]:
    """
    验证字段数据类型
    
    Args:
        data: 要验证的数据
        field_types: 字段类型映射
        
    Returns:
        (是否有效, 错误信息)
    """
    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                return False, f"字段 {field} 类型错误，期望 {expected_type.__name__}，实际 {type(data[field]).__name__}"
    
    return True, None


def validate_string_length(text: str, min_length: int = 0, max_length: int = None) -> bool:
    """
    验证字符串长度
    
    Args:
        text: 要验证的字符串
        min_length: 最小长度
        max_length: 最大长度
        
    Returns:
        是否有效
    """
    if text is None:
        return min_length == 0
    
    length = len(text)
    if length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True


def validate_numeric_range(value: float, min_value: float = None, max_value: float = None) -> bool:
    """
    验证数值范围
    
    Args:
        value: 要验证的数值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        是否有效
    """
    if value is None:
        return False
    
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True

"""
监控服务
"""
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from app.utils.logger import get_logger
from app.services.database_service import database_service

logger = get_logger(__name__)


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    load_average: List[float]


@dataclass
class ApplicationMetrics:
    """应用指标"""
    timestamp: datetime
    active_connections: int
    request_count: int
    error_count: int
    response_time_avg: float
    cache_hit_rate: float
    database_connections: int


@dataclass
class Alert:
    """告警"""
    alert_id: str
    alert_type: str
    severity: str  # critical, warning, info
    title: str
    message: str
    timestamp: datetime
    status: str  # active, resolved
    metadata: Dict[str, Any]


class MonitoringService:
    """监控服务"""
    
    def __init__(self):
        """初始化监控服务"""
        self.db = database_service.get_database()
        self.metrics_history = []
        self.active_alerts = {}
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time": 2.0,
            "error_rate": 0.05,
            "cache_hit_rate": 0.6
        }
        logger.info("监控服务初始化完成")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 网络统计
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent
            network_recv = network.bytes_recv
            
            # 负载平均值
            load_average = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_sent=network_sent,
                network_recv=network_recv,
                load_average=load_average
            )
            
            logger.debug(f"系统指标收集完成: CPU {cpu_percent}%, 内存 {memory_percent}%, 磁盘 {disk_percent}%")
            return metrics
        except Exception as e:
            logger.error(f"收集系统指标失败: {str(e)}")
            raise
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """收集应用指标"""
        try:
            # 模拟应用指标收集
            # 在实际应用中，这些指标应该从应用内部收集
            
            # 活跃连接数（模拟）
            active_connections = 10
            
            # 请求计数（模拟）
            request_count = 1000
            
            # 错误计数（模拟）
            error_count = 50
            
            # 平均响应时间（模拟）
            response_time_avg = 0.5
            
            # 缓存命中率（模拟）
            cache_hit_rate = 0.85
            
            # 数据库连接数（模拟）
            database_connections = 5
            
            metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                active_connections=active_connections,
                request_count=request_count,
                error_count=error_count,
                response_time_avg=response_time_avg,
                cache_hit_rate=cache_hit_rate,
                database_connections=database_connections
            )
            
            logger.debug(f"应用指标收集完成: 请求 {request_count}, 错误 {error_count}, 响应时间 {response_time_avg}s")
            return metrics
        except Exception as e:
            logger.error(f"收集应用指标失败: {str(e)}")
            raise
    
    def check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics) -> List[Alert]:
        """检查告警"""
        alerts = []
        
        try:
            # 检查CPU使用率
            if system_metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
                alert = Alert(
                    alert_id=f"cpu_high_{int(time.time())}",
                    alert_type="system",
                    severity="warning",
                    title="CPU使用率过高",
                    message=f"CPU使用率达到 {system_metrics.cpu_percent:.1f}%，超过阈值 {self.alert_thresholds['cpu_percent']}%",
                    timestamp=datetime.now(),
                    status="active",
                    metadata={"cpu_percent": system_metrics.cpu_percent, "threshold": self.alert_thresholds["cpu_percent"]}
                )
                alerts.append(alert)
            
            # 检查内存使用率
            if system_metrics.memory_percent > self.alert_thresholds["memory_percent"]:
                alert = Alert(
                    alert_id=f"memory_high_{int(time.time())}",
                    alert_type="system",
                    severity="warning",
                    title="内存使用率过高",
                    message=f"内存使用率达到 {system_metrics.memory_percent:.1f}%，超过阈值 {self.alert_thresholds['memory_percent']}%",
                    timestamp=datetime.now(),
                    status="active",
                    metadata={"memory_percent": system_metrics.memory_percent, "threshold": self.alert_thresholds["memory_percent"]}
                )
                alerts.append(alert)
            
            # 检查磁盘使用率
            if system_metrics.disk_percent > self.alert_thresholds["disk_percent"]:
                alert = Alert(
                    alert_id=f"disk_high_{int(time.time())}",
                    alert_type="system",
                    severity="critical",
                    title="磁盘空间不足",
                    message=f"磁盘使用率达到 {system_metrics.disk_percent:.1f}%，超过阈值 {self.alert_thresholds['disk_percent']}%",
                    timestamp=datetime.now(),
                    status="active",
                    metadata={"disk_percent": system_metrics.disk_percent, "threshold": self.alert_thresholds["disk_percent"]}
                )
                alerts.append(alert)
            
            # 检查响应时间
            if app_metrics.response_time_avg > self.alert_thresholds["response_time"]:
                alert = Alert(
                    alert_id=f"response_time_high_{int(time.time())}",
                    alert_type="application",
                    severity="warning",
                    title="响应时间过长",
                    message=f"平均响应时间达到 {app_metrics.response_time_avg:.2f}s，超过阈值 {self.alert_thresholds['response_time']}s",
                    timestamp=datetime.now(),
                    status="active",
                    metadata={"response_time": app_metrics.response_time_avg, "threshold": self.alert_thresholds["response_time"]}
                )
                alerts.append(alert)
            
            # 检查错误率
            error_rate = app_metrics.error_count / app_metrics.request_count if app_metrics.request_count > 0 else 0
            if error_rate > self.alert_thresholds["error_rate"]:
                alert = Alert(
                    alert_id=f"error_rate_high_{int(time.time())}",
                    alert_type="application",
                    severity="critical",
                    title="错误率过高",
                    message=f"错误率达到 {error_rate:.2%}，超过阈值 {self.alert_thresholds['error_rate']:.2%}",
                    timestamp=datetime.now(),
                    status="active",
                    metadata={"error_rate": error_rate, "threshold": self.alert_thresholds["error_rate"]}
                )
                alerts.append(alert)
            
            # 检查缓存命中率
            if app_metrics.cache_hit_rate < self.alert_thresholds["cache_hit_rate"]:
                alert = Alert(
                    alert_id=f"cache_hit_rate_low_{int(time.time())}",
                    alert_type="application",
                    severity="info",
                    title="缓存命中率过低",
                    message=f"缓存命中率为 {app_metrics.cache_hit_rate:.2%}，低于阈值 {self.alert_thresholds['cache_hit_rate']:.2%}",
                    timestamp=datetime.now(),
                    status="active",
                    metadata={"cache_hit_rate": app_metrics.cache_hit_rate, "threshold": self.alert_thresholds["cache_hit_rate"]}
                )
                alerts.append(alert)
            
            # 处理新告警
            for alert in alerts:
                self._process_alert(alert)
            
            logger.info(f"告警检查完成，发现 {len(alerts)} 个新告警")
            return alerts
        except Exception as e:
            logger.error(f"检查告警失败: {str(e)}")
            return []
    
    def _process_alert(self, alert: Alert):
        """处理告警"""
        try:
            # 检查是否已存在相同告警
            existing_alert = self.active_alerts.get(alert.alert_type)
            
            if existing_alert and existing_alert.status == "active":
                # 更新现有告警
                existing_alert.timestamp = alert.timestamp
                existing_alert.message = alert.message
                existing_alert.metadata.update(alert.metadata)
            else:
                # 添加新告警
                self.active_alerts[alert.alert_type] = alert
                
                # 保存到数据库
                self._save_alert(alert)
                
                # 发送告警通知
                self._send_alert_notification(alert)
            
            logger.info(f"告警处理完成: {alert.title}")
        except Exception as e:
            logger.error(f"处理告警失败: {str(e)}")
    
    def _save_alert(self, alert: Alert):
        """保存告警到数据库"""
        try:
            alert_data = {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status,
                "metadata": alert.metadata
            }
            
            self.db.create("alerts", alert_data)
        except Exception as e:
            logger.error(f"保存告警失败: {str(e)}")
    
    def _send_alert_notification(self, alert: Alert):
        """发送告警通知"""
        try:
            # 这里可以集成邮件、短信、钉钉等通知方式
            notification_message = f"""
告警通知:
类型: {alert.alert_type}
严重程度: {alert.severity}
标题: {alert.title}
消息: {alert.message}
时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            logger.warning(f"告警通知: {notification_message}")
            
            # 在实际应用中，这里应该发送到外部通知系统
            # 例如：发送邮件、短信、钉钉消息等
            
        except Exception as e:
            logger.error(f"发送告警通知失败: {str(e)}")
    
    def resolve_alert(self, alert_type: str):
        """解决告警"""
        try:
            if alert_type in self.active_alerts:
                alert = self.active_alerts[alert_type]
                alert.status = "resolved"
                alert.timestamp = datetime.now()
                
                # 更新数据库
                self._save_alert(alert)
                
                # 发送解决通知
                self._send_resolution_notification(alert)
                
                logger.info(f"告警已解决: {alert.title}")
        except Exception as e:
            logger.error(f"解决告警失败: {str(e)}")
    
    def _send_resolution_notification(self, alert: Alert):
        """发送解决通知"""
        try:
            notification_message = f"""
告警解决通知:
类型: {alert.alert_type}
标题: {alert.title}
解决时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            logger.info(f"告警解决通知: {notification_message}")
        except Exception as e:
            logger.error(f"发送解决通知失败: {str(e)}")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取指标摘要"""
        try:
            # 获取历史指标
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 模拟历史数据
            summary = {
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours
                },
                "system_metrics": {
                    "avg_cpu_percent": 45.2,
                    "max_cpu_percent": 78.5,
                    "avg_memory_percent": 62.3,
                    "max_memory_percent": 82.1,
                    "avg_disk_percent": 35.7,
                    "max_disk_percent": 38.2
                },
                "application_metrics": {
                    "total_requests": 50000,
                    "total_errors": 250,
                    "avg_response_time": 0.8,
                    "max_response_time": 3.2,
                    "avg_cache_hit_rate": 0.85,
                    "min_cache_hit_rate": 0.72
                },
                "alerts": {
                    "total_alerts": 5,
                    "active_alerts": 2,
                    "resolved_alerts": 3,
                    "critical_alerts": 1,
                    "warning_alerts": 4
                }
            }
            
            return summary
        except Exception as e:
            logger.error(f"获取指标摘要失败: {str(e)}")
            return {}
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        try:
            active_alerts = []
            for alert in self.active_alerts.values():
                if alert.status == "active":
                    active_alerts.append(asdict(alert))
            
            return active_alerts
        except Exception as e:
            logger.error(f"获取活跃告警失败: {str(e)}")
            return []
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取告警历史"""
        try:
            # 从数据库获取告警历史
            alerts = self.db.read("alerts")
            
            # 过滤时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            filtered_alerts = []
            for alert in alerts:
                alert_time = datetime.fromisoformat(alert["timestamp"])
                if start_time <= alert_time <= end_time:
                    filtered_alerts.append(alert)
            
            return filtered_alerts
        except Exception as e:
            logger.error(f"获取告警历史失败: {str(e)}")
            return []
    
    def update_alert_thresholds(self, thresholds: Dict[str, float]):
        """更新告警阈值"""
        try:
            self.alert_thresholds.update(thresholds)
            logger.info(f"告警阈值已更新: {thresholds}")
        except Exception as e:
            logger.error(f"更新告警阈值失败: {str(e)}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        try:
            # 收集当前指标
            system_metrics = self.collect_system_metrics()
            app_metrics = self.collect_application_metrics()
            
            # 计算健康分数
            health_score = 100
            
            # CPU健康分数
            if system_metrics.cpu_percent > 80:
                health_score -= 20
            elif system_metrics.cpu_percent > 60:
                health_score -= 10
            
            # 内存健康分数
            if system_metrics.memory_percent > 85:
                health_score -= 20
            elif system_metrics.memory_percent > 70:
                health_score -= 10
            
            # 磁盘健康分数
            if system_metrics.disk_percent > 90:
                health_score -= 30
            elif system_metrics.disk_percent > 80:
                health_score -= 15
            
            # 响应时间健康分数
            if app_metrics.response_time_avg > 2.0:
                health_score -= 15
            elif app_metrics.response_time_avg > 1.0:
                health_score -= 5
            
            # 错误率健康分数
            error_rate = app_metrics.error_count / app_metrics.request_count if app_metrics.request_count > 0 else 0
            if error_rate > 0.05:
                health_score -= 20
            elif error_rate > 0.01:
                health_score -= 10
            
            # 确定健康状态
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "status": status,
                "health_score": max(0, health_score),
                "timestamp": datetime.now().isoformat(),
                "system_metrics": asdict(system_metrics),
                "application_metrics": asdict(app_metrics),
                "active_alerts_count": len([a for a in self.active_alerts.values() if a.status == "active"])
            }
        except Exception as e:
            logger.error(f"获取健康状态失败: {str(e)}")
            return {
                "status": "unknown",
                "health_score": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


# 创建全局监控服务实例
monitoring_service = MonitoringService()

"""
风险服务
"""
from typing import List, Optional, Dict, Any
from app.models.risk import Risk, RiskCreate, RiskUpdate, RiskResponse
from app.services.database_service import database_service
from app.utils.logger import get_logger
from app.utils.helpers import generate_id

logger = get_logger(__name__)


class RiskService:
    """风险服务类"""
    
    def __init__(self):
        """初始化风险服务"""
        self.db = database_service.get_database()
        logger.info("风险服务初始化完成")
    
    def get_risks(self, filters: Optional[Dict[str, Any]] = None, search: Optional[str] = None) -> List[RiskResponse]:
        """获取风险列表"""
        try:
            risks_data = self.db.read("risks", filters=filters)
            
            if search:
                risks_data = self.db.search("risks", search, ["risk_title", "description"])
            
            risks = []
            for risk_data in risks_data:
                risk_response = self._calculate_risk_metrics(risk_data)
                risks.append(risk_response)
            
            logger.info(f"获取到 {len(risks)} 个风险")
            return risks
        except Exception as e:
            logger.error(f"获取风险列表失败: {str(e)}")
            raise
    
    def get_risk(self, risk_id: str) -> Optional[RiskResponse]:
        """获取单个风险"""
        try:
            risk_data = self.db.read("risks", risk_id)
            if not risk_data:
                return None
            
            risk_response = self._calculate_risk_metrics(risk_data)
            logger.info(f"获取风险 {risk_id} 成功")
            return risk_response
        except Exception as e:
            logger.error(f"获取风险 {risk_id} 失败: {str(e)}")
            raise
    
    def create_risk(self, risk_data: RiskCreate) -> RiskResponse:
        """创建风险"""
        try:
            # 生成风险ID
            risk_id = f"RISK-{generate_id()[:8].upper()}"
            
            # 创建风险数据
            risk_dict = risk_data.dict()
            risk_dict["risk_id"] = risk_id
            risk_dict["status"] = "已识别"
            
            # 计算风险等级
            risk_level = self._calculate_risk_level(risk_dict["probability"], risk_dict["impact"])
            risk_dict["risk_level"] = risk_level
            
            # 保存到数据库
            created_risk = self.db.create("risks", risk_dict)
            
            risk_response = self._calculate_risk_metrics(created_risk)
            
            logger.info(f"创建风险 {risk_id} 成功")
            return risk_response
        except Exception as e:
            logger.error(f"创建风险失败: {str(e)}")
            raise
    
    def update_risk(self, risk_id: str, risk_data: RiskUpdate) -> Optional[RiskResponse]:
        """更新风险"""
        try:
            # 获取现有风险
            existing_risk = self.db.read("risks", risk_id)
            if not existing_risk:
                return None
            
            # 更新风险数据
            updates = {k: v for k, v in risk_data.dict().items() if v is not None}
            
            # 如果更新了概率或影响，重新计算风险等级
            if "probability" in updates or "impact" in updates:
                probability = updates.get("probability", existing_risk.get("probability"))
                impact = updates.get("impact", existing_risk.get("impact"))
                updates["risk_level"] = self._calculate_risk_level(probability, impact)
            
            updated_risk = self.db.update("risks", risk_id, updates)
            
            if not updated_risk:
                return None
            
            risk_response = self._calculate_risk_metrics(updated_risk)
            
            logger.info(f"更新风险 {risk_id} 成功")
            return risk_response
        except Exception as e:
            logger.error(f"更新风险 {risk_id} 失败: {str(e)}")
            raise
    
    def delete_risk(self, risk_id: str) -> bool:
        """删除风险"""
        try:
            success = self.db.delete("risks", risk_id)
            if success:
                logger.info(f"删除风险 {risk_id} 成功")
            else:
                logger.warning(f"风险 {risk_id} 不存在")
            return success
        except Exception as e:
            logger.error(f"删除风险 {risk_id} 失败: {str(e)}")
            raise
    
    def get_project_risks(self, project_id: str, filters: Optional[Dict[str, Any]] = None) -> List[RiskResponse]:
        """获取项目的风险列表"""
        try:
            project_filters = {"project_id": project_id}
            if filters:
                project_filters.update(filters)
            
            risks = self.get_risks(project_filters)
            logger.info(f"获取项目 {project_id} 的 {len(risks)} 个风险")
            return risks
        except Exception as e:
            logger.error(f"获取项目 {project_id} 的风险列表失败: {str(e)}")
            raise
    
    def get_high_risks(self) -> List[RiskResponse]:
        """获取高风险列表"""
        try:
            high_risks = self.get_risks(filters={"risk_level": "高"})
            critical_risks = self.get_risks(filters={"risk_level": "严重"})
            
            all_high_risks = high_risks + critical_risks
            logger.info(f"获取到 {len(all_high_risks)} 个高风险")
            return all_high_risks
        except Exception as e:
            logger.error(f"获取高风险列表失败: {str(e)}")
            raise
    
    def _calculate_risk_level(self, probability: str, impact: str) -> str:
        """计算风险等级"""
        # 风险等级矩阵
        risk_matrix = {
            ("低", "低"): "低",
            ("低", "中"): "低",
            ("低", "高"): "中",
            ("中", "低"): "低",
            ("中", "中"): "中",
            ("中", "高"): "高",
            ("高", "低"): "中",
            ("高", "中"): "高",
            ("高", "高"): "严重"
        }
        
        return risk_matrix.get((probability, impact), "中")
    
    def _calculate_risk_metrics(self, risk_data: Dict[str, Any]) -> RiskResponse:
        """计算风险指标"""
        try:
            # 计算风险评分（1-9分）
            probability_score = {"低": 1, "中": 2, "高": 3}.get(risk_data.get("probability", "中"), 2)
            impact_score = {"低": 1, "中": 2, "高": 3}.get(risk_data.get("impact", "中"), 2)
            risk_score = probability_score * impact_score
            
            # 计算识别天数（简化计算）
            days_since_identified = 0  # TODO: 实现更准确的日期计算
            
            # 计算缓解进度（基于状态）
            status_progress = {
                "已识别": 0.0,
                "已评估": 25.0,
                "已应对": 75.0,
                "已关闭": 100.0
            }
            mitigation_progress = status_progress.get(risk_data.get("status", "已识别"), 0.0)
            
            # 创建风险响应对象
            risk_response = RiskResponse(
                **risk_data,
                risk_score=risk_score,
                days_since_identified=days_since_identified,
                mitigation_progress=mitigation_progress
            )
            
            return risk_response
        except Exception as e:
            logger.error(f"计算风险指标失败: {str(e)}")
            # 返回基础风险数据
            return RiskResponse(**risk_data)


# 创建全局风险服务实例
risk_service = RiskService()

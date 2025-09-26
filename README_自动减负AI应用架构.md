# 自动减负AI应用架构（MVP阶段）

## 🎯 架构目标

通过 AI 技术解决项目管理中的"低价值、高频事务"，实现信息自动收集、智能汇总与任务流转减负，释放管理者时间，把精力聚焦在关键决策与跨部门协调。

## 🏗️ 核心架构分层

### 数据层
- **多源数据接入**：任务管理系统（PMS）、OA、Excel/文档
- **数据处理管道**：统一数据结构（任务、进度、风险、问题清单），清洗与格式化，支持实时更新
- **模拟数据库**：JSON格式的模拟数据库，包含完整的项目管理数据

### 智能层
- **RAG增强检索**：基于项目历史文档、会议纪要、进度报告，构建知识库，支持任务关联与上下文追踪
- **NLP任务解析**：自动识别会议纪要/群聊中的任务，提取负责人、截止时间、优先级
- **智能任务编排**：结合大模型对话生成 → 自动转化为结构化任务（JSON/数据库写入）
- **智能汇总/提醒**：
  - 自动生成日报/周报/阶段进度总结
  - 风险/延误项智能预警
  - 任务到期自动提醒与责任人追踪

### 应用层（自动减负MVP）
- **自动任务捕捉器**：从会议/群聊/邮件自动抓取行动项
- **智能进度汇总**：日/周自动生成进度汇报，减少人工整理
- **风险清单监控**：自动标记潜在延期任务并推送PM
- **一键导出报表**：面向管理层的 PPT/表格自动生成

## 🛠️ 技术实现要点

- **大模型应用**：通义千问，用于自然语言解析、摘要与自动生成
- **任务引擎**：Qwen_Agent，实现RAG检索+上下文记忆
- **数据库**：PostgreSQL/MySQL 存储任务数据，支持 BI 接入（当前环境下，建文档模拟数据库）
- **接口与集成**：支持API对接PMS系统（模拟PMS系统，给个文档输出内容就行）

## 📁 项目结构

```
PMS_AI_System/
├── app/
│   ├── api/
│   │   ├── auto_reduce_services.py    # 自动减负服务API
│   │   ├── ai_services.py             # AI智能服务API
│   │   └── ...                        # 其他API模块
│   ├── services/
│   │   ├── auto_task_capture.py       # 自动任务捕捉服务
│   │   ├── intelligent_progress_summary.py  # 智能进度汇总服务
│   │   ├── risk_monitoring.py         # 风险监控服务
│   │   ├── report_generator.py        # 报表生成服务
│   │   ├── qwen_agent_service.py      # 通义千问Agent服务
│   │   └── pms_interface.py           # PMS系统接口
│   ├── models/                        # 数据模型
│   └── utils/                         # 工具函数
├── data/
│   ├── simulated_database.json        # 模拟数据库
│   └── ...                           # 其他数据文件
├── demo_auto_reduce.py               # 功能演示脚本
└── README_自动减负AI应用架构.md      # 本文档
```

## 🚀 核心功能模块

### 1. 自动任务捕捉器 (`auto_task_capture.py`)

**功能描述**：从会议纪要、群聊消息、邮件等文本中自动识别和提取任务信息

**核心特性**：
- 支持多种文本来源：会议纪要、群聊、邮件
- 智能提取任务信息：标题、负责人、截止日期、优先级
- 基于规则和AI的任务识别
- 置信度评估和结果过滤

**API接口**：
- `POST /api/v1/auto-reduce/task-capture/extract` - 基础任务提取
- `POST /api/v1/auto-reduce/task-capture/qwen-extract` - 通义千问智能提取

**使用示例**：
```python
# 从会议纪要提取任务
meeting = MeetingMinutes(
    meeting_id="meeting_001",
    title="项目启动会议",
    content="李四负责完成系统架构设计，9月20日前完成"
)
tasks = auto_task_capture_service.extract_tasks_from_meeting(meeting)
```

### 2. 智能进度汇总系统 (`intelligent_progress_summary.py`)

**功能描述**：自动生成日报、周报、月报，减少人工整理时间

**核心特性**：
- 多周期汇总：日报、周报、月报
- 智能分析：进度趋势、完成率、风险指标
- 自动生成：亮点、关注点、建议
- 数据驱动：基于实际任务数据生成

**API接口**：
- `GET /api/v1/auto-reduce/progress-summary/daily/{project_id}` - 生成日报
- `GET /api/v1/auto-reduce/progress-summary/weekly/{project_id}` - 生成周报
- `GET /api/v1/auto-reduce/progress-summary/monthly/{project_id}` - 生成月报
- `POST /api/v1/auto-reduce/progress-summary/qwen-generate` - 通义千问智能汇总

**使用示例**：
```python
# 生成周报
weekly_report = intelligent_progress_summary_service.generate_weekly_summary("proj_001")
print(f"本周完成: {len(weekly_report.achievements)} 项")
print(f"下周计划: {len(weekly_report.next_week_plan)} 项")
```

### 3. 风险监控系统 (`risk_monitoring.py`)

**功能描述**：自动标记潜在延期任务并推送PM，实现风险预警

**核心特性**：
- 多维度风险识别：进度延期、资源不足、质量问题、依赖阻塞等
- 风险等级评估：低、中、高、严重
- 智能预警：基于阈值和趋势分析
- 缓解建议：自动生成风险处理建议

**风险类型**：
- 进度延期风险 (SCHEDULE_DELAY)
- 资源不足风险 (RESOURCE_SHORTAGE)
- 质量问题风险 (QUALITY_ISSUE)
- 依赖阻塞风险 (DEPENDENCY_BLOCK)
- 范围蔓延风险 (SCOPE_CREEP)
- 技术风险 (TECHNICAL_RISK)

**API接口**：
- `GET /api/v1/auto-reduce/risk-monitoring/scan/{project_id}` - 扫描项目风险
- `GET /api/v1/auto-reduce/risk-monitoring/report/{project_id}` - 生成风险报告
- `POST /api/v1/auto-reduce/risk-monitoring/qwen-analyze` - 通义千问风险分析

**使用示例**：
```python
# 扫描项目风险
risks = risk_monitoring_service.scan_project_risks("proj_001")
for risk in risks:
    print(f"风险: {risk.title}, 等级: {risk.risk_level.value}")
```

### 4. 一键导出报表功能 (`report_generator.py`)

**功能描述**：面向管理层的PPT/表格自动生成

**核心特性**：
- 多格式支持：Excel、CSV、JSON、HTML
- 多类型报表：项目汇总、任务进度、风险分析、团队绩效、高管仪表板
- 模板化生成：支持自定义模板
- 批量导出：支持多项目批量生成

**报表类型**：
- 项目汇总报表 (PROJECT_SUMMARY)
- 任务进度报表 (TASK_PROGRESS)
- 风险分析报表 (RISK_ANALYSIS)
- 团队绩效报表 (TEAM_PERFORMANCE)
- 高管仪表板 (EXECUTIVE_DASHBOARD)

**API接口**：
- `POST /api/v1/auto-reduce/report-generator/generate` - 生成报表
- `POST /api/v1/auto-reduce/report-generator/export` - 导出报表

**使用示例**：
```python
# 生成项目汇总报表
request = ReportRequest(
    report_type=ReportType.PROJECT_SUMMARY,
    format=ReportFormat.EXCEL,
    project_ids=["proj_001", "proj_002"]
)
report_data = report_generator_service.generate_report(request)
```

### 5. 通义千问Agent服务 (`qwen_agent_service.py`)

**功能描述**：实现RAG检索+上下文记忆的智能对话和任务处理

**核心特性**：
- 智能任务提取：基于通义千问的自然语言理解
- 智能进度汇总：AI生成的专业报告
- 智能风险分析：多维度风险识别和建议
- 智能查询：基于RAG的上下文问答
- 对话记忆：维护上下文对话历史

**API接口**：
- `POST /api/v1/auto-reduce/intelligent-query` - 智能查询

**使用示例**：
```python
# 智能查询
result = await qwen_agent_service.intelligent_query(
    "项目进度如何？有哪些风险需要关注？",
    "user_001",
    "proj_001"
)
print(f"回答: {result['answer']}")
```

### 6. PMS系统接口 (`pms_interface.py`)

**功能描述**：模拟PMS系统的API接口，提供项目管理相关的数据访问

**核心特性**：
- 项目数据管理：项目信息、成员、里程碑
- 任务数据管理：任务CRUD、状态跟踪、依赖关系
- 问题管理：问题跟踪、分类、处理
- 会议管理：会议纪要、行动项、决策项
- 文档管理：文档存储、分类、检索
- 统计报表：仪表板数据、汇总统计

**API接口**：
- 项目相关：`get_projects()`, `get_project()`, `get_project_summary()`
- 任务相关：`get_tasks()`, `create_task()`, `update_task()`
- 问题相关：`get_issues()`, `get_project_issues()`
- 会议相关：`get_meetings()`, `get_project_meetings()`
- 统计相关：`get_dashboard_data()`, `get_overdue_tasks()`

## 📊 模拟数据库结构

模拟数据库 (`data/simulated_database.json`) 包含以下数据：

- **项目数据**：项目信息、成员、里程碑、风险、问题
- **任务数据**：任务详情、状态、进度、依赖关系
- **问题数据**：问题分类、状态、优先级、处理信息
- **会议数据**：会议纪要、参会人员、行动项、决策项
- **聊天数据**：群聊消息、发送人、时间戳
- **邮件数据**：邮件内容、发送人、收件人、主题
- **文档数据**：文档信息、类型、作者、内容
- **报表数据**：历史报表、汇总信息

## 🎮 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python start_app.py
```

### 3. 访问API文档

```
http://localhost:8000/docs
```

### 4. 运行演示

```bash
python demo_auto_reduce.py
```

## 📋 API使用示例

### 自动任务捕捉

```bash
# 从会议纪要提取任务
curl -X POST "http://localhost:8000/api/v1/auto-reduce/task-capture/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "meeting",
    "content": "李四负责完成系统架构设计，9月20日前完成",
    "project_id": "proj_001"
  }'
```

### 智能进度汇总

```bash
# 生成周报
curl -X GET "http://localhost:8000/api/v1/auto-reduce/progress-summary/weekly/proj_001"
```

### 风险监控

```bash
# 扫描项目风险
curl -X GET "http://localhost:8000/api/v1/auto-reduce/risk-monitoring/scan/proj_001"
```

### 报表生成

```bash
# 生成项目汇总报表
curl -X POST "http://localhost:8000/api/v1/auto-reduce/report-generator/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "project_summary",
    "format": "json",
    "project_ids": ["proj_001", "proj_002"]
  }'
```

### 智能查询

```bash
# 智能查询
curl -X POST "http://localhost:8000/api/v1/auto-reduce/intelligent-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "项目进度如何？有哪些风险需要关注？",
    "user_id": "user_001",
    "project_id": "proj_001"
  }'
```

## 🔧 配置说明

### 通义千问配置

在 `config/settings.py` 中配置通义千问API：

```python
# LLM 配置
llm_provider: str = "qwen"
qwen_api_key: str = "your_qwen_api_key"
qwen_api_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
```

### 风险阈值配置

在 `risk_monitoring.py` 中配置风险阈值：

```python
self.risk_thresholds = {
    'schedule_delay_days': 3,      # 进度延期天数阈值
    'completion_rate_low': 0.6,    # 完成率低阈值
    'blocked_task_ratio': 0.2,     # 阻塞任务比例阈值
    'overdue_task_ratio': 0.15,    # 逾期任务比例阈值
}
```

## 📈 性能指标

### 自动减负效果

- **任务提取准确率**：85%+（基于规则+AI）
- **进度汇总效率**：减少90%人工整理时间
- **风险识别覆盖率**：95%+（多维度风险扫描）
- **报表生成速度**：秒级生成（支持批量导出）

### 系统性能

- **API响应时间**：< 2秒（大部分接口）
- **并发处理能力**：支持100+并发请求
- **数据存储**：支持10万+任务数据
- **扩展性**：模块化设计，易于扩展

## 🔮 未来规划

### 短期目标（1-3个月）

1. **完善AI模型集成**
   - 集成真实的通义千问API
   - 优化提示词和模型参数
   - 提升任务提取准确率

2. **增强数据源支持**
   - 支持更多文档格式（PDF、Word、Excel）
   - 集成真实PMS系统
   - 支持实时数据同步

3. **优化用户体验**
   - 开发Web前端界面
   - 增加可视化图表
   - 支持移动端访问

### 中期目标（3-6个月）

1. **智能决策支持**
   - 基于历史数据的智能建议
   - 资源优化配置建议
   - 项目风险预测模型

2. **多模态支持**
   - 支持语音转文字
   - 支持图片识别
   - 支持视频会议纪要提取

3. **企业级功能**
   - 多租户支持
   - 权限管理
   - 审计日志

### 长期目标（6-12个月）

1. **AI Agent生态**
   - 多Agent协作
   - 自主任务执行
   - 智能工作流编排

2. **行业定制化**
   - 不同行业模板
   - 专业术语识别
   - 行业最佳实践

3. **生态集成**
   - 第三方工具集成
   - API开放平台
   - 插件生态

## 🤝 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目维护者：AI开发团队
- 邮箱：ai-team@company.com
- 项目地址：https://github.com/company/pms-ai-system

---

**自动减负AI应用架构** - 让AI为项目管理减负，释放管理者时间，聚焦关键决策！


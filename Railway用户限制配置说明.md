# 🚀 Railway用户使用次数限制配置说明

## 📋 Railway平台限制机制

### 1️⃣ **Railway平台本身的限制**

Railway平台提供以下限制机制：

**免费计划限制**：
- 每月500小时运行时间
- 512MB内存限制
- 1GB存储空间
- 无自定义域名

**付费计划**：
- 按使用量计费
- 更高的资源限制
- 自定义域名支持
- 更好的性能保证

### 2️⃣ **应用层面的用户限制实现**

由于Railway本身不提供用户使用次数限制功能，需要在应用层面实现：

#### 方案一：基于IP地址的限制
```python
# 在deploy_railway_v007.py中添加
import time
from collections import defaultdict

# 用户使用记录
user_usage = defaultdict(list)
MAX_REQUESTS_PER_HOUR = 10  # 每小时最大请求数
MAX_REQUESTS_PER_DAY = 50   # 每天最大请求数

def check_user_limit(client_ip: str) -> bool:
    """检查用户使用限制"""
    current_time = time.time()
    
    # 清理过期记录
    user_usage[client_ip] = [
        req_time for req_time in user_usage[client_ip] 
        if current_time - req_time < 86400  # 保留24小时内的记录
    ]
    
    # 检查每小时限制
    recent_requests = [
        req_time for req_time in user_usage[client_ip]
        if current_time - req_time < 3600  # 最近1小时
    ]
    
    if len(recent_requests) >= MAX_REQUESTS_PER_HOUR:
        return False
    
    # 检查每天限制
    if len(user_usage[client_ip]) >= MAX_REQUESTS_PER_DAY:
        return False
    
    # 记录本次请求
    user_usage[client_ip].append(current_time)
    return True

# 在聊天接口中使用
@app.post("/api/v1/auto-reduce/intelligent-chat/chat-stream")
async def chat_with_ai_stream(request: dict, client_ip: str = None):
    # 检查用户限制
    if not check_user_limit(client_ip):
        return {"error": "今日使用次数已达上限，请明天再试"}
    
    # 继续处理请求...
```

#### 方案二：基于会话ID的限制
```python
# 基于会话的限制
session_usage = defaultdict(int)
MAX_SESSIONS_PER_IP = 3  # 每个IP最多3个会话

def check_session_limit(client_ip: str, session_id: str) -> bool:
    """检查会话限制"""
    # 检查IP的会话数量
    if len(session_usage[client_ip]) >= MAX_SESSIONS_PER_IP:
        return False
    
    # 记录会话
    session_usage[client_ip].add(session_id)
    return True
```

#### 方案三：基于用户认证的限制
```python
# 需要用户注册和登录
user_limits = {
    "free_user": {"daily_limit": 10, "hourly_limit": 2},
    "premium_user": {"daily_limit": 100, "hourly_limit": 20},
    "enterprise_user": {"daily_limit": 1000, "hourly_limit": 100}
}

def check_user_quota(user_id: str, user_type: str) -> bool:
    """检查用户配额"""
    limits = user_limits.get(user_type, user_limits["free_user"])
    # 实现配额检查逻辑
    pass
```

### 3️⃣ **数据库存储用户限制**

#### 使用SQLite数据库
```python
import sqlite3
from datetime import datetime, timedelta

# 创建数据库表
def init_usage_db():
    conn = sqlite3.connect('usage_tracking.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ip TEXT,
            session_id TEXT,
            request_time TIMESTAMP,
            request_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def track_usage(user_ip: str, session_id: str, request_type: str):
    """记录用户使用情况"""
    conn = sqlite3.connect('usage_tracking.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usage_records (user_ip, session_id, request_time, request_type)
        VALUES (?, ?, ?, ?)
    ''', (user_ip, session_id, datetime.now(), request_type))
    conn.commit()
    conn.close()

def check_usage_limit(user_ip: str, limit_type: str = "daily", limit_value: int = 10):
    """检查使用限制"""
    conn = sqlite3.connect('usage_tracking.db')
    cursor = conn.cursor()
    
    if limit_type == "daily":
        time_threshold = datetime.now() - timedelta(days=1)
    elif limit_type == "hourly":
        time_threshold = datetime.now() - timedelta(hours=1)
    else:
        return True
    
    cursor.execute('''
        SELECT COUNT(*) FROM usage_records 
        WHERE user_ip = ? AND request_time > ?
    ''', (user_ip, time_threshold))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count < limit_value
```

### 4️⃣ **环境变量配置**

在Railway中设置环境变量：

```bash
# Railway环境变量设置
MAX_REQUESTS_PER_HOUR=10
MAX_REQUESTS_PER_DAY=50
ENABLE_USAGE_LIMIT=true
USAGE_LIMIT_TYPE=ip_based  # ip_based, session_based, user_based
```

### 5️⃣ **完整的用户限制实现**

```python
# 完整的用户限制系统
import os
import time
import sqlite3
from datetime import datetime, timedelta
from fastapi import Request, HTTPException

class UsageLimiter:
    def __init__(self):
        self.enabled = os.getenv('ENABLE_USAGE_LIMIT', 'false').lower() == 'true'
        self.hourly_limit = int(os.getenv('MAX_REQUESTS_PER_HOUR', '10'))
        self.daily_limit = int(os.getenv('MAX_REQUESTS_PER_DAY', '50'))
        self.limit_type = os.getenv('USAGE_LIMIT_TYPE', 'ip_based')
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect('usage_tracking.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT,
                request_time TIMESTAMP,
                request_type TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_identifier(self, request: Request) -> str:
        """获取用户标识符"""
        if self.limit_type == 'ip_based':
            return request.client.host
        elif self.limit_type == 'session_based':
            return request.headers.get('x-session-id', request.client.host)
        else:
            return request.client.host
    
    def check_limit(self, identifier: str) -> bool:
        """检查使用限制"""
        if not self.enabled:
            return True
        
        conn = sqlite3.connect('usage_tracking.db')
        cursor = conn.cursor()
        
        # 检查每小时限制
        hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute('''
            SELECT COUNT(*) FROM usage_records 
            WHERE identifier = ? AND request_time > ?
        ''', (identifier, hour_ago))
        hourly_count = cursor.fetchone()[0]
        
        # 检查每天限制
        day_ago = datetime.now() - timedelta(days=1)
        cursor.execute('''
            SELECT COUNT(*) FROM usage_records 
            WHERE identifier = ? AND request_time > ?
        ''', (identifier, day_ago))
        daily_count = cursor.fetchone()[0]
        
        conn.close()
        
        if hourly_count >= self.hourly_limit:
            raise HTTPException(
                status_code=429, 
                detail=f"每小时使用次数已达上限({self.hourly_limit}次)，请稍后再试"
            )
        
        if daily_count >= self.daily_limit:
            raise HTTPException(
                status_code=429, 
                detail=f"每日使用次数已达上限({self.daily_limit}次)，请明天再试"
            )
        
        return True
    
    def record_usage(self, identifier: str, request_type: str = "chat"):
        """记录使用情况"""
        if not self.enabled:
            return
        
        conn = sqlite3.connect('usage_tracking.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usage_records (identifier, request_time, request_type)
            VALUES (?, ?, ?)
        ''', (identifier, datetime.now(), request_type))
        conn.commit()
        conn.close()

# 全局限制器实例
usage_limiter = UsageLimiter()

# 在聊天接口中使用
@app.post("/api/v1/auto-reduce/intelligent-chat/chat-stream")
async def chat_with_ai_stream(request: dict, http_request: Request):
    # 获取用户标识符
    identifier = usage_limiter.get_identifier(http_request)
    
    # 检查使用限制
    usage_limiter.check_limit(identifier)
    
    # 记录使用情况
    usage_limiter.record_usage(identifier, "chat")
    
    # 继续处理请求...
```

### 6️⃣ **Railway部署配置**

在Railway中设置环境变量：

1. 进入Railway项目设置
2. 选择"Variables"标签
3. 添加以下环境变量：

```
ENABLE_USAGE_LIMIT=true
MAX_REQUESTS_PER_HOUR=10
MAX_REQUESTS_PER_DAY=50
USAGE_LIMIT_TYPE=ip_based
```

### 7️⃣ **监控和统计**

```python
# 添加使用统计接口
@app.get("/api/v1/usage/stats")
async def get_usage_stats():
    """获取使用统计"""
    conn = sqlite3.connect('usage_tracking.db')
    cursor = conn.cursor()
    
    # 今日使用统计
    today = datetime.now().date()
    cursor.execute('''
        SELECT COUNT(*) FROM usage_records 
        WHERE DATE(request_time) = ?
    ''', (today,))
    today_count = cursor.fetchone()[0]
    
    # 每小时使用统计
    cursor.execute('''
        SELECT strftime('%H', request_time) as hour, COUNT(*) as count
        FROM usage_records 
        WHERE DATE(request_time) = ?
        GROUP BY strftime('%H', request_time)
        ORDER BY hour
    ''', (today,))
    hourly_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        "today_total": today_count,
        "hourly_stats": [{"hour": h, "count": c} for h, c in hourly_stats],
        "limits": {
            "hourly": usage_limiter.hourly_limit,
            "daily": usage_limiter.daily_limit
        }
    }
```

## 🎯 总结

Railway平台本身不提供用户使用次数限制功能，但可以通过应用层面的实现来达到目的：

1. **基于IP地址的限制**：简单易实现，适合基础需求
2. **基于会话的限制**：更精确的控制，适合中等需求
3. **基于用户认证的限制**：最灵活的控制，适合复杂需求

选择哪种方案取决于您的具体需求和用户规模。建议从简单的IP限制开始，根据实际使用情况逐步优化。

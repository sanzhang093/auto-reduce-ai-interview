-- 自动减负AI应用数据库初始化脚本

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS auto_reduce_db;

-- 使用数据库
\c auto_reduce_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    roles TEXT[] DEFAULT ARRAY['TEAM_MEMBER'],
    is_active BOOLEAN DEFAULT TRUE,
    skills TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建项目表
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'PLANNING',
    manager_id VARCHAR(50) NOT NULL,
    team_members TEXT[] DEFAULT ARRAY[]::TEXT[],
    budget DECIMAL(15,2),
    progress DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(user_id)
);

-- 创建任务表
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to VARCHAR(50),
    due_date DATE,
    status VARCHAR(50) DEFAULT 'NOT_STARTED',
    priority VARCHAR(50) DEFAULT 'MEDIUM',
    dependencies TEXT[] DEFAULT ARRAY[]::TEXT[],
    progress DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- 创建风险表
CREATE TABLE IF NOT EXISTS risks (
    id SERIAL PRIMARY KEY,
    risk_id VARCHAR(50) UNIQUE NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    risk_title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'TECHNICAL',
    probability DECIMAL(3,2) CHECK (probability >= 0 AND probability <= 1),
    impact VARCHAR(50) DEFAULT 'MEDIUM',
    status VARCHAR(50) DEFAULT 'Open',
    mitigation_plan TEXT,
    owner_id VARCHAR(50),
    due_date DATE,
    priority VARCHAR(50) DEFAULT 'MEDIUM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

-- 创建问题表
CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    issue_id VARCHAR(50) UNIQUE NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    task_id VARCHAR(50),
    issue_title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50) DEFAULT 'MEDIUM',
    status VARCHAR(50) DEFAULT 'OPEN',
    reported_by VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(50),
    due_date DATE,
    resolution TEXT,
    priority VARCHAR(50) DEFAULT 'MEDIUM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (reported_by) REFERENCES users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- 创建里程碑表
CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    milestone_id VARCHAR(50) UNIQUE NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    milestone_name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'PLANNING',
    completed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- 创建资源表
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    role VARCHAR(50) DEFAULT 'TEAM_MEMBER',
    allocation_percentage DECIMAL(5,2) DEFAULT 100.0,
    start_date DATE,
    end_date DATE,
    skills TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- 创建时间跟踪表
CREATE TABLE IF NOT EXISTS time_tracking (
    id SERIAL PRIMARY KEY,
    time_tracking_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    task_id VARCHAR(50) NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    hours_spent DECIMAL(5,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- 创建变更请求表
CREATE TABLE IF NOT EXISTS change_requests (
    id SERIAL PRIMARY KEY,
    change_request_id VARCHAR(50) UNIQUE NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requested_by VARCHAR(50) NOT NULL,
    requested_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    approved_by VARCHAR(50),
    approval_date DATE,
    impact_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (requested_by) REFERENCES users(user_id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id)
);

-- 创建项目指标表
CREATE TABLE IF NOT EXISTS project_metrics (
    id SERIAL PRIMARY KEY,
    metrics_id VARCHAR(50) UNIQUE NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    actual_progress DECIMAL(5,2) NOT NULL,
    planned_progress DECIMAL(5,2) NOT NULL,
    cost_variance DECIMAL(15,2),
    schedule_variance DECIMAL(15,2),
    risk_count INTEGER DEFAULT 0,
    issue_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- 创建聊天会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    project_id VARCHAR(50),
    messages JSONB DEFAULT '[]'::jsonb,
    context JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- 创建向量嵌入表
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(100) UNIQUE NOT NULL,
    embedding FLOAT[] NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_projects_manager_id ON projects(manager_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_risks_project_id ON risks(project_id);
CREATE INDEX IF NOT EXISTS idx_issues_project_id ON issues(project_id);
CREATE INDEX IF NOT EXISTS idx_issues_task_id ON issues(task_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_project_id ON chat_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_doc_id ON vector_embeddings(doc_id);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表创建更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_risks_updated_at BEFORE UPDATE ON risks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_issues_updated_at BEFORE UPDATE ON issues FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_milestones_updated_at BEFORE UPDATE ON milestones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_time_tracking_updated_at BEFORE UPDATE ON time_tracking FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_change_requests_updated_at BEFORE UPDATE ON change_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_metrics_updated_at BEFORE UPDATE ON project_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入初始数据
INSERT INTO users (user_id, username, email, hashed_password, full_name, roles) VALUES
('admin_001', 'admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8', '系统管理员', ARRAY['SYSTEM_ADMIN']),
('manager_001', 'manager', 'manager@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8', '项目经理', ARRAY['PROJECT_MANAGER']),
('user_001', 'user1', 'user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8', '用户1', ARRAY['TEAM_MEMBER'])
ON CONFLICT (user_id) DO NOTHING;

-- 插入示例项目
INSERT INTO projects (project_id, project_name, description, start_date, end_date, status, manager_id, budget, progress) VALUES
('PRJ-2024-001', '自动减负AI应用', '基于AI的项目管理应用', '2024-01-01', '2024-12-31', 'IN_PROGRESS', 'manager_001', 1000000.00, 75.0)
ON CONFLICT (project_id) DO NOTHING;

-- 插入示例任务
INSERT INTO tasks (task_id, project_id, task_name, description, assigned_to, due_date, status, priority, progress) VALUES
('TASK-001', 'PRJ-2024-001', '需求分析', '分析项目需求', 'user_001', '2024-02-01', 'COMPLETED', 'HIGH', 100.0),
('TASK-002', 'PRJ-2024-001', '系统设计', '设计系统架构', 'user_001', '2024-03-01', 'IN_PROGRESS', 'HIGH', 80.0),
('TASK-003', 'PRJ-2024-001', '开发实现', '实现核心功能', 'user_001', '2024-06-01', 'IN_PROGRESS', 'MEDIUM', 60.0)
ON CONFLICT (task_id) DO NOTHING;

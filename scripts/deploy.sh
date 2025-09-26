#!/bin/bash

# 自动减负AI应用部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    log_info "检查Docker安装状态..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker和Docker Compose已安装"
}

# 检查环境变量
check_env() {
    log_info "检查环境变量..."
    
    if [ -z "$DASHSCOPE_API_KEY" ]; then
        log_warning "DASHSCOPE_API_KEY未设置，将使用默认值"
        export DASHSCOPE_API_KEY="sk-369a880b04ca4e5cbfd139fe858e7d80"
    fi
    
    if [ -z "$POSTGRES_PASSWORD" ]; then
        log_warning "POSTGRES_PASSWORD未设置，将使用默认值"
        export POSTGRES_PASSWORD="auto_reduce_password"
    fi
    
    if [ -z "$GRAFANA_PASSWORD" ]; then
        log_warning "GRAFANA_PASSWORD未设置，将使用默认值"
        export GRAFANA_PASSWORD="admin"
    fi
    
    log_success "环境变量检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p data
    mkdir -p reports
    mkdir -p logs
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    log_success "目录创建完成"
}

# 构建应用镜像
build_app() {
    log_info "构建应用镜像..."
    
    docker-compose build app
    
    log_success "应用镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础服务
    docker-compose up -d postgres redis
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 30
    
    # 启动应用服务
    docker-compose up -d app
    
    # 启动其他服务
    docker-compose up -d nginx prometheus grafana elasticsearch kibana
    
    log_success "所有服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 等待服务启动
    sleep 60
    
    # 检查应用健康状态
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        log_success "应用服务健康检查通过"
    else
        log_error "应用服务健康检查失败"
        return 1
    fi
    
    # 检查Nginx状态
    if curl -f http://localhost/health/ > /dev/null 2>&1; then
        log_success "Nginx代理健康检查通过"
    else
        log_warning "Nginx代理健康检查失败"
    fi
    
    # 检查Prometheus状态
    if curl -f http://localhost:9090 > /dev/null 2>&1; then
        log_success "Prometheus监控服务正常"
    else
        log_warning "Prometheus监控服务异常"
    fi
    
    # 检查Grafana状态
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Grafana可视化服务正常"
    else
        log_warning "Grafana可视化服务异常"
    fi
}

# 显示服务信息
show_services() {
    log_info "服务访问信息："
    echo "=================================="
    echo "应用服务: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo "Nginx代理: http://localhost"
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3000 (admin/admin)"
    echo "Kibana: http://localhost:5601"
    echo "Elasticsearch: http://localhost:9200"
    echo "=================================="
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    docker-compose down
    
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理资源..."
    
    docker-compose down -v
    docker system prune -f
    
    log_success "资源清理完成"
}

# 查看日志
view_logs() {
    log_info "查看应用日志..."
    
    docker-compose logs -f app
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_dir="backup_${timestamp}"
    
    mkdir -p "$backup_dir"
    
    # 备份数据库
    docker-compose exec postgres pg_dump -U auto_reduce_user auto_reduce_db > "$backup_dir/database.sql"
    
    # 备份应用数据
    cp -r data "$backup_dir/"
    cp -r reports "$backup_dir/"
    cp -r logs "$backup_dir/"
    
    # 压缩备份
    tar -czf "${backup_dir}.tar.gz" "$backup_dir"
    rm -rf "$backup_dir"
    
    log_success "数据备份完成: ${backup_dir}.tar.gz"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份文件路径"
        exit 1
    fi
    
    backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_info "恢复数据..."
    
    # 解压备份
    tar -xzf "$backup_file"
    backup_dir=$(basename "$backup_file" .tar.gz)
    
    # 恢复数据库
    if [ -f "$backup_dir/database.sql" ]; then
        docker-compose exec -T postgres psql -U auto_reduce_user auto_reduce_db < "$backup_dir/database.sql"
    fi
    
    # 恢复应用数据
    if [ -d "$backup_dir/data" ]; then
        cp -r "$backup_dir/data" ./
    fi
    
    if [ -d "$backup_dir/reports" ]; then
        cp -r "$backup_dir/reports" ./
    fi
    
    if [ -d "$backup_dir/logs" ]; then
        cp -r "$backup_dir/logs" ./
    fi
    
    # 清理临时文件
    rm -rf "$backup_dir"
    
    log_success "数据恢复完成"
}

# 主函数
main() {
    case "$1" in
        "start")
            check_docker
            check_env
            create_directories
            build_app
            start_services
            check_services
            show_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 5
            start_services
            check_services
            show_services
            ;;
        "status")
            docker-compose ps
            ;;
        "logs")
            view_logs
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            echo "用法: $0 {start|stop|restart|status|logs|backup|restore|cleanup|help}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动所有服务"
            echo "  stop     - 停止所有服务"
            echo "  restart  - 重启所有服务"
            echo "  status   - 查看服务状态"
            echo "  logs     - 查看应用日志"
            echo "  backup   - 备份数据"
            echo "  restore  - 恢复数据 (需要指定备份文件)"
            echo "  cleanup  - 清理资源"
            echo "  help     - 显示帮助信息"
            ;;
    esac
}

# 执行主函数
main "$@"

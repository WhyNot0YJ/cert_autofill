#!/bin/bash

# 证书管理系统 Docker 部署脚本
# 使用方法: ./deploy.sh [dev|prod]

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
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 检查环境变量文件
check_env() {
    local env_type=$1
    if [ ! -f .env ]; then
        log_warning "未找到 .env 文件，将使用默认配置"
        if [ "$env_type" = "prod" ]; then
            cp env.production .env
            log_info "已创建生产环境配置文件 .env，请根据实际情况修改配置"
        else
            cp env.development .env
            log_info "已创建开发环境配置文件 .env，请根据实际情况修改配置"
        fi
    else
        log_success "环境变量文件检查通过"
    fi
}

# 构建镜像
build_images() {
    log_info "开始构建 Docker 镜像..."
    
    # 构建后端镜像
    log_info "构建后端镜像..."
    docker build -t cert-autofill-backend:latest ./backend
    
    # 构建前端镜像
    log_info "构建前端镜像..."
    docker build -t cert-autofill-frontend:latest ./frontend
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    local profile=$1
    
    log_info "启动服务 (profile: $profile)..."
    
    if [ "$profile" = "prod" ]; then
        docker-compose --profile production up -d
    else
        docker-compose up -d
    fi
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 等待服务启动
    sleep 10
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_success "所有服务运行正常"
        
        # 显示服务状态
        echo ""
        docker-compose ps
        echo ""
        
        # 显示访问地址
        log_info "服务访问地址:"
        log_info "前端: http://localhost"
        log_info "后端API: http://localhost:5000"
        
    else
        log_error "服务启动失败，请检查日志"
        docker-compose logs
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理 Docker 资源..."
    
    # 停止并删除容器
    docker-compose down -v
    
    # 删除镜像
    docker rmi cert-autofill-backend:latest cert-autofill-frontend:latest 2>/dev/null || true
    
    # 清理未使用的资源
    docker system prune -f
    
    log_success "清理完成"
}

# 查看日志
show_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        log_info "显示所有服务日志..."
        docker-compose logs -f
    else
        log_info "显示 $service 服务日志..."
        docker-compose logs -f "$service"
    fi
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务重启完成"
}

# 备份数据
backup_data() {
    local backup_dir="./backups/$(date +%Y%m%d_%H%M%S)"
    
    log_info "备份数据到 $backup_dir..."
    
    mkdir -p "$backup_dir"
    
    # 备份数据库
    docker cp cert-autofill-backend:/app/cert_autofill.db "$backup_dir/" 2>/dev/null || true
    
    # 备份上传文件
    docker cp cert-autofill-backend:/app/uploads "$backup_dir/" 2>/dev/null || true
    
    log_success "数据备份完成: $backup_dir"
}

# 主函数
main() {
    local action=${1:-"dev"}
    
    case $action in
        "dev")
            log_info "部署开发环境..."
            check_docker
            check_env "dev"
            build_images
            start_services "dev"
            check_services
            ;;
        "prod")
            log_info "部署生产环境..."
            check_docker
            check_env "prod"
            build_images
            start_services "prod"
            check_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs $2
            ;;
        "backup")
            backup_data
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            echo "使用方法: $0 [命令]"
            echo ""
            echo "命令:"
            echo "  dev     部署开发环境"
            echo "  prod    部署生产环境"
            echo "  stop    停止服务"
            echo "  restart 重启服务"
            echo "  logs    查看日志 (可选: 服务名)"
            echo "  backup  备份数据"
            echo "  cleanup 清理资源"
            echo "  help    显示帮助信息"
            ;;
        *)
            log_error "未知命令: $action"
            echo "使用 '$0 help' 查看帮助信息"
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"

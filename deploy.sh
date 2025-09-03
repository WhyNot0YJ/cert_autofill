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
    local env_file="env.development"
    if [ "$env_type" = "prod" ]; then
        env_file="env.production"
    fi

    if [ ! -f "$env_file" ]; then
        log_error "未找到 $env_file，请先创建该文件"
        exit 1
    fi

    log_success "环境变量文件检查通过 ($env_file)"
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
    local use_build=$2

    log_info "启动服务 (profile: $profile)..."

    if [ "$profile" = "prod" ]; then
        if [ "$use_build" = "true" ]; then
            log_info "强制重新构建镜像..."
            docker-compose --env-file env.production --profile production up --build -d
        else
            docker-compose --env-file env.production --profile production up -d
        fi
    else
        # 开发环境使用dev配置文件
        if [ "$use_build" = "true" ]; then
            log_info "强制重新构建镜像..."
            docker-compose --env-file env.development -f docker-compose.dev.yml up --build -d
        else
            docker-compose --env-file env.development -f docker-compose.dev.yml up -d
        fi
    fi

    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    local profile=$1
    log_info "检查服务状态..."

    # 等待服务启动
    sleep 10

    # 检查容器状态
    local env_file="env.development"
    if [ "$profile" = "prod" ]; then
        compose_cmd="docker-compose --env-file env.production"
        env_file="env.production"
    else
        compose_cmd="docker-compose --env-file env.development -f docker-compose.dev.yml"
    fi
    
    if $compose_cmd ps | grep -q "Up"; then
        log_success "所有服务运行正常"

        # 显示服务状态
        echo ""
        $compose_cmd ps
        echo ""

        # 根据环境配置显示访问地址
        log_info "服务访问地址:"

        # 读取对应 env 文件
        local server_url=$(grep "^SERVER_URL=" "$env_file" 2>/dev/null | cut -d'=' -f2- || echo "http://localhost")
        local backend_port_prod=$(grep "^BACKEND_PORT_PROD=" "$env_file" 2>/dev/null | cut -d'=' -f2- || echo "5000")
        local frontend_port_prod=$(grep "^FRONTEND_PORT_PROD=" "$env_file" 2>/dev/null | cut -d'=' -f2- || echo "80")
        local backend_port_dev=$(grep "^BACKEND_PORT_DEV=" "$env_file" 2>/dev/null | cut -d'=' -f2- || echo "5000")
        local frontend_port_dev=$(grep "^FRONTEND_PORT_DEV=" "$env_file" 2>/dev/null | cut -d'=' -f2- || echo "80")

        # 提取主机部分（去掉协议和端口）
        local host=$(echo "$server_url" | sed 's|http://||' | sed 's/:.*//')

        if [ "$profile" = "prod" ]; then
            log_info "前端: http://$host:$frontend_port_prod"
            log_info "后端API: http://$host:$backend_port_prod"
            log_info "健康检查: http://$host:$backend_port_prod/api/health"
        else
            log_info "前端: http://localhost:$frontend_port_dev"
            log_info "后端API: http://localhost:$backend_port_dev"
            log_info "健康检查: http://localhost:$backend_port_dev/api/health"
        fi

    else
        log_error "服务启动失败，请检查日志"
        $compose_cmd logs
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    # 尝试停止开发环境
    if [ -f docker-compose.dev.yml ]; then
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    fi
    
    # 停止生产环境
    docker-compose down 2>/dev/null || true
    
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理 Docker 资源..."
    
    # 停止并删除容器
    if [ -f docker-compose.dev.yml ]; then
        docker-compose -f docker-compose.dev.yml down -v 2>/dev/null || true
    fi
    docker-compose down -v 2>/dev/null || true
    
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
    local use_build="false"

    # 检查是否有--build参数
    if [ "$2" = "--build" ] || [ "$1" = "--build" ]; then
        use_build="true"
        if [ "$2" = "--build" ]; then
            # 如果第二个参数是--build，第一个参数是action
            action=${1:-"dev"}
        else
            # 如果第一个参数是--build，默认使用dev
            action="dev"
        fi
    fi

    case $action in
        "dev")
            log_info "部署开发环境..."
            check_docker
            check_env "dev"
            if [ "$use_build" != "true" ]; then
                build_images
            fi
            start_services "dev" "$use_build"
            check_services "dev"
            ;;
        "prod")
            log_info "部署生产环境..."
            check_docker
            check_env "prod"
            if [ "$use_build" != "true" ]; then
                build_images
            fi
            start_services "prod" "$use_build"
            check_services "prod"
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
            echo "使用方法: $0 [命令] [--build]"
            echo ""
            echo "命令:"
            echo "  dev [--build]     部署开发环境"
            echo "  prod [--build]    部署生产环境"
            echo "  stop              停止服务"
            echo "  restart           重启服务"
            echo "  logs              查看日志 (可选: 服务名)"
            echo "  backup            备份数据"
            echo "  cleanup           清理资源"
            echo "  help              显示帮助信息"
            echo ""
            echo "选项:"
            echo "  --build           强制重新构建镜像 (解决依赖更新问题)"
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

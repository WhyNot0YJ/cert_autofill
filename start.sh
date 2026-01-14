#!/bin/bash

# 启动脚本 - 支持开发和生产环境

echo "请选择运行环境："
echo "1) 开发环境 (development)"
echo "2) 生产环境 (production)"
echo "3) 使用Docker Compose"
read -p "请输入选择 (1-3): " choice

# 加载环境变量的辅助函数（过滤注释和空行）
load_env_file() {
    local env_file=$1
    while IFS= read -r line || [ -n "$line" ]; do
        # 跳过空行和注释行
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        # 导出环境变量
        export "$line" 2>/dev/null || true
    done < "$env_file"
}

# 检测 Python 命令
detect_python() {
    # 检查虚拟环境
    if [ -f "backend/venv/bin/python" ]; then
        echo "backend/venv/bin/python"
    elif [ -f "backend/venv/bin/python3" ]; then
        echo "backend/venv/bin/python3"
    elif command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        echo ""
    fi
}

case $choice in
    1)
        echo "启动开发环境..."
        load_env_file env.development
        
        # 检测 Python 命令
        PYTHON_CMD=$(detect_python)
        if [ -z "$PYTHON_CMD" ]; then
            echo "错误: 未找到 Python 命令，请确保已安装 Python 3.8+"
            exit 1
        fi
        
        # 如果使用虚拟环境，激活它
        if [[ "$PYTHON_CMD" == backend/venv/* ]]; then
            source backend/venv/bin/activate 2>/dev/null || true
            PYTHON_CMD="python"
        fi
        
        # 启动后端
        echo "启动后端服务 (端口: ${BACKEND_PORT_DEV:-5000})..."
        cd backend
        $PYTHON_CMD run.py &
        BACKEND_PID=$!
        cd ..
        
        # 启动前端
        echo "启动前端服务 (端口: ${FRONTEND_PORT_DEV:-80})..."
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo "服务已启动！"
        echo "后端: http://localhost:${BACKEND_PORT_DEV:-5000}"
        echo "前端: http://localhost:${FRONTEND_PORT_DEV:-80}"
        echo ""
        echo "按 Ctrl+C 停止服务"
        
        # 等待中断信号
        trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
        ;;
    2)
        echo "启动生产环境..."
        load_env_file env.production
        
        # 检测 Python 命令
        PYTHON_CMD=$(detect_python)
        if [ -z "$PYTHON_CMD" ]; then
            echo "错误: 未找到 Python 命令，请确保已安装 Python 3.8+"
            exit 1
        fi
        
        # 如果使用虚拟环境，激活它
        if [[ "$PYTHON_CMD" == backend/venv/* ]]; then
            source backend/venv/bin/activate 2>/dev/null || true
            PYTHON_CMD="python"
        fi
        
        # 启动后端
        echo "启动后端服务 (端口: ${BACKEND_PORT_PROD:-5000})..."
        cd backend
        $PYTHON_CMD run.py &
        BACKEND_PID=$!
        cd ..
        
        # 启动前端
        echo "启动前端服务 (端口: ${FRONTEND_PORT_PROD:-80})..."
        cd frontend
        npm run build
        npm run preview &
        FRONTEND_PID=$!
        cd ..
        
        echo "服务已启动！"
        echo "后端: http://localhost:${BACKEND_PORT_PROD:-5000}"
        echo "前端: http://localhost:${FRONTEND_PORT_PROD:-80}"
        echo ""
        echo "按 Ctrl+C 停止服务"
        
        # 等待中断信号
        trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
        ;;
    3)
        echo "使用Docker Compose启动..."
        echo "请确保已安装Docker和Docker Compose"
        echo ""
        echo "选择环境："
        echo "1) 开发环境"
        echo "2) 生产环境 (包含Nginx和Redis)"
        read -p "请输入选择 (1-2): " docker_choice
        
        case $docker_choice in
            1)
                load_env_file env.development
                docker-compose up backend frontend
                ;;
            2)
                load_env_file env.production
                docker-compose --profile production up
                ;;
            *)
                echo "无效选择"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

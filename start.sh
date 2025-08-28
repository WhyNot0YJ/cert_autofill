#!/bin/bash

# 启动脚本 - 支持开发和生产环境

echo "请选择运行环境："
echo "1) 开发环境 (development)"
echo "2) 生产环境 (production)"
echo "3) 使用Docker Compose"
read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "启动开发环境..."
        export $(cat env.development | xargs)
        
        # 启动后端
        echo "启动后端服务 (端口: $BACKEND_PORT_DEV)..."
        cd backend
        python run.py &
        BACKEND_PID=$!
        cd ..
        
        # 启动前端
        echo "启动前端服务 (端口: $FRONTEND_PORT_DEV)..."
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo "服务已启动！"
        echo "后端: http://localhost:$BACKEND_PORT_DEV"
        echo "前端: http://localhost:$FRONTEND_PORT_DEV"
        echo ""
        echo "按 Ctrl+C 停止服务"
        
        # 等待中断信号
        trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
        wait
        ;;
    2)
        echo "启动生产环境..."
        export $(cat env.production | xargs)
        
        # 启动后端
        echo "启动后端服务 (端口: $BACKEND_PORT_PROD)..."
        cd backend
        python run.py &
        BACKEND_PID=$!
        cd ..
        
        # 启动前端
        echo "启动前端服务 (端口: $FRONTEND_PORT_PROD)..."
        cd frontend
        npm run build
        npm run preview &
        FRONTEND_PID=$!
        cd ..
        
        echo "服务已启动！"
        echo "后端: http://localhost:$BACKEND_PORT_PROD"
        echo "前端: http://localhost:$FRONTEND_PORT_PROD"
        echo ""
        echo "按 Ctrl+C 停止服务"
        
        # 等待中断信号
        trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
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
                export $(cat env.development | xargs)
                docker-compose up backend frontend
                ;;
            2)
                export $(cat env.production | xargs)
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

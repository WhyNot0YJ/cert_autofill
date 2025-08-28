@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 请选择运行环境：
echo 1) 开发环境 (development)
echo 2) 生产环境 (production)
echo 3) 使用Docker Compose
set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    echo 启动开发环境...
    
    REM 加载开发环境变量
    for /f "tokens=1,* delims==" %%a in (env.development) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    
    echo 启动后端服务 (端口: %BACKEND_PORT_DEV%)...
    cd backend
    start "Backend" python run.py
    cd ..
    
    echo 启动前端服务 (端口: %FRONTEND_PORT_DEV%)...
    cd frontend
    start "Frontend" npm run dev
    cd ..
    
    echo 服务已启动！
    echo 后端: http://localhost:%BACKEND_PORT_DEV%
    echo 前端: http://localhost:%FRONTEND_PORT_DEV%
    echo.
    echo 按任意键退出...
    pause >nul
    
) else if "%choice%"=="2" (
    echo 启动生产环境...
    
    REM 加载生产环境变量
    for /f "tokens=1,* delims==" %%a in (env.production) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    
    echo 启动后端服务 (端口: %BACKEND_PORT_PROD%)...
    cd backend
    start "Backend" python run.py
    cd ..
    
    echo 启动前端服务 (端口: %FRONTEND_PORT_PROD%)...
    cd frontend
    start "Frontend" npm run build
    start "Frontend Preview" npm run preview
    cd ..
    
    echo 服务已启动！
    echo 后端: http://localhost:%BACKEND_PORT_PROD%
    echo 前端: http://localhost:%FRONTEND_PORT_PROD%
    echo.
    echo 按任意键退出...
    pause >nul
    
) else if "%choice%"=="3" (
    echo 使用Docker Compose启动...
    echo 请确保已安装Docker和Docker Compose
    echo.
    echo 选择环境：
    echo 1) 开发环境
    echo 2) 生产环境 (包含Nginx和Redis)
    set /p docker_choice=请输入选择 (1-2): 
    
    if "!docker_choice!"=="1" (
        for /f "tokens=1,* delims==" %%a in (env.development) do (
            if not "%%a"=="" if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
            )
        )
        docker-compose up backend frontend
    ) else if "!docker_choice!"=="2" (
        for /f "tokens=1,* delims==" %%a in (env.production) do (
            if not "%%a"=="" if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
            )
        )
        docker-compose --profile production up
    ) else (
        echo 无效选择
        goto :eof
    )
    
) else (
    echo 无效选择
    goto :eof
)

endlocal

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title CertAutofill 一键启动 [Windows 方案]

REM =================================================================
REM  CertAutofill - Windows 一键启动脚本
REM  说明：后端依赖 Microsoft Word COM (pywin32)，仅支持 Windows 运行
REM  作者：romainyu
REM =================================================================

set "ROOT_DIR=%~dp0"
set "ROOT_DIR=%ROOT_DIR:~0,-1%"
set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

REM ---------- 菜单 ----------
:MENU
cls
echo.
echo  =====================================================
echo     CertAutofill 一键启动 ^| Windows 原生方案
echo  =====================================================
echo.
echo     1^) 启动开发环境   ^(前端 Vite 热更新 + 后端 Flask^)
echo     2^) 启动生产环境   ^(前端 build + preview + 后端^)
echo     3^) 仅启动后端     ^(python run.py^)
echo     4^) 仅启动前端     ^(npm run dev^)
echo     5^) 环境自检       ^(检查 Python/Node/Word/依赖^)
echo     6^) 停止所有服务
echo     0^) 退出
echo.
echo  -----------------------------------------------------
echo   提示：后端依赖 Microsoft Word，不支持 Docker 部署
echo  -----------------------------------------------------
echo.
set "choice="
set /p choice=请输入选择 (0-6): 

if "%choice%"=="1" goto DEV
if "%choice%"=="2" goto PROD
if "%choice%"=="3" goto ONLY_BACKEND
if "%choice%"=="4" goto ONLY_FRONTEND
if "%choice%"=="5" goto CHECK_ENV
if "%choice%"=="6" goto STOP_ALL
if "%choice%"=="0" goto END
echo [错误] 无效选择，请重新输入...
timeout /t 2 >nul
goto MENU


REM =================================================================
REM  环境自检
REM =================================================================
:CHECK_ENV
cls
echo.
echo  ============ 环境自检 ============
echo.

REM --- Python ---
set "PY_CMD="
if exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    set "PY_CMD=%BACKEND_DIR%\venv\Scripts\python.exe"
    echo   [OK ] Python 虚拟环境: backend\venv
) else (
    where python >nul 2>&1
    if !errorlevel! == 0 (
        set "PY_CMD=python"
        echo   [OK ] Python 已安装（系统 PATH）
    ) else (
        echo   [ERR] 未找到 Python，请安装 Python 3.8+
    )
)
if defined PY_CMD (
    for /f "tokens=*" %%v in ('"!PY_CMD!" --version 2^>^&1') do echo        版本: %%v
)

REM --- pywin32 (Word COM 依赖) ---
if defined PY_CMD (
    "!PY_CMD!" -c "import win32com.client" >nul 2>&1
    if !errorlevel! == 0 (
        echo   [OK ] pywin32 已安装（Word COM 可用）
    ) else (
        echo   [ERR] pywin32 未安装！请执行: pip install pywin32
    )
)

REM --- Node.js ---
where node >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=*" %%v in ('node --version') do echo   [OK ] Node.js 版本: %%v
) else (
    echo   [ERR] 未找到 Node.js，请安装 Node 18+
)

REM --- npm ---
where npm >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK ] npm 可用
) else (
    echo   [ERR] 未找到 npm
)

REM --- 前端依赖 ---
if exist "%FRONTEND_DIR%\node_modules" (
    echo   [OK ] 前端依赖已安装 (node_modules 存在)
) else (
    echo   [WARN] 前端依赖未安装，启动时会自动执行 npm install
)

REM --- Microsoft Word ---
reg query "HKEY_CLASSES_ROOT\Word.Application" >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK ] Microsoft Word 已安装（COM 注册表已注册）
) else (
    echo   [ERR] 未检测到 Microsoft Word，PDF 导出将失败
)

REM --- 环境文件 ---
if exist "%ROOT_DIR%\env.development" (
    echo   [OK ] env.development 存在
) else (
    echo   [WARN] env.development 不存在，将使用默认端口
)
if exist "%ROOT_DIR%\env.production" (
    echo   [OK ] env.production 存在
) else (
    echo   [WARN] env.production 不存在，将使用默认端口
)

echo.
echo  ==================================
echo.
pause
goto MENU


REM =================================================================
REM  加载 env 文件（Windows 原生方式，跳过空行和注释）
REM =================================================================
:LOAD_ENV
set "ENV_FILE=%~1"
if not exist "%ENV_FILE%" goto :eof
for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
    set "line=%%a"
    if defined line (
        set "first=!line:~0,1!"
        if not "!first!"=="#" (
            if not "%%b"=="" set "%%a=%%b"
        )
    )
)
goto :eof


REM =================================================================
REM  检测 Python 命令（优先 venv）
REM =================================================================
:DETECT_PYTHON
set "PY_CMD="
if exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    set "PY_CMD=%BACKEND_DIR%\venv\Scripts\python.exe"
    goto :eof
)
where python >nul 2>&1
if %errorlevel% == 0 (
    set "PY_CMD=python"
    goto :eof
)
where python3 >nul 2>&1
if %errorlevel% == 0 (
    set "PY_CMD=python3"
    goto :eof
)
goto :eof


REM =================================================================
REM  开发环境：启动前后端
REM =================================================================
:DEV
cls
echo.
echo  ============ 启动开发环境 ============
echo.
call :LOAD_ENV "%ROOT_DIR%\env.development"
if not defined BACKEND_PORT_DEV  set "BACKEND_PORT_DEV=5000"
if not defined FRONTEND_PORT_DEV set "FRONTEND_PORT_DEV=80"

call :DETECT_PYTHON
if not defined PY_CMD (
    echo [错误] 未找到 Python，请安装后再试。
    pause & goto MENU
)
echo   Python: !PY_CMD!

REM 检查前端依赖
if not exist "%FRONTEND_DIR%\node_modules" (
    echo   [提示] 前端依赖未安装，正在执行 npm install ...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)

echo.
echo   启动后端服务  (端口: !BACKEND_PORT_DEV!) ...
start "CertAutofill-Backend [DEV:!BACKEND_PORT_DEV!]" cmd /k "cd /d "%BACKEND_DIR%" && "!PY_CMD!" run.py"

timeout /t 2 >nul

echo   启动前端服务  (端口: !FRONTEND_PORT_DEV!) ...
start "CertAutofill-Frontend [DEV:!FRONTEND_PORT_DEV!]" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

echo.
echo  ======================================
echo   服务已启动（分别在独立窗口运行）
echo   后端: http://localhost:!BACKEND_PORT_DEV!
echo   前端: http://localhost:!FRONTEND_PORT_DEV!
echo  ======================================
echo.
echo   3 秒后自动打开浏览器 ...
timeout /t 3 >nul
start "" "http://localhost:!FRONTEND_PORT_DEV!"
echo.
pause
goto MENU


REM =================================================================
REM  生产环境
REM =================================================================
:PROD
cls
echo.
echo  ============ 启动生产环境 ============
echo.
call :LOAD_ENV "%ROOT_DIR%\env.production"
if not defined BACKEND_PORT_PROD  set "BACKEND_PORT_PROD=5000"
if not defined FRONTEND_PORT_PROD set "FRONTEND_PORT_PROD=80"

call :DETECT_PYTHON
if not defined PY_CMD (
    echo [错误] 未找到 Python，请安装后再试。
    pause & goto MENU
)

echo   构建前端 ...
pushd "%FRONTEND_DIR%"
if not exist "node_modules" call npm install
call npm run build
popd

echo.
echo   启动后端服务  (端口: !BACKEND_PORT_PROD!) ...
start "CertAutofill-Backend [PROD:!BACKEND_PORT_PROD!]" cmd /k "cd /d "%BACKEND_DIR%" && set FLASK_ENV=production && "!PY_CMD!" run.py"

timeout /t 2 >nul

echo   启动前端预览  (端口: !FRONTEND_PORT_PROD!) ...
start "CertAutofill-Frontend [PROD:!FRONTEND_PORT_PROD!]" cmd /k "cd /d "%FRONTEND_DIR%" && npm run preview"

echo.
echo  ======================================
echo   生产环境服务已启动
echo   后端: http://localhost:!BACKEND_PORT_PROD!
echo   前端: http://localhost:!FRONTEND_PORT_PROD!
echo  ======================================
echo.
pause
goto MENU


REM =================================================================
REM  仅启动后端
REM =================================================================
:ONLY_BACKEND
cls
echo.
echo  ============ 仅启动后端 ============
call :LOAD_ENV "%ROOT_DIR%\env.development"
if not defined BACKEND_PORT_DEV set "BACKEND_PORT_DEV=5000"
call :DETECT_PYTHON
if not defined PY_CMD (
    echo [错误] 未找到 Python。
    pause & goto MENU
)
start "CertAutofill-Backend [!BACKEND_PORT_DEV!]" cmd /k "cd /d "%BACKEND_DIR%" && "!PY_CMD!" run.py"
echo   后端已在独立窗口启动: http://localhost:!BACKEND_PORT_DEV!
echo.
pause
goto MENU


REM =================================================================
REM  仅启动前端
REM =================================================================
:ONLY_FRONTEND
cls
echo.
echo  ============ 仅启动前端 ============
call :LOAD_ENV "%ROOT_DIR%\env.development"
if not defined FRONTEND_PORT_DEV set "FRONTEND_PORT_DEV=80"
if not exist "%FRONTEND_DIR%\node_modules" (
    echo   [提示] 安装前端依赖 ...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)
start "CertAutofill-Frontend [!FRONTEND_PORT_DEV!]" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"
echo   前端已在独立窗口启动: http://localhost:!FRONTEND_PORT_DEV!
echo.
pause
goto MENU


REM =================================================================
REM  停止所有服务（关闭标题包含 CertAutofill 的窗口）
REM =================================================================
:STOP_ALL
cls
echo.
echo  ============ 停止所有服务 ============
echo.
echo   正在关闭 CertAutofill 相关窗口 ...
taskkill /FI "WINDOWTITLE eq CertAutofill-Backend*"  /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq CertAutofill-Frontend*" /T /F >nul 2>&1
echo   已发送终止信号。
echo.
echo   如仍有残留，请根据端口手动结束：
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5000 " ^| findstr LISTENING') do (
    echo     后端(5000) PID: %%p  ^=^> taskkill /PID %%p /F
)
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":80 " ^| findstr LISTENING') do (
    echo     前端(80)   PID: %%p  ^=^> taskkill /PID %%p /F
)
echo.
pause
goto MENU


:END
endlocal
exit /b 0

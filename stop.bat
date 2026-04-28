@echo off
chcp 65001 >nul
title CertAutofill 停止服务

echo.
echo  ============ 停止 CertAutofill 所有服务 ============
echo.

REM 关闭所有标题以 CertAutofill- 开头的窗口
echo   [1/3] 关闭后端窗口 ...
taskkill /FI "WINDOWTITLE eq CertAutofill-Backend*" /T /F >nul 2>&1

echo   [2/3] 关闭前端窗口 ...
taskkill /FI "WINDOWTITLE eq CertAutofill-Frontend*" /T /F >nul 2>&1

echo   [3/3] 按端口清理残留进程 ...

REM 清理 5000 端口（后端）
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5000 " ^| findstr LISTENING') do (
    echo         - 终止后端进程 PID=%%p
    taskkill /PID %%p /F >nul 2>&1
)

REM 清理 80 端口（前端）
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":80 " ^| findstr LISTENING') do (
    echo         - 终止前端进程 PID=%%p
    taskkill /PID %%p /F >nul 2>&1
)

REM 清理常见 Vite 端口
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173 " ^| findstr LISTENING') do (
    taskkill /PID %%p /F >nul 2>&1
)
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":4173 " ^| findstr LISTENING') do (
    taskkill /PID %%p /F >nul 2>&1
)

echo.
echo  ============ 已完成 ============
echo.
timeout /t 2 >nul
exit /b 0

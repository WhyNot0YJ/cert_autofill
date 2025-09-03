# 证书管理系统 Docker 部署指南（Windows）

## 一、前提条件
- **系统要求**：Windows 10/11（专业版优先），或 Windows Server 2019+
- **WSL2要求**：已启用 WSL2（Docker Desktop 依赖）
- **网络要求**：内网环境，确保服务器间网络互通
- **端口要求**：80（前端）、5001（后端API）
- **硬件要求**：至少 4GB RAM，20GB 可用磁盘空间

## 二、安装 Docker Desktop

### 2.1 下载安装
1. 下载 Docker Desktop：`https://www.docker.com/products/docker-desktop`
2. 安装过程中勾选 "Use WSL 2 instead of Hyper-V"
3. 重启计算机（如需要）

### 2.2 配置 WSL2 集成
1. 启动 Docker Desktop
2. 进入 Settings -> Resources -> WSL Integration
3. 启用 "Enable integration with my default WSL distro"
4. 启用您使用的 WSL 发行版（如 Ubuntu）

### 2.3 验证安装
```powershell
# PowerShell 验证
wsl -l -v
docker --version
docker-compose --version

# 测试 Docker 运行
docker run hello-world
```

### 2.4 常见安装问题
- **WSL2 未启用**：以管理员身份运行 `wsl --install`
- **Hyper-V 冲突**：确保选择 WSL2 而不是 Hyper-V
- **权限问题**：确保用户有管理员权限

## 三、获取项目并配置环境

### 3.1 获取项目代码
**推荐使用 WSL Shell**（避免路径和权限问题）：

```bash
# WSL Shell 中执行
git clone <your-repo-url>
cd cert_autofill
```

**或使用 PowerShell**：
```powershell
# PowerShell 中执行
git clone <your-repo-url>
cd cert_autofill
```

### 3.2 配置环境变量
```bash
# WSL Shell 中执行
cp env.production .env
nano .env
```

**或使用 PowerShell**：
```powershell
# PowerShell 中执行
Copy-Item env.production .env
notepad .env
```

### 3.3 重要配置项说明
```bash
# 服务器地址配置（内网部署关键）
SERVER_URL=http://192.168.1.100  # 替换为您的内网IP地址

# 端口配置
BACKEND_PORT_PROD=5001
FRONTEND_PORT_PROD=81

# 安全配置
SECRET_KEY=your-super-secret-production-key-here-change-this  # 请修改为复杂密钥

# AI服务配置
DIFY_API_KEY=app-aOHstplRYJhO3uadmVwKnf8E
DIFY_API_BASE=https://api.dify.ai/v1

# 数据库配置
DATABASE_URL=sqlite:///cert_autofill.db
```

### 3.4 内网部署特殊配置
对于Windows内网环境，需要特别注意：

1. **SERVER_URL配置**：设置为内网可访问的IP地址
2. **Windows防火墙**：确保80和5001端口开放
3. **WSL网络**：确保WSL可以访问内网其他设备

## 四、一键部署（推荐）

### 4.1 准备部署脚本
**在 WSL Shell 中执行**（推荐）：
```bash
# 转换换行符并赋予执行权限
dos2unix deploy.sh 2>/dev/null || true
chmod +x deploy.sh

# 验证脚本权限
ls -la deploy.sh
```

**或在 PowerShell 中执行**：
```powershell
# 检查文件权限
Get-ChildItem deploy.sh

# 如果需要，使用 WSL 执行脚本
wsl chmod +x deploy.sh
```

### 4.2 内网生产环境部署
```bash
# 在 WSL Shell 中执行（前端端口81，后端端口5001）
./deploy.sh prod

# 如果遇到依赖更新问题，强制重新构建
./deploy.sh prod --build
```

### 4.3 开发环境部署（可选）
```bash
# 开发环境部署（前端端口80，后端端口5000）
./deploy.sh dev

# 开发环境强制重新构建
./deploy.sh dev --build
```

### 4.4 服务管理命令
```bash
# 查看所有可用命令
./deploy.sh help

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs

# 备份数据
./deploy.sh backup

# 清理资源
./deploy.sh cleanup
```

### 4.5 部署验证
部署完成后，通过以下方式验证：

**访问地址**：
- **生产环境**：
  - 前端：`http://您的内网IP:81`
  - 后端API：`http://您的内网IP:5001/api`
  - 健康检查：`http://您的内网IP:5001/api/health`
- **开发环境**：
  - 前端：`http://您的内网IP:80`
  - 后端API：`http://您的内网IP:5000/api`
  - 健康检查：`http://您的内网IP:5000/api/health`

**验证步骤**：
```bash
# 在 WSL Shell 中检查容器状态
docker-compose ps

# 检查服务日志
./deploy.sh logs

# 测试健康检查
curl http://localhost:5000/api/health
```

**或在 PowerShell 中验证**：
```powershell
# 检查容器状态
docker-compose ps

# 测试健康检查
Invoke-WebRequest -Uri "http://localhost:5000/api/health"
```

## 五、手动部署（可选）
可在 PowerShell 或 WSL Shell 执行：
```powershell
# 构建镜像
docker-compose build

# 启动（默认前后端）
docker-compose up -d

# 启动（生产 profile，含外部 nginx 容器）
docker-compose --profile production up -d

# 依赖更新后的重新构建和启动
docker-compose up --build -d
docker-compose --profile production up --build -d
```

## 六、常用运维命令
```powershell
# 查看容器状态
docker-compose ps

# 查看日志（全部/指定服务）
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启/停止（建议在 WSL Shell 内执行）
./deploy.sh restart
./deploy.sh stop

# 备份（数据库与上传文件）
./deploy.sh backup
```

## 七、Windows防火墙配置

### 7.1 开放必要端口
```powershell
# 以管理员身份运行 PowerShell
# 开放80端口（前端）
New-NetFirewallRule -DisplayName "Cert System Frontend" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# 开放5001端口（后端API）
New-NetFirewallRule -DisplayName "Cert System Backend" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow

# 查看防火墙规则
Get-NetFirewallRule -DisplayName "*Cert System*"
```

### 7.2 图形界面配置
1. 打开 Windows Defender 防火墙
2. 点击"高级设置"
3. 选择"入站规则" -> "新建规则"
4. 选择"端口" -> "TCP" -> "特定本地端口" -> 输入"80,5001"
5. 选择"允许连接" -> 应用到所有配置文件

## 八、内网部署配置要点

### 8.1 网络配置
- **SERVER_URL**：必须设置为内网可访问的IP地址
- **端口映射**：确保80和5001端口在防火墙中开放
- **WSL网络**：确保WSL可以访问内网其他设备

### 8.2 访问方式
- **生产环境**：
  - 内网访问：`http://内网IP:81`
  - API访问：`http://内网IP:5001/api`
  - 健康检查：`http://内网IP:5001/api/health`
- **开发环境**：
  - 内网访问：`http://内网IP:80`
  - API访问：`http://内网IP:5000/api`
  - 健康检查：`http://内网IP:5000/api/health`

### 8.3 安全建议
- 修改默认的SECRET_KEY
- 定期备份数据库和上传文件
- 监控系统资源使用情况

## 九、注意事项
- **WSL路径**：建议在WSL的项目目录内执行Docker命令，避免路径与权限问题
- **文件换行符**：从Windows编辑的脚本在WSL下运行前，执行 `dos2unix deploy.sh`
- **端口占用**：确保80/5001未被其他程序（如IIS）占用
- **权限问题**：首次运行Docker Desktop需管理员权限
- **WSL集成**：确保Docker Desktop的WSL集成已正确配置

## 十、排障速查

### 10.1 基础检查命令
```powershell
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 进入容器
docker exec -it cert-autofill-backend bash

# 查看端口占用
netstat -aon | findstr ":80"
netstat -aon | findstr ":5001"
```

### 10.2 服务状态检查
```powershell
# 检查服务健康状态
Invoke-WebRequest -Uri "http://localhost:5000/api/health"

# 检查前端服务
Invoke-WebRequest -Uri "http://localhost"

# 检查WSL状态
wsl -l -v
```

### 10.3 WSL相关检查
```bash
# 在WSL中检查
docker --version
docker-compose --version

# 检查WSL网络
ip addr show
```

## 十一、常见问题与解决方案

### 11.1 依赖更新后容器启动失败

**问题现象**：
```
exec: "gunicorn": executable file not found in $PATH
```

**解决方案**：
```bash
# 在WSL Shell中执行
./deploy.sh prod --build

# 手动方式
docker-compose up --build -d
```

**原因**：修改依赖文件后，Docker使用了旧镜像缓存，新依赖没有被安装。

### 11.2 前端构建失败

**问题现象**：
```
sh: vite: not found
npm ERR! missing script: build
```

**解决方案**：
```bash
# 在WSL Shell中执行
./deploy.sh prod --build

# 手动清理并重建
docker-compose down
docker system prune -f
docker-compose up --build -d
```

### 11.3 WSL与Windows文件权限问题

**问题现象**：
```
Permission denied
bash: ./deploy.sh: Permission denied
```

**解决方案**：
```bash
# 在WSL中重新设置文件权限
chmod +x deploy.sh

# 转换Windows换行符
dos2unix deploy.sh

# 检查文件所有权
ls -la deploy.sh
```

### 11.4 Docker Desktop网络连接问题

**问题现象**：
- Docker命令无法执行
- WSL集成失败

**解决方案**：
```powershell
# 重启Docker Desktop
# 或在Docker Desktop设置中重新启用WSL集成

# 检查WSL集成状态
wsl -l -v

# 重新启用WSL集成
wsl --shutdown
# 然后在Docker Desktop中重新启用WSL集成
```

### 11.5 端口占用问题

**问题现象**：
```
bind: address already in use
```

**解决方案**：
```powershell
# 查找占用端口的进程
netstat -aon | findstr ":80"
netstat -aon | findstr ":5001"

# 停止占用进程
taskkill /PID <进程ID> /F
```

### 11.6 磁盘空间不足

**解决方案**：
```bash
# 在WSL中清理Docker资源
docker system prune -a

# 清理未使用的镜像和容器
docker image prune -a
docker container prune

# 使用脚本清理
./deploy.sh cleanup
```

### 11.7 Windows防火墙阻止访问

**问题现象**：
- 外部无法访问服务
- 连接被拒绝

**解决方案**：
```powershell
# 以管理员身份运行PowerShell
# 开放端口
New-NetFirewallRule -DisplayName "Cert System" -Direction Inbound -Protocol TCP -LocalPort 80,5001 -Action Allow

# 或通过图形界面配置防火墙
```

## 十二、升级与回滚

### 12.1 常规升级
```bash
# 在WSL Shell中执行
# 拉取最新代码
git pull

# 使用一键脚本升级（推荐）
./deploy.sh prod --build  # 生产环境
```

### 12.2 手动升级
```bash
# 在WSL Shell中执行
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build
docker-compose up -d

# 生产环境
docker-compose --profile production up --build -d
```

### 12.3 依赖更新升级
当更新了依赖文件时，必须使用 `--build` 选项：
```bash
# 方式1：使用脚本（推荐）
./deploy.sh prod --build

# 方式2：手动命令
docker-compose up --build -d
```

### 12.4 回滚策略
```bash
# 在WSL Shell中执行
# 停止当前服务
docker-compose down

# 回滚到指定版本
git checkout <commit-hash>
docker-compose up --build -d

# 或使用镜像标签
docker-compose pull
docker-compose up -d
```

### 12.5 数据备份与恢复
```bash
# 备份数据
./deploy.sh backup

# 数据恢复（如需要）
# 停止服务
docker-compose down

# 恢复数据卷
docker volume restore backend_data <backup-file>
docker volume restore backend_db <backup-file>

# 重启服务
docker-compose up -d
```

**重要说明**：
- 数据库与上传目录已挂载到命名卷（`backend_data`、`backend_db`），容器重建数据不丢失
- 建议定期备份重要数据
- 升级前请确保已备份当前数据

# 证书管理系统 Docker 部署指南（Windows）

## 一、前提条件
- 系统：Windows 10/11（专业版优先），或 Windows Server 2019+
- 已启用 WSL2（Docker Desktop 依赖）
- 网络端口：80（前端）、5000（后端直连调试时，可选）

## 二、安装 Docker Desktop
1. 下载并安装 Docker Desktop：`https://www.docker.com/products/docker-desktop`
2. 安装过程中勾选 "Use WSL 2 instead of Hyper-V"
3. 首次启动后，确保 Settings -> Resources -> WSL Integration 启用你的发行版（如 Ubuntu）
4. 命令行验证：
```powershell
# PowerShell
wsl -l -v
docker --version
docker-compose --version  # Desktop 内置 v2，可用 docker compose
```

## 三、获取项目并配置环境
可以在 PowerShell、CMD 或者 WSL Shell 中操作（推荐 WSL Shell 一致 Linux 体验）。

```bash
# WSL Shell 示例：
# 1) 获取代码
git clone <your-repo-url>
cd cert_autofill

# 2) 准备环境变量
# 开发环境：
cp env.development .env
# 或生产环境：
# cp env.production .env
nano .env
# 根据需要修改：SECRET_KEY、DIFY_API_KEY、SERVER_URL（无域名用 http://本机IP 或 http://WSL分配的IP）
```

如果使用 PowerShell，可用：
```powershell
# 开发环境：
Copy-Item env.development .env
# 或生产环境：
# Copy-Item env.production .env
notepad .env  # 编辑后保存
```

## 四、一键部署（推荐）
Windows 下建议在 WSL Shell 执行脚本，以避免换行符与权限问题。脚本支持多种部署模式和选项。

### 基础部署
```bash
# 如从 Windows 拷贝过来，先转换换行符并赋权限
dos2unix deploy.sh 2>/dev/null || true
chmod +x deploy.sh

# 开发/内网（HTTP）
./deploy.sh dev

# 生产（仅 80 端口、无证书；如需 HTTPS 与域名，见 Linux 文档）
./deploy.sh prod
```

### 依赖更新部署
当修改了依赖文件（如 `requirements_clean.txt`、`package.json`）后，需要强制重新构建镜像：
```bash
# 开发环境 - 强制重新构建镜像（解决依赖更新问题）
./deploy.sh dev --build

# 生产环境 - 强制重新构建镜像
./deploy.sh prod --build
```

### 其他管理命令
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

访问：
- 前端：`http://localhost` 或 `http://本机IP`
- 健康检查：`http://localhost/health` 或 `http://localhost:5000/api/health`

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

## 七、无域名部署
- `.env` 中 `SERVER_URL=http://本机IP`（或 `http://localhost`）
- 直接访问 `http://localhost`
- 当前 `nginx/nginx.conf` 已配置为仅 80 端口、无证书

## 八、注意事项
- Windows 与 WSL 路径差异：建议在 WSL 的项目目录内执行 Docker 命令，避免路径与权限问题。
- 文件换行符：从 Windows 编辑的脚本在 WSL 下运行前，执行 `dos2unix deploy.sh`。
- 端口占用：确保 80/5000 未被其他程序（如 IIS）占用。
- 权限：首次运行 Docker Desktop 需管理员权限；如提示共享驱动器权限，按提示授权。

## 九、排障速查
```powershell
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 进入容器（WSL/PowerShell 通用）
docker exec -it cert-autofill-backend bash

# 查看端口占用（PowerShell）
netstat -aon | findstr ":80"
netstat -aon | findstr ":5000"
```

## 十、常见问题与解决方案

### 依赖更新后容器启动失败

**问题现象**：
```
exec: "gunicorn": executable file not found in $PATH
```

**解决方案**：
```powershell
# 使用--build选项强制重新构建镜像
./deploy.sh dev --build
# 或
./deploy.sh prod --build

# 手动方式
docker-compose up --build -d
```

**原因**：修改依赖文件后，Docker使用了旧镜像缓存，新依赖没有被安装。

### 前端构建失败

**问题现象**：
```
sh: vite: not found
```

**解决方案**：
```powershell
# 强制重新构建前端镜像
./deploy.sh dev --build
# 或手动
docker-compose up --build -d frontend
```

**原因**：前端依赖未正确安装。

### WSL与Windows文件权限问题

**解决方案**：
```powershell
# 在WSL中重新设置文件权限
chmod +x deploy.sh

# 转换Windows换行符
dos2unix deploy.sh

# 检查文件所有权
ls -la deploy.sh
```

### Docker Desktop网络连接问题

**解决方案**：
```powershell
# 重启Docker Desktop
# 或在Docker Desktop设置中重新启用WSL集成

# 检查WSL集成状态
wsl -l -v
```

### 磁盘空间不足

**解决方案**：
```powershell
# 清理Docker资源
docker system prune -a

# 或使用脚本清理
./deploy.sh cleanup
```

## 十一、升级与回滚

### 常规升级
```powershell
# 拉取最新代码
git pull

# 使用一键脚本升级（推荐）
./deploy.sh dev --build  # 开发环境
./deploy.sh prod --build # 生产环境
```

### 手动升级
```powershell
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build
docker-compose up -d

# 生产环境
docker-compose --profile production up --build -d
```

### 依赖更新升级
当更新了依赖文件时，必须使用 `--build` 选项：
```powershell
# 方式1：使用脚本（推荐）
./deploy.sh dev --build

# 方式2：手动命令
docker-compose up --build -d
```

### 回滚策略
```powershell
# 停止当前服务
docker-compose down

# 回滚到指定版本
git checkout <commit-hash>
docker-compose up --build -d

# 或使用镜像标签
docker-compose pull
docker-compose up -d
```

备注：数据库与上传目录已挂载到命名卷（`backend_data`、`backend_db`），容器重建数据不丢失。

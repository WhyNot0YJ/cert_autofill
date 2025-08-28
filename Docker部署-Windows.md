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
Windows 下建议在 WSL Shell 执行脚本，以避免换行符与权限问题。
```bash
# 如从 Windows 拷贝过来，先转换换行符并赋权限
dos2unix deploy.sh 2>/dev/null || true
chmod +x deploy.sh

# 开发/内网（HTTP）
./deploy.sh dev

# 生产（仅 80 端口、无证书；如需 HTTPS 与域名，见 Linux 文档）
./deploy.sh prod
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

## 十、升级与回滚
```powershell
# 升级
git pull
docker-compose build
docker-compose up -d

# 回滚：按镜像 tag 切换或使用上一次可用镜像
```

备注：数据库与上传目录已挂载到命名卷（`backend_data`、`backend_db`），容器重建数据不丢失。

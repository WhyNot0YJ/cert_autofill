# 证书管理系统 Docker 部署指南（Linux）

## 一、前提条件
- **支持的系统**：Ubuntu 20.04+/Debian 11+/CentOS 7+/RHEL 8+
- **网络要求**：内网环境，确保服务器间网络互通
- **端口要求**：80（前端）、5001（后端API）
- **权限要求**：有 sudo 权限的用户
- **硬件要求**：至少 2GB RAM，10GB 可用磁盘空间

## 二、安装 Docker 与 Compose
### Ubuntu/Debian
```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # 重新登录生效

# 安装 Docker Compose（独立二进制）
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### CentOS/RHEL
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # 重新登录生效

# 安装 Docker Compose（独立二进制）
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 三、获取项目并配置环境

### 3.1 获取项目代码
```bash
# 获取代码
git clone <your-repo-url>
cd cert_autofill
```

### 3.2 配置环境变量
```bash
# 复制生产环境配置
cp env.production .env

# 编辑配置文件
nano .env
```

**重要配置项说明**：
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

### 3.3 内网部署特殊配置
对于内网环境，需要特别注意以下配置：

1. **SERVER_URL配置**：必须设置为内网可访问的IP地址
2. **防火墙设置**：确保80和5001端口开放
3. **网络连通性**：确保AI服务API可访问（如需要）

## 四、一键部署（推荐）

### 4.1 准备部署脚本
```bash
# 解决换行符并赋予执行权限（如从 Windows 拷贝）
dos2unix deploy.sh 2>/dev/null || true
chmod +x deploy.sh

# 验证脚本权限
ls -la deploy.sh
```

### 4.2 内网生产环境部署
```bash
# 内网生产环境部署（前端端口81，后端端口5001）
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
# 检查容器状态
docker-compose ps

# 检查服务日志
./deploy.sh logs

# 测试健康检查
curl http://您的内网IP:5001/api/health
```

## 五、手动部署（可选）
```bash
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
```bash
# 查看容器状态
docker-compose ps

# 查看日志（全部/指定服务）
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启/停止
./deploy.sh restart
./deploy.sh stop

# 备份（数据库与上传文件）
./deploy.sh backup
```

## 七、防火墙配置

### 7.1 Ubuntu/Debian 系统
```bash
# 开放必要端口
sudo ufw allow 80/tcp      # 前端访问
sudo ufw allow 5001/tcp    # 后端API
sudo ufw allow 22/tcp      # SSH（可选）

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 7.2 CentOS/RHEL 系统
```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --permanent --add-service=ssh  # 可选

# 重新加载配置
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

### 7.3 SELinux 配置（如需要）
```bash
# 检查SELinux状态
sestatus

# 如需要，可临时禁用SELinux（重启后恢复）
sudo setenforce 0

# 或永久禁用（不推荐）
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
```

## 八、内网部署配置要点

### 8.1 网络配置
- **SERVER_URL**：必须设置为内网可访问的IP地址
- **端口映射**：确保80和5001端口在防火墙中开放
- **网络连通性**：确保服务器间网络互通

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

## 九、排障速查

### 9.1 基础检查命令
```bash
# 检查端口占用
ss -tulpn | grep -E ":80|:5001"

# 检查容器状态
docker-compose ps

# 检查容器日志
docker-compose logs -f

# 进入后端容器
docker exec -it cert-autofill-backend bash

# 检查Docker网络
docker network ls
docker network inspect cert-autofill-network
```

### 9.2 服务状态检查
```bash
# 检查服务健康状态
curl -f http://localhost:5000/api/health

# 检查前端服务
curl -I http://localhost

# 检查系统资源
free -h
df -h
```

## 十、常见问题与解决方案

### 10.1 依赖更新后容器启动失败

**问题现象**：
```
exec: "gunicorn": executable file not found in $PATH
```

**解决方案**：
```bash
# 使用--build选项强制重新构建镜像
./deploy.sh prod --build

# 手动方式
docker-compose up --build -d
```

**原因**：修改依赖文件后，Docker使用了旧镜像缓存，新依赖没有被安装。

### 10.2 前端构建失败

**问题现象**：
```
sh: vite: not found
npm ERR! missing script: build
```

**解决方案**：
```bash
# 强制重新构建前端镜像
./deploy.sh prod --build

# 手动清理并重建
docker-compose down
docker system prune -f
docker-compose up --build -d
```

### 10.3 网络连接问题

**问题现象**：
- 前端无法访问后端API
- 容器间通信失败

**解决方案**：
```bash
# 检查网络连接
docker network ls
docker network inspect cert-autofill-network

# 重启网络
docker-compose down
docker-compose up -d

# 检查防火墙设置
sudo ufw status
```

### 10.4 端口占用问题

**问题现象**：
```
bind: address already in use
```

**解决方案**：
```bash
# 查找占用端口的进程
sudo lsof -i :80
sudo lsof -i :5001

# 停止占用进程或修改端口配置
sudo kill -9 <PID>
```

### 10.5 磁盘空间不足

**解决方案**：
```bash
# 清理Docker资源
docker system prune -a

# 清理未使用的镜像和容器
docker image prune -a
docker container prune

# 使用脚本清理
./deploy.sh cleanup
```

### 10.6 权限问题

**问题现象**：
```
Permission denied
```

**解决方案**：
```bash
# 检查文件权限
ls -la deploy.sh

# 修复权限
chmod +x deploy.sh
sudo chown -R $USER:$USER .
```

## 十一、升级与回滚

### 常规升级
```bash
# 拉取最新代码
git pull

# 使用一键脚本升级（推荐）
./deploy.sh dev --build  # 开发环境
./deploy.sh prod --build # 生产环境
```

### 手动升级
```bash
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
```bash
# 方式1：使用脚本（推荐）
./deploy.sh dev --build

# 方式2：手动命令
docker-compose up --build -d
```

### 回滚策略
```bash
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

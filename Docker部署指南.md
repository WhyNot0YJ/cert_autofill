# 🐳 证书管理系统 Docker 部署指南

## 📋 目录

- [项目概述](#项目概述)
- [系统架构](#系统架构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [生产环境配置](#生产环境配置)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)
- [常见问题](#常见问题)

## 🎯 项目概述

证书管理系统是一个基于 **Vue 3 + Flask** 的现代化Web应用，集成了AI智能文档提取功能。系统采用前后端分离架构，支持容器化部署，提供高可用性和可扩展性。

### 主要功能
- 🚀 AI智能文档提取和处理
- 📋 申请书管理和状态跟踪
- 🏢 企业信息管理
- 📄 多种证书模板支持
- 🔐 用户认证和权限管理

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Host (宿主机)                      │
├─────────────────────────────────────────────────────────────┤
│                    Docker Engine                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  前端容器   │  │  后端容器   │  │  Nginx容器  │        │
│  │ (Vue + Nginx)│  │ (Flask + Gunicorn)│ (反向代理)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Linux Kernel                             │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈
- **前端**: Vue 3 + TypeScript + Element Plus + Vite
- **后端**: Flask + SQLAlchemy + SQLite + Gunicorn
- **Web服务器**: Nginx
- **容器化**: Docker + Docker Compose
- **AI服务**: Dify AI平台集成

## 🔧 环境要求

### 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+
- **内存**: 最少4GB，推荐8GB+
- **存储**: 最少20GB可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 用于代码管理

## 🚀 快速开始

### 1. 安装Docker

#### Ubuntu/Debian
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# 安装必要软件
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

#### Windows
1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 启动Docker Desktop
3. 确保WSL2已启用

### 2. 安装Docker Compose

```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 设置执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 3. 克隆项目

```bash
# 克隆项目代码
git clone <your-repository-url>
cd cert_autofill

# 查看项目结构
ls -la
```

## 📝 详细部署步骤

### 第一步：环境配置

```bash
# 1. 复制环境变量文件
cp env.example .env

# 2. 编辑环境变量文件
nano .env
```

#### 环境变量配置说明
```bash
# 生产环境配置
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here-change-this
DATABASE_URL=sqlite:///cert_autofill.db
SERVER_URL=https://your-domain.com
DIFY_API_KEY=app-aOHstplRYJhO3uadmVwKnf8E
DIFY_API_BASE=https://api.dify.ai/v1

# 数据库配置（如果使用外部数据库）
# DATABASE_URL=postgresql://user:password@localhost:5432/cert_autofill
# DATABASE_URL=mysql://user:password@localhost:3306/cert_autofill

# Redis配置（可选）
# REDIS_URL=redis://redis:6379/0

# 日志级别
LOG_LEVEL=INFO

# 文件上传配置
MAX_FILE_SIZE=16777216  # 16MB in bytes
UPLOAD_FOLDER=/app/uploads
```

### 第二步：部署应用

#### 使用部署脚本（推荐）
```bash
# 1. 设置脚本执行权限
chmod +x deploy.sh

# 2. 部署开发环境
./deploy.sh dev

# 3. 或部署生产环境
./deploy.sh prod
```

#### 手动部署
```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps
```

### 第三步：验证部署

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看服务日志
docker-compose logs

# 3. 测试服务访问
curl http://localhost
curl http://localhost:5000/api/health
```

## 🌐 生产环境配置

### 1. SSL证书配置

```bash
# 创建SSL证书目录
mkdir -p nginx/ssl

# 将SSL证书复制到目录
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# 设置正确的权限
chmod 600 nginx/ssl/*
```

### 2. 域名配置

编辑 `nginx/nginx.conf` 文件，将 `your-domain.com` 替换为您的实际域名：

```nginx
server_name your-domain.com www.your-domain.com;
```

### 3. 生产环境部署

```bash
# 使用生产环境配置部署
./deploy.sh prod

# 或手动部署
docker-compose --profile production up -d
```

### 4. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📊 监控和维护

### 1. 服务管理

```bash
# 查看服务状态
./deploy.sh status

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop

# 查看日志
./deploy.sh logs
./deploy.sh logs backend
./deploy.sh logs frontend
```

### 2. 数据备份

```bash
# 备份数据
./deploy.sh backup

# 查看备份文件
ls -la backups/
```

### 3. 资源清理

```bash
# 清理未使用的Docker资源
./deploy.sh cleanup

# 手动清理
docker system prune -f
docker volume prune -f
```

### 4. 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看系统资源
htop
df -h
free -h
```

## 🔍 故障排除

### 1. 常见问题诊断

#### 服务无法启动
```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
netstat -tulpn | grep :5000
netstat -tulpn | grep :80

# 检查Docker服务状态
sudo systemctl status docker
```

#### 权限问题
```bash
# 修复文件权限
sudo chown -R $USER:$USER .
chmod +x deploy.sh

# 修复Docker权限
sudo chmod 666 /var/run/docker.sock
```

#### 网络问题
```bash
# 检查网络配置
docker network ls
docker network inspect cert_autofill_cert-autofill-network

# 重启网络
docker-compose down
docker-compose up -d
```

### 2. 日志分析

```bash
# 实时查看日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看Nginx日志
docker exec cert-autofill-nginx tail -f /var/log/nginx/access.log
docker exec cert-autofill-nginx tail -f /var/log/nginx/error.log
```

### 3. 容器调试

```bash
# 进入容器内部
docker exec -it cert-autofill-backend bash
docker exec -it cert-autofill-frontend sh

# 检查容器内部文件
docker exec cert-autofill-backend ls -la /app
docker exec cert-autofill-frontend ls -la /usr/share/nginx/html
```

## ❓ 常见问题

### Q1: 容器启动失败怎么办？
**A**: 检查以下几点：
1. 确认Docker服务正在运行
2. 检查端口是否被占用
3. 查看容器日志：`docker-compose logs`
4. 检查环境变量配置是否正确

### Q2: 如何更新应用？
**A**: 使用以下步骤：
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d
```

### Q3: 如何备份数据库？
**A**: 使用备份脚本：
```bash
./deploy.sh backup
```
备份文件将保存在 `backups/` 目录中。

### Q4: 如何查看应用性能？
**A**: 使用以下命令：
```bash
# 查看容器资源使用
docker stats

# 查看系统资源
htop
df -h
free -h

# 查看Nginx访问日志
docker exec cert-autofill-nginx tail -f /var/log/nginx/access.log
```

### Q5: 如何配置HTTPS？
**A**: 按以下步骤操作：
1. 获取SSL证书
2. 将证书文件复制到 `nginx/ssl/` 目录
3. 编辑 `nginx/nginx.conf` 中的域名
4. 重启Nginx服务：`docker-compose restart nginx`

## 📚 进阶配置

### 1. 负载均衡

```bash
# 扩展后端服务
docker-compose up -d --scale backend=3

# 配置Nginx负载均衡
# 编辑 nginx/nginx.conf 文件
```

### 2. 数据库优化

```bash
# 使用PostgreSQL替代SQLite
# 修改 .env 文件中的 DATABASE_URL
DATABASE_URL=postgresql://user:password@postgres:5432/cert_autofill

# 添加PostgreSQL服务到 docker-compose.yml
```

### 3. 缓存配置

```bash
# 启用Redis缓存
# 在 docker-compose.yml 中启用Redis服务
docker-compose --profile production up -d
```

### 4. 监控集成

```bash
# 集成Prometheus监控
# 添加监控服务到 docker-compose.yml
```

## 🔐 安全建议

### 1. 环境变量安全
- 使用强密码和密钥
- 定期更换密钥
- 不要在代码中硬编码敏感信息

### 2. 网络安全
- 启用防火墙
- 只开放必要端口
- 使用HTTPS加密传输

### 3. 容器安全
- 定期更新基础镜像
- 使用非root用户运行容器
- 限制容器权限

### 4. 数据安全
- 定期备份数据
- 加密敏感数据
- 监控异常访问

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查Docker和容器日志
3. 确认系统环境满足要求
4. 联系技术支持团队

## 📝 更新日志

### v1.0.0 (2024-12-19)
- ✨ 新增Docker容器化支持
- 🔧 集成Docker Compose管理
- 📱 支持开发和生产环境
- 🎨 优化部署脚本和配置
- 🔒 增强安全配置

---

**注意**: 本文档适用于证书管理系统v1.0.0及以上版本。请确保您的系统环境满足最低要求，并按照步骤正确执行部署操作。

# 证书管理系统 Docker 部署指南（Linux）

## 一、前提条件
- 支持的系统：Ubuntu 20.04+/Debian/CentOS 7+/RHEL 8+
- 已开放端口：80（前端）、5000（后端直连调试时，可选）
- 推荐：有 sudo 权限的用户

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
```bash
# 获取代码
git clone <your-repo-url>
cd cert_autofill

# 准备环境变量
cp env.example .env
nano .env
# 至少设置：SECRET_KEY、DIFY_API_KEY、SERVER_URL（无域名用 http://服务器IP）
```

## 四、一键部署（推荐）
项目已提供脚本 `deploy.sh`
```bash
# 解决换行符并赋予执行权限（如从 Windows 拷贝）
dos2unix deploy.sh 2>/dev/null || true
chmod +x deploy.sh

# 开发/内网（HTTP）：
./deploy.sh dev

# 生产（含反向代理，当前配置已为仅 80 端口，无证书）：
./deploy.sh prod
```

访问：
- 前端：`http://服务器IP`
- 健康检查：`http://服务器IP/health` 或 `http://服务器IP:5000/api/health`

## 五、手动部署（可选）
```bash
# 构建镜像
docker-compose build

# 启动（默认前后端）
docker-compose up -d

# 启动（生产 profile，含外部 nginx 容器）
docker-compose --profile production up -d
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

## 七、防火墙/SELinux 提示
- Ubuntu/Debian：
```bash
sudo ufw allow 80/tcp
sudo ufw allow 5000/tcp   # 仅调试直连后端时
sudo ufw enable
```
- CentOS/RHEL：
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=5000/tcp   # 仅调试直连后端时
sudo firewall-cmd --reload
```
- SELinux 开启时，Nginx 反代/卷挂载可能需额外策略（生产建议保持默认容器网络与卷权限）。

## 八、无域名部署
- `.env` 中 `SERVER_URL=http://服务器IP`
- 直接访问 `http://服务器IP`
- 已将 `nginx/nginx.conf` 配置为仅 80 端口、无证书

## 九、排障速查
```bash
# 端口占用
ss -tulpn | grep -E ":80|:5000"

# 容器日志
docker-compose logs -f

# 进入容器
docker exec -it cert-autofill-backend bash

# 检查网络
docker network ls
```

## 十、升级与回滚
```bash
# 升级
git pull
docker-compose build
docker-compose up -d

# 回滚（按镜像 tag 或上一次可用镜像）
# 例如：docker run your-image:previous
```

备注：数据库与上传目录已挂载到命名卷（`backend_data`、`backend_db`），容器重建数据不丢失。

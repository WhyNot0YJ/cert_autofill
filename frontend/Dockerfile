# 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖，用于构建）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段 - 使用简单的静态文件服务器
FROM node:18-alpine

# 安装serve作为静态文件服务器
RUN npm install -g serve

# 设置工作目录
WORKDIR /app

# 复制构建结果
COPY --from=builder /app/dist ./dist

# 暴露端口
EXPOSE 80

# 启动静态文件服务器
CMD ["serve", "-s", "dist", "-l", "80"]

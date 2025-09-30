# 使用Python 3.9官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app.main:create_app

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libtiff5-dev \
        libopenjp2-7-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 LibreOffice（headless）与常用字体（含中文），以及 JRE（部分转换路径需要）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer \
        default-jre-headless \
        fonts-noto-cjk \
        fonts-noto \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements_clean.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements_clean.txt

# 复制应用代码
COPY . .

# 创建uploads目录
RUN mkdir -p uploads/generated_files \
    && chmod 755 uploads uploads/generated_files

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令 - 使用Gunicorn作为生产服务器
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "app.main:app"]

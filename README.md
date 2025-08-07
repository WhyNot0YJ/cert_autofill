# 认证文档自动填充系统

## 项目简介

这是一个用于自动生成认证文档的系统，支持玻璃制品认证申请文档的自动填充和生成。

## 技术栈

### 后端
- Python 3.8+
- Flask
- SQLAlchemy
- python-docx
- docxtpl
- docxcompose (多模板合并)

### 前端
- Vue 3
- TypeScript
- Element Plus
- Vite

## 项目结构

```
cert_autofill/
├── backend/                 # 后端代码
│   ├── app/                # 应用代码
│   │   ├── api/           # API接口
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   └── utils/         # 工具函数
│   ├── templates/         # Word模板文件
│   ├── client/           # 客户端资源
│   ├── generated_files/   # 生成的文档
│   ├── uploads/          # 上传文件
│   └── requirements.txt   # Python依赖
├── frontend/              # 前端代码
│   ├── src/              # 源代码
│   │   ├── api/          # API调用
│   │   ├── components/   # Vue组件
│   │   ├── views/        # 页面视图
│   │   └── router/       # 路由配置
│   ├── package.json      # Node.js依赖
│   └── vite.config.ts    # Vite配置
└── README.md             # 项目说明
```

## 安装和运行

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate   # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行后端服务：
```bash
python run.py
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 运行开发服务器：
```bash
npm run dev
```

## 功能特性

- ✅ 文档模板管理
- ✅ 表单数据收集
- ✅ 自动文档生成
- ✅ 多车辆信息支持
- ✅ 文档预览和下载
- ✅ 申请记录管理

## 开发说明

### 文档生成逻辑

系统使用多模板合并渲染方案，完美保留Word格式：

- **基础模板**: `backend/templates/IF_Template_Base.docx` (固定部分)
- **车辆模板**: `backend/templates/IF_Template_Vehicle.docx` (循环部分)
- **生成逻辑**: `backend/app/services/generate.py` - `generate_if_template_document()`
- **技术方案**: 使用 `docxcompose` 进行多模板合并，完整保留格式
- **变量规范**: 使用标准化的变量名（如 `veh_mfr`, `veh_type`, `dev_area` 等）
- **优势**: 完美保留页眉页脚、分页符、样式继承等复杂格式

### 数据库

- 使用SQLite作为开发数据库
- 支持企业信息、申请记录、文档模板等管理

## 部署

### 生产环境

1. 配置环境变量
2. 使用生产级数据库（如PostgreSQL）
3. 配置Web服务器（如Nginx）
4. 使用进程管理器（如PM2）

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

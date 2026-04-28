# 智能证书生成系统

## 项目概述

这是一个基于Vue 3 + Flask的证书管理系统，集成了基于**正则表达式规则引擎**的文档提取功能，能够自动从申请书文档中提取关键信息并填充到表单中。

## 主要功能

### 🚀 规则引擎文档提取
- **支持格式**: 支持上传 .doc, .docx, .pdf 格式的申请书文档
- **规则提取**: 使用正则表达式规则引擎自动提取文档中的关键信息
- **自动填充**: 提取的信息自动填充到对应的表单字段
- **数据映射**: 支持企业信息、技术参数、车辆信息等结构化数据提取

### 📋 申请书管理
- 申请书创建、编辑、删除
- 表单数据自动保存和恢复
- 搜索和筛选功能
- 分页显示
- 批量文档生成

### 🏢 公司管理
- 企业信息管理
- 商标和图案管理
- 设备信息管理
- 文件上传和管理
- 公司信息快速填充

### 📄 文档生成
- 支持多种文档类型生成（IF、CERT、RCS、TR、TM、OTHER）
- 支持DOCX和PDF格式输出
- 批量文档生成和ZIP打包下载
- 模板化文档生成
- 实时预览和下载



## 技术架构

### 前端 (Frontend)
- **框架**: Vue 3 + TypeScript
- **UI组件**: Element Plus
- **路由**: Vue Router 4
- **构建工具**: Vite

### 后端 (Backend)
- **框架**: Flask (Python)
- **数据库**: SQLAlchemy + SQLite
- **提取服务**: 自研规则引擎（基于 Python 正则表达式）
- **文件处理**: 支持多种文档格式
- **文档生成**: python-docx + Microsoft Word (COM)
- **文件上传**: 统一文件上传服务
- **工具类**: JSON字段处理、文件管理等

### 提取服务说明
- **实现方式**: 自研规则引擎（Python + 正则表达式）
- **部署位置**: `backend/app/services/document_extract/`

## 安装和运行

### 环境要求
- Windows 10/11（后端强依赖 Windows Word COM 组件生成文档）
- Node.js 16+
- Python 3.8+
- pip
- Microsoft Word（用于 DOCX → PDF 转换）

### 🚀 一键启动（推荐）
在项目根目录双击 `start.bat` 即可自动安装依赖并启动前后端服务：
```bat
start.bat
```
停止服务请运行：
```bat
stop.bat
```

### 手动启动

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

#### 后端启动
```bash
cd backend
pip install -r requirements.txt
python run.py
```

## 提取功能使用说明

### 1. 访问提取页面
- 在导航栏中点击“文档处理”按钮
- 或直接访问 `/` 首页

### 2. 上传文档
- 支持拖拽上传或点击选择文件
- 目前仅支持申请书文档上传（.doc, .docx, .pdf）
- 测试报告功能暂未开放

### 3. 提取过程
- 点击“提取信息”按钮
- 系统后台的**规则引擎**会读取文档文本（剔除隐藏/删除线内容）并按预定义的正则规则进行匹配
- 提取完成后显示结果预览

### 4. 结果应用
- 查看提取的信息是否正确
- 点击“应用到表单”自动填充到申请书表单
- 可以手动编辑和调整提取的数据

### 5. 保存申请书
- 完善必填信息
- 点击"保存申请书"完成创建

## 支持的数据字段

### 企业信息
- 企业名称
- 企业英文名
- 企业地址

### 认证信息
- 认证类型
- 产品名称

### 技术参数
- 风窗厚度 (Windscreen Thickness)
- 夹层厚度 (Interlayer Thickness)
- 玻璃层数 (Glass Layers)
- 夹层数 (Interlayer Layers)
- 夹层类型 (Interlayer Type)
- 玻璃处理 (Glass Treatment)
- 涂层类型 (Coating Type)
- 涂层厚度 (Coating Thickness)
- 涂层颜色 (Coating Color)
- 材料性质 (Material Nature)
- 玻璃颜色选择 (Glass Color Choice)
- 导体选择 (Conductors Choice)
- 不透明/模糊选择 (Opaque/Obscure Choice)
- 夹层着色信息 (Interlayer Coloring)

### 车辆信息
- 车辆制造商 (Vehicle Manufacturer)
- 车辆类型 (Vehicle Type)
- 车辆类别 (Vehicle Category)
- 开发区域 (Development Area)
- 段高度 (Segment Height)
- 曲率半径 (Curvature Radius)
- 安装角度 (Installation Angle)
- 座椅角度 (Seat Angle)
- 参考点坐标 (Reference Point Coordinates)
- 开发描述 (Development Description)

### 商标信息
- 商标名称列表 (Trade Names)
- 商标图片管理 (Trade Marks)
- 设备信息管理 (Equipment Information)

### 系统参数
- 版本号管理 (Version Numbers)
- 实验室环境参数 (Laboratory Parameters)
- 法规更新日期 (Regulation Update Date)

## 配置说明

### 环境变量
本系统的文档提取功能基于本地规则引擎实现，环境变量重点关注：`SECRET_KEY`、`DATABASE_URL`、`SERVER_URL`、`BACKEND_PORT_DEV/PROD`、`FRONTEND_PORT_DEV/PROD`等。

### API端点

#### 主要业务API (`/api/mvp`)
- `POST /api/mvp/document-extract`: 文档信息提取
- `POST /api/mvp/upload-file`: 文件上传
- `POST /api/mvp/save-form-data`: 保存表单数据
- `GET /api/mvp/get-form-data/<session_id>`: 获取表单数据
- `POST /api/mvp/generate-documents`: 生成所有文档
- `POST /api/mvp/generate-if`: 生成IF文档
- `POST /api/mvp/generate-cert`: 生成证书文档
- `POST /api/mvp/generate-other`: 生成其他文档
- `POST /api/mvp/generate-tr`: 生成技术报告
- `POST /api/mvp/generate-tm`: 生成技术备忘录
- `POST /api/mvp/generate-review-control-sheet`: 生成审查控制表
- `GET /api/mvp/download/<filename>`: 下载生成文档

#### 公司管理API (`/api`)
- `GET /api/companies`: 获取公司列表
- `POST /api/companies`: 创建公司
- `GET /api/companies/<id>`: 获取公司详情
- `PUT /api/companies/<id>`: 更新公司信息
- `DELETE /api/companies/<id>`: 删除公司

#### 申请书管理API (`/api`)
- `GET /api/applications`: 获取申请书列表
- `GET /api/applications/<id>`: 获取申请书详情
- `DELETE /api/applications/<id>`: 删除申请书

#### 系统API
- `GET /api/health`: 健康检查

## 开发说明

### 项目结构
```
cert_autofill/
├── backend/                 # 后端Flask应用
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── mvp_routes.py      # 主要业务API
│   │   │   ├── company_routes.py  # 公司管理API
│   │   │   └── application_routes.py # 申请书管理API
│   │   ├── models/         # 数据模型
│   │   │   ├── form_data.py       # 表单数据模型
│   │   │   ├── company.py         # 公司信息模型
│   │   │   └── base.py            # 基础模型类
│   │   ├── services/       # 业务逻辑服务
│   │   │   ├── document_extract/    # 规则引擎提取服务（正则匹配）
│   │   │   ├── file_upload_service.py # 文件上传服务│   │   │   ├── system_config.py      # 系统配置服务
│   │   │   └── generators/           # 文档生成器
│   │   │       ├── base_generator.py # 基础生成器
│   │   │       ├── if_generator.py   # IF文档生成器
│   │   │       ├── cert_generator.py # 证书生成器
│   │   │       ├── rcs_generator.py  # 审查控制表生成器
│   │   │       ├── tr_generator.py   # 技术报告生成器
│   │   │       ├── tm_generator.py   # 技术备忘录生成器
│   │   │       └── other_generator.py # 其他文档生成器
│   │   ├── utils/          # 工具类
│   │   │   └── json_handler.py      # JSON字段处理工具
│   │   ├── templates/      # 文档模板
│   │   ├── config.py       # 配置文件
│   │   └── main.py         # 应用主文件
│   ├── uploads/            # 文件上传目录
│   ├── instance/           # 数据库文件
│   ├── requirements.txt    # Python依赖
│   └── run.py              # 启动文件
├── frontend/                # 前端Vue应用
│   ├── src/
│   │   ├── components/     # 组件
│   │   │   ├── UploadForm.vue        # 文件上传组件
│   │   │   ├── DocumentGenerator.vue # 文档生成组件
│   │   │   ├── ApplicationEditor.vue # 申请书编辑组件
│   │   │   ├── CompanyManagement.vue # 公司管理组件
│   │   │   └── Navigation.vue        # 导航组件
│   │   ├── views/          # 页面
│   │   │   ├── MVP.vue              # 主要功能页面
│   │   │   ├── ApplicationManager.vue # 申请书管理页面
│   │   │   └── CompanyManagement.vue  # 公司管理页面
│   │   ├── api/            # API接口
│   │   │   ├── mvp.ts              # 主要业务API
│   │   │   ├── company.ts          # 公司管理API
│   │   │   └── application.ts      # 申请书管理API
│   │   ├── router/         # 路由配置
│   │   ├── types/          # TypeScript类型定义
│   │   └── main.ts         # 应用入口
│   ├── dist/               # 构建输出
│   ├── package.json        # 项目配置
│   └── vite.config.ts      # Vite配置
├── nginx/                  # Nginx 反向代理配置（预留，未来原生部署可用）
├── start.bat               # Windows 一键启动脚本
├── stop.bat                # Windows 一键停止脚本
└── README.md               # 项目说明
```

### 扩展开发
- 添加新的文档类型支持
- 扩展提取字段
- 集成其他提取服务
- 优化提取准确率

## 注意事项

1. **文件格式**: 支持申请书文档（.doc, .docx, .pdf），测试报告功能开发中
2. **文件大小**: 建议单个文件不超过16MB
3. **网络要求**: 无特殊要求
4. **文档格式规范**: 规则引擎依赖原始文档的格式规范性，建议提供原生 `.docx`，避免扫描版 PDF（文字无法提取）
5. **文档生成**: 需安装 Microsoft Word 以支持 DOCX → PDF 转换
6. **浏览器兼容**: 建议使用Chrome、Firefox、Safari等现代浏览器
7. **数据备份**: 建议定期备份数据库文件（instance/cert_autofill.db）

## 故障排除

### 常见问题
1. **提取结果不准或字段缺失**: 规则引擎基于正则表达式匹配，请确认申请书格式规范（避免扫描版/合并单元格/图片化文字）；若格式差异较大，请研发扩充 `backend/app/services/document_extract/rule_engine_strategy.py` 中的规则
2. **文件上传失败**: 确认文件格式和大小，检查上传目录权限
3. **表单验证错误**: 检查必填字段是否完整
4. **文档生成失败**: 确认 Microsoft Word 已正确安装，检查模板文件是否存在
5. **PDF生成失败**: 检查 Word COM 是否可用（`python -c "import win32com.client"`），清理残留的 WINWORD.EXE 进程
6. **数据库错误**: 检查数据库文件权限，必要时重新创建数据库
7. **页面加载缓慢**: 检查网络连接，清除浏览器缓存

### 日志查看
- 后端日志: `backend/logs/`
- 前端控制台: 浏览器开发者工具

## 更新日志

### v1.2.0 (2024-12-22)
- ✨ 新增多种文档类型生成支持（IF、CERT、RCS、TR、TM、OTHER）
- 🔧 优化文档生成器架构，支持批量生成
- 📄 新增PDF格式输出支持
- 🏢 完善公司管理功能，支持设备信息管理
- 🛠️ 优化代码结构，提升维护性
- 🎨 改进用户界面和交互体验

### v1.1.0 (2024-12-20)
- ✨ 新增公司管理功能
- 🔧 优化文件上传服务
- 📱 完善移动端响应式设计
- 🎨 改进表单验证和错误处理

### v1.0.0 (2024-12-19)
- ✨ 新增基于规则引擎的文档提取功能
- 🔧 集成 Python + 正则表达式本地提取方案
- 📱 优化移动端响应式设计
- 🎨 改进用户界面和交互体验

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请联系开发团队。

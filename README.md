# 面向流媒体/自媒体营销的"内容创作AI-Agent"

一款轻量化、易上手的流媒体/自媒体营销内容辅助工具，帮助自媒体从业者提高创作效率，降低创作门槛。

## 项目简介

本项目旨在开发一款轻量化的AI辅助内容创作工具，聚焦"营销素材智能生成、内容格式快速适配、创作记录留存与基础数据统计"核心需求。

### 核心功能

- **用户认证**：用户注册、登录、JWT认证
- **素材库管理**：素材CRUD、分类管理、标签管理、素材检索
- **AI内容生成**：选题推荐、文案生成、质量评估、人工编辑
- **平台适配**：抖音、小红书、微信视频号格式适配，一键排版
- **创作记录**：创作历史、版本管理、检索功能、导出功能
- **统计分析**：每日统计、关键词分析、数据可视化

### 技术栈

**前端**：
- Vue.js 3
- Element Plus
- Pinia（状态管理）
- Vue Router（路由）
- Axios（HTTP客户端）
- ECharts（数据可视化）

**后端**：
- Python FastAPI
- SQLAlchemy（ORM）
- Alembic（数据库迁移）
- JWT认证
- OpenAI API / 通义千问 / 文心一言

**数据库**：
- MySQL 8.0
- Redis 6.0

**部署**：
- Docker
- Nginx

## 项目结构

```
内容创作AI-Agent/
├── frontend/                 # 前端项目（Vue.js 3）
│   ├── src/
│   │   ├── api/            # API请求封装
│   │   ├── assets/         # 资源文件
│   │   ├── components/     # 公共组件
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── backend/                 # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic模型
│   │   ├── services/      # 业务逻辑
│   │   ├── utils/         # 工具函数
│   │   └── main.py        # 应用入口
│   ├── tests/             # 测试文件
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
├── 文档集合/                # 项目文档
├── 启动项目.bat             # 项目启动脚本
├── 启动测试.bat             # 测试启动脚本
├── docker-compose.yml       # Docker编排
└── README.md
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- MySQL 8.0+
- Redis 6.0+
- Docker（可选）

### 一键启动项目（推荐）

Windows系统下，可以使用提供的批处理脚本快速启动项目：

```bash
# 双击运行或在命令行执行
启动项目.bat
```

该脚本会自动：
1. 启动后端服务（http://localhost:8000）
2. 启动前端服务（http://localhost:3000）

**默认账号**：
- 用户名：admin
- 密码：admin123

### 手动启动项目

#### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.development
# 编辑.env.development文件，填写配置信息

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:3000 启动

#### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填写配置信息

# 初始化数据库
alembic upgrade head

# 启动后端服务
python run.py
```

后端服务将在 http://localhost:8000 启动

API文档访问地址：http://localhost:8000/docs

### 启动测试

#### 一键启动测试（推荐）

Windows系统下，可以使用提供的批处理脚本启动测试可视化工具：

```bash
# 双击运行或在命令行执行
启动测试.bat
```

该脚本会自动：
1. 检查Python环境
2. 检查并创建虚拟环境
3. 安装测试依赖（pytest、pytest-json-report）
4. 启动后端服务（如果未运行）
5. 打开测试可视化网页
6. 建议先启动start_backend.bat文件在启动以上bat文件
**测试可视化网页**：项目根目录下的 `test-dashboard.html`

#### 手动运行测试

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装测试依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 运行特定测试函数
pytest tests/test_auth.py::test_register

# 生成测试报告
pytest --json-report --json-report-file=test_report.json
```

**测试覆盖范围**：
- 用户认证测试（`test_auth.py`）
- 素材管理测试（`test_materials.py`）
- 创作记录测试（`test_records.py`）
- 平台适配测试（`test_adapter.py`）
- 统计分析测试（`test_statistics.py`）
- 仪表盘测试（`test_dashboard.py`）
- 安全性测试（`test_security.py`）
- 性能测试（`test_performance.py`）

### Docker启动

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 开发指南

### 前端开发

前端项目使用Vue.js 3 + Vite + Element Plus构建。

#### 目录结构

- `src/api/`：API请求封装
- `src/components/`：公共组件
- `src/layouts/`：布局组件
- `src/router/`：路由配置
- `src/stores/`：Pinia状态管理
- `src/views/`：页面组件
- `src/utils/`：工具函数

#### 代码规范

- 遵循ESLint规则
- 遵循Prettier格式化
- 组件命名：PascalCase
- 文件命名：kebab-case
- 变量命名：camelCase

### 后端开发

后端项目使用Python FastAPI + SQLAlchemy构建。

#### 目录结构

- `app/api/`：API路由
- `app/core/`：核心配置
- `app/models/`：数据模型
- `app/schemas/`：Pydantic模型
- `app/services/`：业务逻辑
- `app/utils/`：工具函数
- `tests/`：测试文件

#### 代码规范

- 遵循PEP 8规范
- 函数命名：snake_case
- 类命名：PascalCase
- 常量命名：UPPER_CASE
- 添加类型注解

## API文档

后端API文档使用Swagger/OpenAPI自动生成，启动后端服务后访问：

http://localhost:8000/docs

## 数据库设计

### 主要数据表

- `users`：用户表
- `categories`：分类表
- `materials`：素材表
- `tags`：标签表
- `material_tags`：素材标签关联表
- `records`：创作记录表
- `versions`：版本表
- `statistics`：统计表

详细的数据库设计请参考 [`文档集合/详细设计文档.md`](文档集合/详细设计文档.md)

## 项目文档

- [`文档集合/概要设计文档.md`](文档集合/概要设计文档.md)：项目概要设计
- [`文档集合/详细设计文档.md`](文档集合/详细设计文档.md)：项目详细设计
- [`文档集合/项目定位与功能设计.md`](文档集合/项目定位与功能设计.md)：项目定位与功能设计
- [`文档集合/详细分工文档.md`](文档集合/详细分工文档.md)：团队详细分工
- [`文档集合/接口设计文档.md`](文档集合/接口设计文档.md)：API接口设计
- [`文档集合/开发流程文档.md`](文档集合/开发流程文档.md)：开发流程说明
- [`文档集合/测试报告.md`](文档集合/05-测试与运维/测试报告.md)：测试报告

## 团队分工

本项目由4人团队开发，采用角色分工模式：

1. **队长**：项目统筹、后端架构、AI核心功能
2. **前端开发**：Vue3页面、SSE交互、UI/UX
3. **后端开发**：数据模型、业务API、数据库
4. **测试运维**：质量保障、CI/CD、部署文档

详细的团队分工请参考 [`文档集合/04-研发管理/项目现状审计与任务分配.md`](文档集合/04-研发管理/项目现状审计与任务分配.md)

## 开发计划

本项目开发周期为14周（按课程大纲），采用Scrum敏捷迭代：

- **第1-3周**：团队组建、需求分析、系统设计
- **第4-6周**：用户认证、素材库管理、数据库设计
- **第6-8周**：AI内容生成（RAG + SSE + Few-Shot）
- **第8-10周**：平台适配、创作记录、版本管理
- **第10-12周**：统计分析、前后端联调、系统测试
- **第12-14周**：项目答辩与总结

详细的开发计划请参考 [`文档集合/01-项目背景与需求/项目定位与功能设计.md`](文档集合/01-项目背景与需求/项目定位与功能设计.md)

## 贡献指南

1. 切到 develop 拉取最新代码 (`git checkout develop && git pull`)
2. 切回个人分支并同步 (`git checkout dev/你的名字 && git merge develop`)
3. 开发并提交 (`git commit -m 'feat: 你的改动描述'`)
4. 推送到远端 (`git push`)
5. 在 GitHub 上创建 Pull Request 到 `develop` 分支，等待队长审查

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

**注意**：本项目为教学实训项目，仅供学习交流使用。

# 启航引路人 - AI留学规划师平台

连接留学申请者（学弟学妹）与目标学校学长学姐的专业指导服务平台。基于FastAPI + LangGraph + Supabase构建，集成AI智能对话、实时消息、文件管理、精准匹配等全方位留学申请指导功能。

**🤖 AI智能对话 | 💬 实时消息 | 📁 文件管理 | 🎯 精准匹配 | 🏛️ 指导服务 | 🚀 高性能架构**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-orange.svg)](https://supabase.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.51-red.svg)](https://github.com/langchain-ai/langgraph)

## 🌟 平台特色

### 🎓 留学双边信息平台

连接想要申请留学的学弟学妹与目标学校院系的学长学姐，为留学申请提供个性化指导服务，包括文书指导、推荐信建议、面试辅导等专业服务。

| 功能模块     | 学弟学妹端                     | 学长学姐端               | 平台管理           |
| ------------ | ------------------------------ | ------------------------ | ------------------ |
| **用户管理** | 申请者资料、申请目标设置       | 指导者资料、学校院系认证 | 用户审核、身份验证 |
| **匹配系统** | 按学校/专业/申请方向筛选指导者 | 设置指导领域和时间安排   | 智能推荐算法       |
| **服务交易** | 浏览和购买指导服务             | 发布指导服务、设置价格   | 交易保障、纠纷处理 |
| **沟通协作** | 实时消息、文档共享             | 指导反馈、进度跟踪       | 对话监控、质量保证 |
| **评价体系** | 对指导者评价                   | 获得信誉积累             | 信誉算法、排名系统 |

### 🤖 AI留学规划师

- **智能对话**: 基于LangGraph的多轮对话AI系统
- **知识库学习**: 支持PDF文档上传，AI自动学习专业知识
- **实时搜索**: 集成Tavily网络搜索获取最新留学信息
- **工具融合**: 数据库查询 + 网络搜索 + 知识库检索 + 留学规划工具

### 💬 实时消息系统

- **一对一指导**: 学长学姐与学弟学妹的专属沟通渠道
- **对话管理**: 对话列表、未读消息提醒、消息搜索
- **消息状态**: 已发送、已送达、已读状态跟踪
- **文件共享**: 支持在对话中分享留学资料和文档

### 📁 文件管理系统

- **头像管理**: 用户头像上传和更新
- **文档上传**: PDF、Word、TXT等留学申请资料上传
- **安全验证**: 文件类型、大小、内容安全检查
- **云存储**: 集成MinIO对象存储，支持高性能分布式存储
- **存储桶管理**: 自动分类存储（头像、文档、通用文件）
- **预签名URL**: 安全的文件访问链接，支持过期时间控制

### 🎯 智能匹配系统

- **多维度匹配**: 基于目标学校、专业、申请阶段、预算等综合匹配
- **精准推荐**: AI算法推荐最适合的指导者
- **服务定制**: 文书指导、推荐信、面试辅导等专项服务
- **信誉体系**: 基于完成率、评价、服务质量的信誉评分

### 🏛️ 指导服务交易

- **服务发布**: 学长学姐发布专业指导服务
- **价格透明**: 服务定价和时长明确
- **交易保障**: 平台担保的交易安全
- **进度跟踪**: 服务进度和交付物管理

## 📁 项目结构

```
backend/
├── apps/                        # 应用核心代码
│   ├── api/                     # API层 - 处理HTTP请求
│   │   └── v1/                  # API版本1
│   │       ├── endpoints/       # 路由端点 (Endpoint层)
│   │       │   ├── agents.py    # AI智能体API
│   │       │   ├── auth.py      # 认证授权API
│   │       │   ├── files.py     # 文件上传API
│   │       │   ├── matchings.py # 匹配推荐API
│   │       │   ├── mentors.py   # 导师管理API
│   │       │   ├── messages.py  # 消息系统API
│   │       │   ├── services.py  # 服务管理API
│   │       │   ├── sessions.py  # 会话管理API
│   │       │   ├── students.py  # 学生档案API
│   │       │   └── users.py     # 用户管理API
│   │       ├── services/        # 业务逻辑层 (Service层)
│   │       │   ├── matching.py  # 匹配业务逻辑
│   │       │   ├── mentor.py    # 导师业务逻辑
│   │       │   ├── message.py   # 消息业务逻辑
│   │       │   ├── profile_service.py # 档案服务
│   │       │   ├── student.py   # 学生业务逻辑
│   │       │   └── user.py      # 用户业务逻辑
│   │       ├── repositories/    # 数据访问层 (Repository层)
│   │       │   ├── matching.py  # 匹配数据访问
│   │       │   ├── mentor.py    # 导师数据访问
│   │       │   ├── message.py   # 消息数据访问
│   │       │   ├── service.py   # 服务数据访问
│   │       │   ├── session.py   # 会话数据访问
│   │       │   ├── student.py   # 学生数据访问
│   │       │   └── user.py      # 用户数据访问
│   │       └── deps.py          # 依赖注入
│   ├── schemas/                 # 数据模型定义
│   │   ├── matching.py          # 匹配数据模型
│   │   ├── mentor.py            # 导师数据模型
│   │   ├── message.py           # 消息数据模型
│   │   ├── service.py           # 服务数据模型
│   │   ├── session.py           # 会话数据模型
│   │   ├── student.py           # 学生数据模型
│   │   ├── token.py             # 令牌数据模型
│   │   └── user.py              # 用户数据模型
│   └── main.py                  # FastAPI应用入口
├── libs/                        # 核心基础设施
│   ├── agents/                  # AI智能体系统
│   │   └── v2/                  # 第二代智能体实现
│   │       ├── ai_foundation/   # AI基础设施
│   │       │   ├── agents/      # 智能体工厂
│   │       │   ├── llm/         # 大语言模型管理
│   │       │   └── memory/      # 记忆系统
│   │       ├── core_infrastructure/ # 核心基础设施
│   │       │   ├── error/       # 异常处理
│   │       │   ├── oss/         # 对象存储管理
│   │       │   └── utils/       # 工具函数
│   │       ├── data_communication/ # 数据通信
│   │       │   └── rag/         # RAG知识检索
│   │       ├── tools/           # 智能体工具
│   │       └── config.py        # 智能体配置
│   ├── config/                  # 配置管理
│   │   ├── settings.py          # 应用配置
│   │   ├── database_config.py   # 数据库配置
│   │   ├── ai_config.py         # AI模型配置
│   │   ├── security_config.py   # 安全配置
│   │   └── langsmith_config.py  # LangSmith配置
│   ├── database/                # 数据库访问层
│   │   ├── connection.py        # 数据库连接
│   │   └── adapters.py          # 数据库适配器
│   ├── exceptions/              # 自定义异常
│   ├── logging/                 # 日志配置
│   ├── security/                # 安全工具
│   └── utils/                   # 通用工具
├── tests/                       # 测试文件
│   ├── agents/                  # AI智能体测试 (18个文件)
│   ├── api/                     # API功能测试 (12个文件)
│   ├── database/                # 数据库测试 (10个文件)
│   ├── integration/             # 集成测试 (3个文件)
│   ├── tools/                   # 测试工具 (12个文件)
│   ├── scripts/                 # 测试脚本 (7个文件)
│   └── reports/                 # 测试报告 (10个文件)
├── scripts/                     # 工具脚本
│   ├── deploy.sh                # 部署脚本
│   ├── start_server.sh          # 服务启动脚本
│   ├── start_agents_v2.sh       # AI智能体启动脚本
│   └── docker/                  # Docker相关脚本
├── docs/                        # 项目文档
│   ├── api/                     # API文档
│   ├── guides/                  # 使用指南
│   ├── knowledge_base/          # 知识库文档
│   ├── reports/                 # 项目报告
│   └── *.md                     # 各类文档
├── uploads/                     # 文件上传目录
│   ├── avatars/                 # 头像存储
│   └── documents/               # 文档存储
├── vector_store/                # 向量数据库(ChromaDB)
├── poetry.lock                  # Poetry依赖锁定文件
├── pyproject.toml               # 项目配置文件
└── README.md                    # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装 Poetry (推荐)
curl -sSL https://install.python-poetry.org | python3 -

# 或使用 pip 安装
pip install poetry

# 安装项目依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 2. 配置环境变量

复制项目根目录的 `.env.example` 为 `.env` 并填入配置：

```env
# OpenAI API Key (必需)
OPENAI_API_KEY=sk-...

# Tavily API Key (可选，用于网络搜索)
TAVILY_API_KEY=tvly-...

# Supabase数据库配置 (必需)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_DB_PASSWORD=your-database-password
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# 其他配置
DEBUG=true
```

### 3. 启动MinIO服务

```bash
# 启动MinIO对象存储服务
./scripts/minio/manage_minio.sh start

# 验证MinIO服务状态
./scripts/minio/manage_minio.sh status

# 初始化存储桶（如果需要）
./scripts/minio/manage_minio.sh init
```

MinIO服务信息:
- **服务器地址**: http://localhost:9000
- **控制台地址**: http://localhost:9001
- **访问密钥**: minioadmin
- **秘密密钥**: minioadmin

### 4. 数据库初始化

```bash
# 使用诊断工具检查环境和数据库
cd tests/tools && python fix_test_issues.py

# 验证数据库连接和表结构
cd tests/database && python test_database_comprehensive.py
```

### 5. 启动服务

```bash
# 方式1: 使用 Poetry 启动 (推荐)
poetry run uvicorn apps.main:app --reload

# 方式2: 使用启动脚本
./scripts/start_server.sh

# 方式3: 启动AI智能体系统
./scripts/start_agents_v2.sh

# 访问服务
# - API文档: http://localhost:8000/docs
# - 在线API文档: https://hf1z77hza6.apifox.cn
# - 健康检查: http://localhost:8000/health
```

### 5. 运行测试

```bash
# 一键测试所有功能 (推荐)
cd tests/scripts && ./run_feature_tests.sh

# 按模块运行测试
python -m pytest tests/api/           # API功能测试
python -m pytest tests/database/     # 数据库测试
python -m pytest tests/agents/       # AI智能体测试
python -m pytest tests/integration/  # 集成测试

# 使用测试工具
cd tests/tools && python fix_test_issues.py  # 环境诊断

# 运行完整测试套件
cd tests/scripts && ./run_tests.sh
```

## 🛠️ 技术栈

| 组件           | 技术              | 版本    | 作用            |
| -------------- | ----------------- | ------- | --------------- |
| **后端框架**   | FastAPI           | 0.116.1 | RESTful API服务 |
| **智能体核心** | LangGraph         | 0.2.51  | AI工作流编排    |
| **大语言模型** | OpenAI GPT        | 4o-mini | 智能对话和推理  |
| **知识库**     | ChromaDB          | 0.5.15  | 向量数据库      |
| **文件处理**   | aiofiles          | 24.1.0  | 异步文件操作    |
| **Web界面**    | Streamlit         | 1.41.1  | 交互式前端      |
| **数据库**     | Supabase          | 2.17.0  | 后端数据存储    |
| **网络搜索**   | Tavily/DuckDuckGo | latest  | 实时信息检索    |
| **HTTP客户端** | httpx             | 0.28.1  | 异步HTTP请求    |


## 🗄️ 数据库

基于 Supabase PostgreSQL，包含用户、消息、文件、会话等核心数据表，支持高性能查询和数据一致性。

## 📚 API 文档

完整的API接口文档已部署到 Apifox，包含所有接口的详细说明、参数定义和示例代码：

- **在线文档**: [https://hf1z77hza6.apifox.cn](https://hf1z77hza6.apifox.cn)
- **项目地址**: [https://app.apifox.com/project/7119886](https://app.apifox.com/project/7119886)

### 主要API模块

- **认证系统**: 用户注册、登录、令牌刷新
- **用户管理**: 用户资料管理、公开信息获取
- **学长学姐**: 指导者资料管理、搜索功能
- **学弟学妹**: 申请者资料管理、搜索功能
- **智能匹配**: 基于需求推荐、高级筛选、匹配历史
- **指导服务**: 服务发布、管理、浏览
- **指导会话**: 会话创建、管理、反馈、统计
- **消息系统**: 消息发送、对话管理
- **文件上传**: 头像、文档上传管理
- **AI智能体 v2.0**: 留学规划师对话、智能咨询

## 🧪 测试

```bash
# 运行所有测试
cd tests/scripts && ./run_tests.sh

# 环境诊断
cd tests/tools && python fix_test_issues.py
```

## 🔧 开发指南

项目采用清晰的三层架构：
- **Endpoints层**: 处理HTTP请求和响应
- **Services层**: 编排和执行业务逻辑  
- **Repositories层**: 数据访问和数据库操作

## 🚀 部署

支持 Docker 容器化部署，详细配置请查看 `scripts/docker/` 目录。

```bash
# Docker 部署
docker build -t peerportal-backend .
docker run -d -p 8000:8000 --env-file .env peerportal-backend
```

## 🆘 故障排除

常见问题解决：

```bash
# 环境诊断
cd tests/tools && python fix_test_issues.py

# 检查服务状态
curl http://localhost:8000/health

# 查看详细日志
poetry run uvicorn apps.main:app --reload --log-level debug
```
# offerin启航引路人 - AI留学规划师平台

连接留学申请者（学弟学妹）与目标学校学长学姐的专业指导服务平台。基于FastAPI + LangGraph + Supabase构建，集成AI智能对话、实时消息、文件管理、精准匹配等全方位留学申请指导功能。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-orange.svg)](https://supabase.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.51-red.svg)](https://github.com/langchain-ai/langgraph)

## 平台特色

### 留学双边信息平台

连接想要申请留学的学弟学妹与目标学校院系的学长学姐，为留学申请提供个性化指导服务。

| 功能模块   | 学弟学妹端               | 学长学姐端             | 平台管理         |
| ---------- | ------------------------ | ---------------------- | ---------------- |
| 用户管理   | 申请者资料、申请目标设置 | 指导者资料、学校院系认证 | 用户审核、身份验证 |
| 匹配系统   | 按条件筛选指导者         | 设置指导领域和时间安排 | 智能推荐算法     |
| 服务交易   | 浏览和购买指导服务       | 发布指导服务、设置价格 | 交易保障         |
| 沟通协作   | 实时消息、文档共享       | 指导反馈、进度跟踪     | 对话监控         |
| 评价体系   | 对指导者评价             | 获得信誉积累           | 信誉算法         |

### AI留学规划师

- 智能对话: 基于LangGraph的多轮对话AI系统
- 知识库学习: 支持PDF文档上传，AI自动学习专业知识
- 实时搜索: 集成Tavily网络搜索获取最新留学信息
- 工具融合: 数据库查询 + 网络搜索 + 知识库检索

### 实时消息系统

- 一对一指导: 学长学姐与学弟学妹的专属沟通渠道
- 对话管理: 对话列表、未读消息提醒、消息搜索
- 消息状态: 已发送、已送达、已读状态跟踪
- 文件共享: 支持在对话中分享留学资料和文档

### 文件管理系统

- 头像管理: 用户头像上传和更新
- 文档上传: PDF、Word、TXT等留学申请资料上传
- 云存储: 集成MinIO对象存储，支持分布式存储
- 安全验证: 文件类型、大小、内容安全检查

### 智能匹配系统

- 多维度匹配: 基于目标学校、专业、申请阶段等综合匹配
- 精准推荐: AI算法推荐最适合的指导者
- 服务定制: 文书指导、推荐信、面试辅导等专项服务
- 信誉体系: 基于完成率、评价、服务质量的信誉评分

## 项目结构

```
backend/
├── apps/                    # 应用核心代码
│   ├── api/v1/
│   │   ├── endpoints/       # API路由端点
│   │   ├── services/        # 业务逻辑层
│   │   └── repositories/    # 数据访问层
│   ├── schemas/             # 数据模型定义
│   └── main.py              # FastAPI应用入口
├── libs/                    # 核心基础设施
│   ├── agents/              # AI智能体系统
│   ├── config/              # 配置管理
│   ├── database/            # 数据库访问层
│   ├── exceptions/          # 自定义异常
│   ├── logging/             # 日志配置
│   ├── security/            # 安全工具
│   └── utils/               # 通用工具
├── tests/                   # 测试文件
├── scripts/                 # 工具脚本
├── docs/                    # 项目文档
├── uploads/                 # 文件上传目录
├── vector_store/            # 向量数据库
├── pyproject.toml           # 项目配置
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```env
# OpenAI/OpenRouter API Key (必需，可替换为其他格式的key)
OPENAI_API_KEY=sk-or-v1-...

# Supabase数据库配置 (必需)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_DB_PASSWORD=your-database-password

# 其他配置
DEBUG=true
```

### 3. 启动服务

```bash
# 开发模式
poetry run uvicorn apps.main:app --reload

# 访问API文档
# http://localhost:8000/docs
```

### 4. 运行测试

```bash
# 运行测试
cd tests/scripts && ./run_tests.sh

# 环境诊断
cd tests/tools && python fix_test_issues.py
```

## 技术栈

| 组件     | 技术      | 版本    | 作用         |
| -------- | --------- | ------- | ------------ |
| 后端框架 | FastAPI   | 0.116.1 | RESTful API服务 |
| AI框架   | LangGraph | 0.2.51  | AI工作流编排 |
| LLM      | OpenAI GPT| 4o-mini | 智能对话     |
| 数据库   | Supabase  | 2.17.0  | 数据存储     |
| 向量库   | ChromaDB  | 0.5.15  | 知识库存储   |

## API文档

API文档: [https://hf1z77hza6.apifox.cn](https://hf1z77hza6.apifox.cn)

主要模块: 认证、用户管理、消息系统、文件上传、AI智能体

## 开发指南

项目采用三层架构：
- Endpoints层: 处理HTTP请求和响应
- Services层: 编排和执行业务逻辑
- Repositories层: 数据访问和数据库操作

## 部署

```bash
# Docker部署
docker build -t peerportal-backend .
docker run -d -p 8000:8000 --env-file .env peerportal-backend
```
### **启航引路人 - 留学双边信息平台后端技术文档**

**版本:** 2.0
**项目名称:** 启航引路人 (PeerPortal) - AI留学规划师平台
**目标:** 本文档旨在为"启航引路人"留学双边信息平台的后端开发提供全面的技术规范。该平台基于`libs/app`分离架构，采用FastAPI + Supabase + LangGraph构建，集成AI智能对话、实时消息、精准匹配等全方位留学申请指导功能。

### 1. 业务场景与平台定位

#### 1.1 核心业务模式

**留学双边信息平台**是一个连接留学申请者（学弟学妹）与目标学校学长学姐的专业服务平台：

- **申请者端（学弟学妹）**：寻找目标学校院系的学长学姐，获得留学申请指导
- **指导者端（学长学姐）**：提供专业的留学申请指导服务，包括文书修改、推荐信建议、面试辅导等
- **平台价值**：通过精准匹配，让申请者获得第一手的申请经验和个性化指导

#### 1.2 核心功能模块

| 功能模块     | 学弟学妹端                     | 学长学姐端               | 平台管理           |
| ------------ | ------------------------------ | ------------------------ | ------------------ |
| **用户管理** | 申请者资料、申请目标设置       | 指导者资料、学校院系认证 | 用户审核、身份验证 |
| **匹配系统** | 按学校/专业/申请方向筛选指导者 | 设置指导领域和时间安排   | 智能推荐算法       |
| **服务交易** | 浏览和购买指导服务             | 发布指导服务、设置价格   | 交易保障、纠纷处理 |
| **沟通协作** | 实时消息、文档共享             | 指导反馈、进度跟踪       | 对话监控、质量保证 |
| **评价体系** | 对指导者评价                   | 获得信誉积累             | 信誉算法、排名系统 |

### 2. 技术栈与架构设计

#### 2.1 核心技术栈

| 类别           | 技术栈                          | 版本    | 核心作用                                                                 |
| :------------- | :------------------------------ | :------ | :----------------------------------------------------------------------- |
| **核心框架**   | **FastAPI**                     | 0.116.1 | 高性能异步API框架，支持自动API文档生成和依赖注入                       |
| **数据验证**   | **Pydantic V2**                 | 2.x     | 运行时数据验证，保障API数据完整性                                       |
| **数据库**     | **Supabase (PostgreSQL)**       | latest  | 云原生PostgreSQL数据库，支持实时订阅和存储                             |
| **数据库交互** | **`asyncpg`**                   | latest  | 高性能异步PostgreSQL驱动，支持连接池                                     |
| **认证鉴权**   | **JWT + `python-jose`**         | latest  | 无状态JWT认证，支持多重身份验证                                         |
| **AI智能体**   | **LangGraph**                   | 0.2.51  | AI工作流编排，支持复杂对话逻辑                                          |
| **大语言模型** | **OpenAI GPT**                  | 4o-mini | 智能对话和留学规划推理                                                 |
| **向量数据库** | **ChromaDB**                    | 0.5.15  | 知识库向量化存储，支持语义检索                                         |
| **网络搜索**   | **Tavily**                      | latest  | 实时网络信息检索，获取最新留学资讯                                     |
| **依赖管理**   | **Poetry**                      | latest  | Python项目依赖管理和打包工具                                           |

#### 2.2 架构设计理念

本项目采用**`libs/app`分离架构**，实现关注点分离：

- **`libs/`**: 基础设施层，包含可复用的核心组件
- **`apps/`**: 业务逻辑层，专注具体业务功能实现
- **三层架构**: `Endpoints` → `Services` → `Repositories`

### 3. 数据库设计理念

#### 3.1 实际数据库架构

基于Supabase PostgreSQL的29表完整数据模型：

```
📊 启航引路人数据架构 (29表)
├── 👥 用户与社交系统 (6表)
│   ├── users                    # 用户基础信息
│   ├── profiles                 # 详细个人资料
│   ├── friends                  # 用户好友关系
│   ├── user_credit_logs         # 用户积分记录
│   ├── user_wallets             # 用户钱包系统
│   └── user_reputation_stats    # 用户信誉统计
│
├── 💬 沟通系统 (5表)
│   ├── conversations            # 对话会话
│   ├── conversation_participants # 会话参与者
│   ├── messages                 # 消息内容
│   ├── uploaded_files           # 文件上传管理
│   └── forum_posts              # 论坛帖子 (扩展功能)
│   ├── forum_replies            # 论坛回复
│   ├── forum_likes              # 论坛点赞
│   └── forum_reply_likes        # 回复点赞
│
├── 🎓 留学指导系统 (8表)
│   ├── mentor_matches           # 导师匹配记录
│   ├── mentorship_relationships # 指导关系管理
│   ├── mentorship_sessions      # 指导会话记录
│   ├── mentorship_reviews       # 指导评价
│   ├── mentorship_transactions  # 指导交易
│   ├── services                 # 指导服务发布
│   ├── orders                   # 服务订单
│   └── reviews                  # 服务评价
│
├── 🛠️ 技能与匹配系统 (4表)
│   ├── skill_categories         # 技能分类 (商科、工科等)
│   ├── skills                   # 具体技能项
│   ├── user_skills              # 用户技能映射
│   └── user_learning_needs      # 学习需求分析
│
└── 📅 时间管理 (2表)
    ├── user_availability        # 用户可用时间
    └── user_unavailable_periods # 不可用时间段
```

#### 3.2 核心业务表详解

**🎓 留学指导系统核心表**：

- `mentorship_relationships`：管理学长学姐与学弟学妹的指导关系，包含目标学校、专业、申请阶段等30个字段
- `mentorship_transactions`：记录指导服务的付费交易，支持文书指导、推荐信建议等不同服务类型
- `mentorship_sessions`：追踪每次指导会话，包括指导内容、时长、效果反馈等

**🛠️ 专业技能系统**：

- `skill_categories`：留学申请方向分类（商科、工科、医学、艺术等6大类）
- `skills`：具体专业方向（金融、计算机科学、机械工程等31个专业）
- `user_skills`：学长学姐的专业背景和指导能力映射

**💎 用户扩展系统**：

- `user_learning_needs`：申请者的具体需求（目标学校、专业、申请时间线等）
- `user_reputation_stats`：指导者的信誉评分、成功案例数量等统计
- `user_availability`：指导者的可用时间段管理

### 4. 项目结构

基于`libs/app`分离架构的模块化设计，实现基础设施与业务逻辑的清晰分离。

```
backend/
├── apps/                         # 📦 业务逻辑层
│   ├── api/                      # 🌐 API层
│   │   └── v1/                   # API版本管理
│   │       ├── endpoints/        # 🎯 路由端点 (Endpoints层)
│   │       │   ├── agents.py     # 🤖 AI智能体API
│   │       │   ├── auth.py       # 🔐 用户认证API
│   │       │   ├── files.py      # 📁 文件管理API
│   │       │   ├── matchings.py  # 🎯 智能匹配API
│   │       │   ├── mentors.py    # 👨‍🏫 导师管理API
│   │       │   ├── messages.py   # 💬 消息系统API
│   │       │   ├── services.py   # 🛍️ 服务管理API
│   │       │   ├── sessions.py   # 📅 会话管理API
│   │       │   ├── students.py   # 👨‍🎓 学生档案API
│   │       │   └── users.py      # 👥 用户管理API
│   │       ├── services/         # 🏗️ 业务逻辑层 (Services层)
│   │       │   ├── *.py          # 各模块业务逻辑
│   │       ├── repositories/     # 💾 数据访问层 (Repositories层)
│   │       │   ├── *.py          # 各模块数据访问
│   │       └── deps.py           # 🔗 依赖注入配置
│   ├── schemas/                  # 📋 数据模型定义
│   │   ├── *.py                  # Pydantic数据模型
│   └── main.py                   # 🚀 FastAPI应用入口
│
├── libs/                         # 🏗️ 基础设施层
│   ├── agents/                   # 🤖 AI智能体系统
│   │   └── v2/                   # 第二代智能体实现
│   │       ├── ai_foundation/    # 🤖 AI基础设施
│   │       │   ├── agents/       # 智能体工厂
│   │       │   ├── llm/          # 大语言模型管理
│   │       │   └── memory/       # 记忆系统
│   │       ├── core_infrastructure/ # 🏗️ 核心基础设施
│   │       │   ├── error/        # 异常处理
│   │       │   ├── oss/          # 对象存储
│   │       │   └── utils/        # 工具函数
│   │       ├── data_communication/ # 📡 数据通信
│   │       │   └── rag/          # RAG知识检索
│   │       ├── tools/            # 🛠️ 智能体工具
│   │       └── config.py         # ⚙️ 智能体配置
│   ├── config/                   # ⚙️ 配置管理
│   │   ├── settings.py           # 主配置入口
│   │   ├── database_config.py    # 数据库配置
│   │   ├── ai_config.py          # AI模型配置
│   │   ├── security_config.py    # 安全配置
│   │   └── *.py                  # 其他专项配置
│   ├── database/                 # 💾 数据库访问层
│   │   ├── connection.py         # 连接管理
│   │   └── adapters.py           # 数据库适配器
│   ├── exceptions/               # 🚨 异常处理
│   ├── logging/                  # 📝 日志系统
│   ├── security/                 # 🔒 安全工具
│   └── utils/                    # 🛠️ 通用工具
│
├── scripts/                      # 🛠️ 工具脚本
│   ├── database/                 # 💾 数据库管理脚本
│   │   ├── export_schema.py      # 导出数据库结构
│   │   ├── snapshot_to_sql.py    # 生成SQL脚本
│   │   ├── migrate_remote.py     # 远程迁移执行
│   │   └── check_alignment.py    # 对齐检查
│   └── *.sh                      # 部署和启动脚本
│
├── docs/                        # 📚 项目文档
├── tests/                       # 🧪 测试套件
├── supabase/                    # ☁️ Supabase配置
│   ├── schema_snapshot.json     # 数据库结构快照
│   └── schema.sql               # 数据库迁移脚本
├── uploads/                     # 📁 文件上传存储
│   ├── avatars/                 # 用户头像
│   └── documents/               # 文档存储
├── vector_store/                # 🧠 向量数据库
├── pyproject.toml               # 📦 项目配置
├── poetry.lock                  # 🔒 依赖锁定
└── README.md                    # 📖 项目说明
```

### 5. 核心API设计

#### 5.1 AI智能体API (`/api/v2/agents`)

```python
# AI留学规划师接口
POST   /api/v2/agents/chat/planner       # 与留学规划师对话
POST   /api/v2/agents/chat/consultant    # 与留学顾问对话
POST   /api/v2/agents/chat/auto          # 智能自动对话
GET    /api/v2/agents/status             # AI系统状态检查
```

#### 5.2 用户认证API (`/api/v1/auth`)

```python
POST   /api/v1/auth/login               # 用户登录
POST   /api/v1/auth/register            # 用户注册
POST   /api/v1/auth/refresh             # 刷新令牌
POST   /api/v1/auth/logout              # 用户登出
```

#### 5.3 用户管理API (`/api/v1/users`)

```python
GET    /api/v1/users/me                 # 获取当前用户信息
PUT    /api/v1/users/me                 # 更新用户信息
GET    /api/v1/users/{id}               # 获取指定用户信息
GET    /api/v1/users/                   # 用户列表（管理员）
```

#### 5.4 导师管理API (`/api/v1/mentors`)

```python
GET    /api/v1/mentors                  # 浏览导师列表
GET    /api/v1/mentors/{id}             # 查看导师详情
POST   /api/v1/mentors/profile          # 注册成为导师
PUT    /api/v1/mentors/profile          # 更新导师资料
GET    /api/v1/mentors/services         # 查看导师服务
```

#### 5.5 学生档案API (`/api/v1/students`)

```python
POST   /api/v1/students/profile          # 完善学生资料
PUT    /api/v1/students/learning-needs   # 设置学习需求
GET    /api/v1/students/matches          # 获取推荐导师
GET    /api/v1/students/orders           # 查看服务订单
```

#### 5.6 智能匹配API (`/api/v1/matching`)

```python
POST   /api/v1/matching/recommend        # 基于需求推荐导师
GET    /api/v1/matching/filters          # 获取筛选条件
POST   /api/v1/matching/create           # 创建匹配关系
GET    /api/v1/matching/history          # 查看匹配历史
```

#### 5.7 消息系统API (`/api/v1/messages`)

```python
GET    /api/v1/messages/conversations    # 获取对话列表
GET    /api/v1/messages/{conversation_id} # 获取对话消息
POST   /api/v1/messages/send             # 发送消息
PUT    /api/v1/messages/{id}/read        # 标记已读
```

#### 5.8 文件管理API (`/api/v1/files`)

```python
POST   /api/v1/files/upload/avatar       # 上传头像
POST   /api/v1/files/upload/document     # 上传文档
GET    /api/v1/files/{id}                # 获取文件信息
DELETE /api/v1/files/{id}                # 删除文件
```

### 6. 数据库连接与适配器

#### 6.1 连接管理 (`libs/database/connection.py`)

基于`asyncpg`的连接池管理，支持自动重连和连接生命周期管理：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
import asyncpg
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global db_pool
    # 创建连接池
    db_pool = await asyncpg.create_pool(
        dsn=settings.postgres_url,
        min_size=1, max_size=10,
        command_timeout=30
    )
    yield
    # 关闭连接池
    await db_pool.close()

async def get_database_adapter() -> AsyncGenerator[DatabaseAdapter, None]:
    """按请求提供数据库适配器"""
    async with db_pool.acquire() as connection:
        adapter = PostgreSQLAdapter(connection)
        yield adapter
```

#### 6.2 数据库适配器 (`libs/database/adapters.py`)

统一的数据库操作接口，支持PostgreSQL和Supabase：

```python
class DatabaseAdapter(ABC):
    @abstractmethod
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """获取单条记录"""
        pass

    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        """获取多条记录"""
        pass

    @abstractmethod
    async def execute(self, query: str, *args) -> str:
        """执行SQL命令"""
        pass

class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL适配器实现"""
    def __init__(self, connection):
        self.connection = connection

    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        result = await self.connection.fetchrow(query, *args)
        return dict(result) if result else None
```

### 7. AI智能体系统架构

#### 7.1 系统架构 (`libs/agents/v2/`)

第二代AI智能体采用模块化设计：

```
libs/agents/v2/
├── ai_foundation/           # 🤖 AI基础设施
│   ├── agents/              # 智能体工厂
│   ├── llm/                 # 大语言模型管理
│   └── memory/              # 记忆系统
├── core_infrastructure/     # 🏗️ 核心基础设施
│   ├── error/               # 异常处理
│   ├── oss/                 # 对象存储
│   └── utils/               # 工具函数
├── data_communication/      # 📡 数据通信
│   └── rag/                 # RAG知识检索
├── tools/                   # 🛠️ 智能体工具
└── config.py                # ⚙️ 智能体配置
```

#### 7.2 核心组件

- **智能体工厂**: 创建和管理不同类型的AI智能体
- **LLM管理器**: 统一管理OpenAI等大语言模型接口
- **记忆系统**: 支持会话记忆和长期记忆管理
- **RAG系统**: 基于向量检索的知识库问答
- **工具集成**: 网络搜索、数据库查询等外部工具

### 8. 配置管理系统

#### 8.1 配置架构 (`libs/config/`)

模块化的配置管理：

```python
# libs/config/settings.py
from libs.config.database_config import DatabaseConfig
from libs.config.ai_config import AIConfig
from libs.config.security_config import SecurityConfig

class Settings(BaseSettings):
    """主配置类，组合各个专项配置"""

    # 应用基本配置
    APP_NAME: str = "启航引路人 API"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化专项配置
        self.database = DatabaseConfig()
        self.ai = AIConfig()
        self.security = SecurityConfig()
```

#### 8.2 专项配置

- **数据库配置**: PostgreSQL/Supabase连接参数
- **AI配置**: OpenAI、Tavily等API密钥
- **安全配置**: JWT密钥、加密参数

### 9. 部署与运维

#### 9.1 快速启动

```bash
# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
poetry run uvicorn apps.main:app --reload
```

#### 9.2 Docker部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /usr/src/app

# 安装Poetry和依赖
COPY poetry.lock pyproject.toml ./
RUN pip install poetry && poetry install --no-dev

# 复制应用代码
COPY apps/ apps/
COPY libs/ libs/

# 启动服务
CMD ["poetry", "run", "uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 9.3 数据库迁移

```bash
# 导出数据库结构
poetry run python scripts/database/export_schema.py

# 生成迁移脚本
poetry run python scripts/database/snapshot_to_sql.py

# 执行远程迁移
poetry run python scripts/database/migrate_remote.py

# 检查对齐状态
poetry run python scripts/database/check_alignment.py
```

### 10. 开发规范

#### 10.1 三层架构模式

严格遵循`Endpoints → Services → Repositories`的分层架构：

- **Endpoints层**: 仅处理HTTP请求/响应，不包含业务逻辑
- **Services层**: 实现完整业务用例，编排Repository操作
- **Repositories层**: 原子化数据操作，不包含业务逻辑

#### 10.2 代码规范

- 使用类型注解，提高代码可读性
- 遵循RESTful API设计规范
- 异步优先，支持高并发处理
- 统一错误处理和日志记录

### 11. 测试策略

#### 11.1 测试架构

```bash
tests/
├── agents/              # AI智能体测试
├── api/                 # API功能测试
├── database/            # 数据库测试
├── integration/         # 集成测试
├── tools/               # 测试工具
├── scripts/             # 测试脚本
└── reports/             # 测试报告
```

#### 11.2 测试运行

```bash
# 运行所有测试
poetry run pytest

# 按模块测试
poetry run pytest tests/api/
poetry run pytest tests/database/

# 生成测试报告
poetry run pytest --cov=apps --cov-report=html
```

---

## 总结

启航引路人平台基于现代化的技术栈和架构设计，为留学申请者提供全方位的AI智能指导服务。通过`libs/app`分离架构、三层架构模式和模块化设计，确保了代码的可维护性、可扩展性和高性能。

**核心特色**：

- 🤖 **AI驱动**: 集成LangGraph和OpenAI，提供智能留学规划
- 🎯 **精准匹配**: 基于多维度算法的导师-学生智能匹配
- 💬 **实时交互**: 完整的消息和文件共享系统
- 🏗️ **架构优良**: 模块化设计，支持快速迭代和扩展
- ☁️ **云原生**: 基于Supabase的云原生数据库和存储

该平台不仅技术先进，更重要的是连接了真实的留学需求与供给，为学子们的留学梦想提供可靠的技术支撑。

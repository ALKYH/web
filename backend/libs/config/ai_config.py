"""
AI 配置模块
管理所有 AI 相关的配置项
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class AIConfig(BaseSettings):
    """AI 配置类"""
    
    # 基础 AI 配置
    OPENAI_API_KEY: str = Field(..., description="OpenAI API 密钥")
    OPENAI_BASE_URL: Optional[str] = Field(default=None, description="OpenAI API 基础URL")

    # OpenRouter 配置
    OPENROUTER_HTTP_REFERER: Optional[str] = Field(default=None, description="OpenRouter HTTP-Referer header")
    OPENROUTER_X_TITLE: Optional[str] = Field(default=None, description="OpenRouter X-Title header")

    DEFAULT_EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", description="默认嵌入模型")
    
    # Agent 性能配置
    AGENT_MAX_ITERATIONS: int = Field(default=10, description="Agent 最大思考轮数")
    AGENT_TIMEOUT_SECONDS: int = Field(default=300, description="Agent 超时时间（秒）")
    
    # 搜索工具配置
    TAVILY_API_KEY: Optional[str] = Field(default=None, description="Tavily 搜索 API 密钥")
    
    # LangSmith 配置 - Agent 监控和评估
    LANGCHAIN_TRACING_V2: Optional[bool] = Field(default=False, description="启用 LangChain 追踪")
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None, description="LangChain API 密钥")
    LANGCHAIN_PROJECT: Optional[str] = Field(default="AI留学规划师-默认", description="LangChain 项目名称")
    LANGCHAIN_ENDPOINT: Optional[str] = Field(default="https://api.smith.langchain.com", description="LangChain 端点")
    
    # 记忆系统配置
    REDIS_URL: Optional[str] = Field(default=None, description="Redis 连接字符串")
    MEMORY_SESSION_TTL: int = Field(default=86400, description="会话记忆保持时间（秒）")
    MEMORY_DECAY_DAYS: int = Field(default=30, description="长期记忆衰减周期（天）")
    
    # 企业级知识库系统配置
    MILVUS_HOST: Optional[str] = Field(default=None, description="Milvus 主机地址")
    MILVUS_PORT: int = Field(default=19530, description="Milvus 端口")
    MILVUS_USER: Optional[str] = Field(default=None, description="Milvus 用户名")
    MILVUS_PASSWORD: Optional[str] = Field(default=None, description="Milvus 密码")
    
    MONGODB_URL: Optional[str] = Field(default=None, description="MongoDB 连接字符串")
    ELASTICSEARCH_URL: Optional[str] = Field(default=None, description="Elasticsearch 连接字符串")
    
    # RAG 系统配置
    RAG_CHUNK_SIZE: int = Field(default=1000, description="文档分块大小")
    RAG_CHUNK_OVERLAP: int = Field(default=200, description="分块重叠长度")
    RAG_TOP_K: int = Field(default=5, description="默认检索数量")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

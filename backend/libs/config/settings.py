"""
应用配置管理模块
统一管理应用的所有配置项，组合各个专门的配置类
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

from libs.config.database_config import DatabaseConfig
from libs.config.ai_config import AIConfig
from libs.config.security_config import SecurityConfig
from libs.config.minio_config import MinIOConfig


class Settings(BaseSettings):
    """主应用配置类，组合各个专门的配置模块"""
    
    # 应用基本配置
    APP_NAME: str = Field(default="启航引路人 API", description="应用名称")
    VERSION: str = Field(default="1.0.0", description="应用版本")
    DESCRIPTION: str = Field(default="基于 FastAPI 的社交平台后端 API", description="应用描述")
    DEBUG: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", description="服务器监听地址")
    PORT: int = Field(default=8000, description="服务器端口")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # 忽略额外的环境变量
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化各个专门的配置模块
        object.__setattr__(self, 'database', DatabaseConfig())
        object.__setattr__(self, 'ai', AIConfig())
        object.__setattr__(self, 'security', SecurityConfig())
        object.__setattr__(self, 'minio', MinIOConfig())
    
    @property
    def postgres_url(self) -> str:
        """代理到数据库配置的 postgres_url"""
        return self.database.postgres_url

    # 为了向后兼容，提供一些常用配置的直接访问属性
    @property
    def SECRET_KEY(self) -> str:
        return self.security.SECRET_KEY
    
    @property
    def ALGORITHM(self) -> str:
        return self.security.ALGORITHM
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.security.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.ai.OPENAI_API_KEY

    @property
    def DEFAULT_MODEL(self) -> str:
        """根据配置动态返回默认模型"""
        # 如果配置了OpenRouter，使用OpenRouter免费模型
        if self.ai.OPENAI_BASE_URL and 'openrouter.ai' in self.ai.OPENAI_BASE_URL:
            return "z-ai/glm-4.5-air:free"  # OpenRouter免费模型
        # 否则使用标准OpenAI模型
        return "gpt-4o-mini"


# 创建全局配置实例
settings = Settings()
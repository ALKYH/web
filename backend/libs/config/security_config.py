"""
安全配置模块
管理认证、授权和安全相关的配置项
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import json


class SecurityConfig(BaseSettings):
    """安全配置类"""
    
    # JWT 配置
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT 密钥")
    ALGORITHM: str = Field(default="HS256", description="JWT 算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="访问令牌过期时间（分钟）")
    
    # CORS 配置
    ALLOWED_ORIGINS: str = Field(
        default='["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]',
        description="允许的跨域来源"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }
    
    @property
    def origins_list(self) -> List[str]:
        """将 CORS 配置字符串转换为列表"""
        try:
            return json.loads(self.ALLOWED_ORIGINS)
        except json.JSONDecodeError:
            return ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]

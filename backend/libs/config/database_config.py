"""
数据库配置模块
专门管理数据库相关的配置项
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class DatabaseConfig(BaseSettings):
    """数据库配置类"""
    
    # 连接池配置
    DB_POOL_MIN_SIZE: int = Field(default=1, description="数据库连接池最小连接数")
    DB_POOL_MAX_SIZE: int = Field(default=10, description="数据库连接池最大连接数")
    
    # Supabase 配置
    SUPABASE_URL: str = Field(..., description="Supabase 项目 URL")
    SUPABASE_KEY: str = Field(..., description="Supabase API Key")
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None, description="Supabase JWT 密钥")
    SUPABASE_DB_PASSWORD: Optional[str] = Field(default=None, description="Supabase 数据库密码")
    
    # 可选的直连 PostgreSQL 配置
    DATABASE_URL: Optional[str] = Field(default=None, description="PostgreSQL 直连字符串")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

    @property
    def postgres_url(self) -> str:
        """从 Supabase 配置构建 PostgreSQL 连接字符串"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
            
        if hasattr(self, '_postgres_url'):
            return self._postgres_url
            
        # 从环境变量获取数据库密码
        db_password = self.SUPABASE_DB_PASSWORD or os.getenv('SUPABASE_DB_PASSWORD')
        if not db_password:
            raise ValueError(
                "缺少数据库密码配置。请在 .env 文件中设置 SUPABASE_DB_PASSWORD\n"
                "您可以在 Supabase 项目设置中找到这个密码。"
            )
            
        # 从 Supabase URL 提取项目 ID
        if 'supabase.co' in self.SUPABASE_URL:
            project_id = self.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
            self._postgres_url = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
        else:
            raise ValueError("Invalid SUPABASE_URL format")
            
        return self._postgres_url

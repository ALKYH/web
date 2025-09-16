"""
MinIO对象存储配置管理模块
统一管理MinIO相关的配置项
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class MinIOConfig(BaseSettings):
    """MinIO配置类"""

    # MinIO服务器配置
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO服务器端点")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO访问密钥")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO秘密密钥")

    # MinIO存储桶配置
    MINIO_BUCKET_AVATARS: str = Field(default="avatars", description="头像存储桶名称")
    MINIO_BUCKET_DOCUMENTS: str = Field(default="documents", description="文档存储桶名称")
    MINIO_BUCKET_GENERAL: str = Field(default="general", description="通用存储桶名称")

    # MinIO安全配置
    MINIO_SECURE: bool = Field(default=False, description="是否使用HTTPS")
    MINIO_REGION: Optional[str] = Field(default=None, description="MinIO区域")

    # MinIO客户端配置
    MINIO_POOL_SIZE: int = Field(default=10, description="连接池大小")

    # 文件大小限制
    MAX_AVATAR_SIZE: int = Field(default=5 * 1024 * 1024, description="头像最大文件大小(字节)")
    MAX_DOCUMENT_SIZE: int = Field(default=10 * 1024 * 1024, description="文档最大文件大小(字节)")
    MAX_GENERAL_SIZE: int = Field(default=50 * 1024 * 1024, description="通用文件最大文件大小(字节)")

    # 文件过期时间配置
    AVATAR_URL_EXPIRE_MINUTES: int = Field(default=60, description="头像URL过期时间(分钟)")
    DOCUMENT_URL_EXPIRE_MINUTES: int = Field(default=1440, description="文档URL过期时间(分钟)")  # 24小时
    GENERAL_URL_EXPIRE_MINUTES: int = Field(default=1440, description="通用文件URL过期时间(分钟)")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

    @property
    def minio_url(self) -> str:
        """获取完整的MinIO URL"""
        protocol = "https" if self.MINIO_SECURE else "http"
        return f"{protocol}://{self.MINIO_ENDPOINT}"

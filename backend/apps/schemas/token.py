"""
JWT Token - 数据模型
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AuthenticatedUser(BaseModel):
    """
    认证后的用户信息模型，通常在请求上下文中传递
    """
    id: UUID = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: Optional[str] = Field(None, description="用户角色")


class Token(BaseModel):
    """Token API 响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="令牌过期时间（秒）")
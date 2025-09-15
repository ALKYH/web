from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ServiceBase(BaseModel):
    """指导服务基础模型 - 匹配 services 表"""
    title: str = Field(..., max_length=200, description="服务标题")
    description: Optional[str] = Field(None, description="服务描述")
    category: Optional[str] = Field(None, description="服务分类")
    price: Optional[Decimal] = Field(None, ge=0, description="服务价格（numeric）")
    duration_hours: Optional[int] = Field(None, ge=1, description="服务时长（小时）")
    
class ServiceCreate(ServiceBase):
    """创建服务"""
    pass

class ServiceUpdate(BaseModel):
    """更新服务"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None  # 整数类型
    duration_hours: Optional[int] = None

class ServiceRead(ServiceBase):
    """服务详情 - 匹配实际 services 表结构"""
    id: int
    navigator_id: Optional[int]  # 可空
    is_active: bool = Field(default=True, description="是否可用")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ServicePublic(BaseModel):
    """公开的服务信息（用于搜索和展示） - 匹配实际 services 表结构"""
    id: int
    navigator_id: Optional[int]
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    duration_hours: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
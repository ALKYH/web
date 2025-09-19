"""
服务 - 数据模型
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 服务 (Service) ============
class ServiceBase(BaseModel):
    """服务基础模型"""
    mentor_id: UUID = Field(..., description="提供服务的导师ID")
    skill_id: UUID = Field(..., description="关联的技能ID")
    title: str = Field(..., max_length=200, description="服务标题")
    description: Optional[str] = Field(None, description="服务描述")
    price: Decimal = Field(..., ge=0, description="服务价格 (CNY)")
    duration_hours: int = Field(..., ge=1, description="服务时长（小时）")
    is_active: bool = Field(True, description="是否可用")


class ServiceCreate(ServiceBase):
    """服务创建模型"""
    pass


class ServiceUpdate(BaseModel):
    """服务更新模型"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    duration_hours: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class Service(IDModel, TimestampModel, ServiceBase):
    """服务完整模型"""
    class Config(IDModel.Config):
        from_attributes = True

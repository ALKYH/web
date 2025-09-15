"""
订单系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class OrderStatus(str, Enum):
    """订单状态"""
    pending = "pending"
    confirmed = "confirmed"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    refunded = "refunded"


class OrderBase(BaseModel):
    """订单基础模型"""
    service_id: int = Field(..., description="服务ID")
    client_id: int = Field(..., description="客户ID")
    navigator_id: int = Field(..., description="导航员ID")
    status: OrderStatus = Field(default=OrderStatus.pending, description="订单状态")
    scheduled_at: Optional[datetime] = Field(None, description="预约时间")
    total_price: Optional[Decimal] = Field(None, ge=0, description="总价")
    notes: Optional[str] = Field(None, description="备注")


class OrderCreate(OrderBase):
    """创建订单"""
    pass


class OrderUpdate(BaseModel):
    """更新订单"""
    status: Optional[OrderStatus] = None
    scheduled_at: Optional[datetime] = None
    total_price: Optional[Decimal] = None
    notes: Optional[str] = None


class OrderRead(OrderBase):
    """订单读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class OrderDetail(OrderRead):
    """订单详情"""
    service_title: Optional[str] = None
    service_description: Optional[str] = None
    client_username: Optional[str] = None
    client_email: Optional[str] = None
    navigator_username: Optional[str] = None
    navigator_email: Optional[str] = None


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: List[OrderDetail]
    total: int
    has_next: bool


class OrderStats(BaseModel):
    """订单统计"""
    total_orders: int = 0
    pending_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    total_revenue: Decimal = Field(default=Decimal('0'))
    average_order_value: Optional[Decimal] = None

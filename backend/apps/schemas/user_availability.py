"""
用户可用性系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time


class UserAvailabilityBase(BaseModel):
    """用户可用性基础模型"""
    user_id: int = Field(..., description="用户ID")
    day_of_week: int = Field(..., ge=0, le=6, description="星期几(0=周日, 6=周六)")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    availability_type: str = Field(default="mentoring", description="可用性类型(mentoring/learning)")
    is_active: bool = Field(default=True, description="是否激活")
    notes: Optional[str] = Field(None, description="备注")


class UserAvailabilityCreate(UserAvailabilityBase):
    """创建用户可用性"""
    pass


class UserAvailabilityUpdate(BaseModel):
    """更新用户可用性"""
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    timezone: Optional[str] = None
    availability_type: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class UserAvailabilityRead(UserAvailabilityBase):
    """用户可用性读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserAvailabilityDetail(UserAvailabilityRead):
    """用户可用性详情"""
    username: Optional[str] = None
    user_role: Optional[str] = None


class UserAvailabilityListResponse(BaseModel):
    """用户可用性列表响应"""
    availabilities: List[UserAvailabilityDetail]
    total: int


class AvailabilitySlot(BaseModel):
    """可用时间段"""
    day_of_week: int
    start_time: time
    end_time: time
    timezone: str
    is_available: bool = True


class WeeklyAvailability(BaseModel):
    """每周可用性"""
    user_id: int
    timezone: str = "Asia/Shanghai"
    slots: List[AvailabilitySlot] = []


class AvailabilityConflict(BaseModel):
    """可用性冲突"""
    conflicting_slot: UserAvailabilityRead
    conflict_reason: str

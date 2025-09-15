"""
用户不可用时间段系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time


class UserUnavailablePeriodBase(BaseModel):
    """用户不可用时间段基础模型"""
    user_id: int = Field(..., description="用户ID")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    start_time: Optional[time] = Field(None, description="开始时间(可选，用于部分时间段)")
    end_time: Optional[time] = Field(None, description="结束时间(可选，用于部分时间段)")
    reason: Optional[str] = Field(None, description="不可用原因")
    description: Optional[str] = Field(None, description="详细描述")
    affects_mentoring: bool = Field(default=True, description="影响指导")
    affects_learning: bool = Field(default=True, description="影响学习")


class UserUnavailablePeriodCreate(UserUnavailablePeriodBase):
    """创建用户不可用时间段"""
    pass


class UserUnavailablePeriodUpdate(BaseModel):
    """更新用户不可用时间段"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None
    description: Optional[str] = None
    affects_mentoring: Optional[bool] = None
    affects_learning: Optional[bool] = None


class UserUnavailablePeriodRead(UserUnavailablePeriodBase):
    """用户不可用时间段读取模型"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserUnavailablePeriodDetail(UserUnavailablePeriodRead):
    """用户不可用时间段详情"""
    username: Optional[str] = None


class UserUnavailablePeriodListResponse(BaseModel):
    """用户不可用时间段列表响应"""
    periods: List[UserUnavailablePeriodDetail]
    total: int
    has_next: bool


class UnavailablePeriodStats(BaseModel):
    """不可用时间段统计"""
    total_periods: int = 0
    current_periods: int = 0  # 当前有效的不可用时间段
    upcoming_periods: int = 0  # 即将到来的不可用时间段
    total_days_unavailable: int = 0


class AvailabilityCalendar(BaseModel):
    """可用性日历"""
    user_id: int
    date: date
    is_available: bool = True
    unavailable_periods: List[UserUnavailablePeriodRead] = []


class BulkUnavailablePeriodCreate(BaseModel):
    """批量创建不可用时间段"""
    periods: List[UserUnavailablePeriodCreate] = Field(..., min_items=1, description="不可用时间段列表")

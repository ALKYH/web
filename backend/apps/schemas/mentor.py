from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class MentorBase(BaseModel):
    """指导者基础模型 - 匹配 mentorship_relationships """
    title: str = Field(..., description="指导关系标题")
    description: Optional[str] = Field(None, description="指导描述")
    learning_goals: Optional[str] = Field(None, description="学习目标")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="时薪")
    session_duration_minutes: Optional[int] = Field(default=60, description="会话时长（分钟）")
    
class MentorProfile(MentorBase):
    """完整的指导者资料 - 完全匹配 mentorship_relationships 表"""
    id: int
    mentor_id: Optional[int] = None  # 可空，与数据库一致
    mentee_id: Optional[int] = None
    skill_id: Optional[int] = None
    match_id: Optional[int] = None
    success_criteria: Optional[str] = None
    start_date: Optional[date] = None  # date 类型，与数据库一致
    estimated_end_date: Optional[date] = None  # date 类型，与数据库一致
    total_sessions_planned: Optional[int] = None
    total_amount: Optional[Decimal] = None  # numeric 类型，与数据库一致
    payment_schedule: Optional[str] = Field(default="per_session", description="付款时间表")
    relationship_type: Optional[str] = Field(default="paid", description="关系类型")  # 数据库默认 'paid'
    preferred_communication: Optional[str] = None
    meeting_frequency: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = Field(default="pending", description="状态")  # 数据库默认 'pending'
    cancellation_reason: Optional[str] = None
    sessions_completed: Optional[int] = Field(default=0, description="已完成会话数")
    total_hours_spent: Optional[Decimal] = Field(default=Decimal('0'), description="总花费时间")  # numeric，默认 0
    last_session_at: Optional[datetime] = None
    next_session_at: Optional[datetime] = None
    created_at: Optional[datetime] = None  # 可空，与数据库一致
    updated_at: Optional[datetime] = None  # 可空，与数据库一致
    completed_at: Optional[datetime] = None
    currency: Optional[str] = Field(default="CNY", description="货币类型")
    
    class Config:
        from_attributes = True

class MentorUpdate(BaseModel):
    """更新指导者资料"""
    title: Optional[str] = None
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    hourly_rate: Optional[Decimal] = None  # 与数据库 numeric 类型一致
    session_duration_minutes: Optional[int] = None
    success_criteria: Optional[str] = None
    estimated_end_date: Optional[date] = None
    total_sessions_planned: Optional[int] = None
    total_amount: Optional[Decimal] = None
    payment_schedule: Optional[str] = None
    relationship_type: Optional[str] = None
    preferred_communication: Optional[str] = None
    meeting_frequency: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None

class MentorCreate(MentorBase):
    """创建指导者资料"""
    mentor_id: Optional[int] = None
    mentee_id: Optional[int] = None
    skill_id: Optional[int] = None
    match_id: Optional[int] = None
    success_criteria: Optional[str] = None
    estimated_end_date: Optional[date] = None
    total_sessions_planned: Optional[int] = None
    total_amount: Optional[Decimal] = None
    payment_schedule: Optional[str] = Field(default="per_session")
    relationship_type: Optional[str] = Field(default="paid")
    preferred_communication: Optional[str] = None
    meeting_frequency: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = Field(default="pending")


class MentorPublic(BaseModel):
    """公开的指导者信息（用于搜索和展示）"""
    id: int
    mentor_id: Optional[int] = None  # 可空，与数据库一致
    title: str
    description: Optional[str] = None
    hourly_rate: Optional[Decimal] = None  # numeric 类型
    rating: Optional[Decimal] = None  # 如果有评分字段
    sessions_completed: Optional[int] = Field(default=0)

    class Config:
        from_attributes = True

"""
导师制 & 服务 - 数据模型
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from enum import Enum

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

# ============ 导师关系 (Mentorship) ============
class MentorshipStatus(str, Enum):
    """导师关系状态"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MentorshipBase(BaseModel):
    """导师关系基础模型"""
    mentor_id: UUID = Field(..., description="导师ID")
    mentee_id: UUID = Field(..., description="学员ID")
    service_id: UUID = Field(..., description="关联的服务ID")
    status: MentorshipStatus = Field(MentorshipStatus.PENDING, description="关系状态")

class MentorshipCreate(MentorshipBase):
    """导师关系创建模型"""
    pass

class MentorshipUpdate(BaseModel):
    """导师关系更新模型"""
    status: Optional[MentorshipStatus] = None

class Mentorship(IDModel, TimestampModel, MentorshipBase):
    """导师关系完整模型"""
    class Config(IDModel.Config):
        from_attributes = True

# ============ 关系会话 (Session) ============
class SessionStatus(str, Enum):
    """会话状态"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SessionBase(BaseModel):
    """会话基础模型"""
    mentorship_id: UUID = Field(..., description="所属导师关系ID")
    scheduled_at: datetime = Field(..., description="预定时间")
    duration_minutes: int = Field(60, ge=15, description="持续时间（分钟）")
    status: SessionStatus = Field(SessionStatus.SCHEDULED, description="会话状态")

class SessionCreate(SessionBase):
    """会话创建模型"""
    pass

class SessionUpdate(BaseModel):
    """会话更新模型"""
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15)
    status: Optional[SessionStatus] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None

class Session(IDModel, TimestampModel, SessionBase):
    """会话完整模型"""
    mentor_notes: Optional[str] = Field(None, description="导师笔记")
    mentee_notes: Optional[str] = Field(None, description="学员笔记")
    class Config(IDModel.Config):
        from_attributes = True

# ============ 评价 (Review) ============
class ReviewBase(BaseModel):
    """评价基础模型"""
    mentorship_id: UUID = Field(..., description="所属导师关系ID")
    reviewer_id: UUID = Field(..., description="评价者ID")
    reviewee_id: UUID = Field(..., description="被评价者ID")
    rating: int = Field(..., ge=1, le=5, description="评分 (1-5)")
    comment: Optional[str] = Field(None, description="评价内容")

class ReviewCreate(ReviewBase):
    """评价创建模型"""
    pass

class ReviewUpdate(BaseModel):
    """评价更新模型"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Review(IDModel, TimestampModel, ReviewBase):
    """评价完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 会话读取模型 (SessionRead) ============
class SessionRead(Session):
    """会话读取模型"""
    pass


# ============ 会话反馈模型 (SessionFeedback) ============
class SessionFeedbackBase(BaseModel):
    """会话反馈基础模型"""

    session_id: UUID = Field(..., description="会话ID")
    rating: int = Field(..., ge=1, le=5, description="评分 (1-5)")
    feedback: Optional[str] = Field(None, description="反馈内容")
    is_mentor_feedback: bool = Field(True, description="是否为导师反馈")


class SessionFeedbackCreate(SessionFeedbackBase):
    """会话反馈创建模型"""
    pass


class SessionFeedback(SessionFeedbackBase, IDModel, TimestampModel):
    """会话反馈完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 会话总结模型 (SessionSummary) ============
class SessionSummary(BaseModel):
    """会话总结信息"""

    session_id: UUID = Field(..., description="会话ID")
    duration_actual: Optional[int] = Field(None, description="实际持续时间（分钟）")
    topics_discussed: List[str] = Field(default_factory=list, description="讨论的话题")
    key_takeaways: List[str] = Field(default_factory=list, description="关键收获")
    next_steps: List[str] = Field(default_factory=list, description="后续行动")
    summary: Optional[str] = Field(None, description="总结内容")

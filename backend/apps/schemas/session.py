"""
会话中心 - 数据模型
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 会话状态枚举 ============
class SessionStatus(str, Enum):
    """会话状态"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============ 会话模型 ============
class SessionBase(BaseModel):
    """会话基础模型"""

    mentorship_id: UUID = Field(..., description="所属导师关系ID")
    scheduled_at: datetime = Field(..., description="预定时间")
    duration_minutes: int = Field(60, ge=15, description="持续时间（分钟）")
    status: SessionStatus = Field(SessionStatus.SCHEDULED, description="会话状态")
    mentor_notes: Optional[str] = Field(None, description="导师笔记")
    mentee_notes: Optional[str] = Field(None, description="学员笔记")


class SessionCreate(SessionBase):
    """会话创建模型"""
    pass


class SessionRead(Session):
    """会话读取模型"""
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

    class Config(IDModel.Config):
        from_attributes = True


# ============ 会话统计模型 ============
class SessionStats(BaseModel):
    """会话统计信息"""

    total_sessions: int = Field(..., description="总会话数")
    completed_sessions: int = Field(..., description="已完成会话数")
    upcoming_sessions: int = Field(..., description="即将到来的会话数")
    cancelled_sessions: int = Field(..., description="已取消会话数")


# ============ 会话反馈模型 ============
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


# ============ 会话总结模型 ============
class SessionSummary(BaseModel):
    """会话总结信息"""

    session_id: UUID = Field(..., description="会话ID")
    duration_actual: Optional[int] = Field(None, description="实际持续时间（分钟）")
    topics_discussed: List[str] = Field(default_factory=list, description="讨论的话题")
    key_takeaways: List[str] = Field(default_factory=list, description="关键收获")
    next_steps: List[str] = Field(default_factory=list, description="后续行动")
    summary: Optional[str] = Field(None, description="总结内容")

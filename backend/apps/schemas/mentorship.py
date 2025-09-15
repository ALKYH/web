"""
导师系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class MatchStatus(str, Enum):
    """匹配状态"""
    suggested = "suggested"
    contacted = "contacted"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"


class RelationshipStatus(str, Enum):
    """导师关系状态"""
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    paused = "paused"


class SessionStatus(str, Enum):
    """导师会话状态"""
    scheduled = "scheduled"
    confirmed = "confirmed"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class PaymentStatus(str, Enum):
    """支付状态"""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class TransactionType(str, Enum):
    """交易类型"""
    payment = "payment"
    refund = "refund"
    bonus = "bonus"
    adjustment = "adjustment"


class MentorMatchBase(BaseModel):
    """导师匹配基础模型"""
    mentor_id: int = Field(..., description="导师ID")
    mentee_id: int = Field(..., description="学员ID")
    skill_id: Optional[int] = Field(None, description="技能ID")
    learning_need_id: Optional[int] = Field(None, description="学习需求ID")
    mentor_skill_id: Optional[int] = Field(None, description="导师技能ID")
    match_score: Optional[float] = Field(None, ge=0, le=1, description="匹配分数")
    match_algorithm: str = Field(default="v1.0", description="匹配算法版本")
    match_factors: Optional[Dict[str, Any]] = Field(None, description="匹配因素")
    status: MatchStatus = Field(default=MatchStatus.suggested, description="匹配状态")


class MentorMatchCreate(MentorMatchBase):
    """创建导师匹配"""
    pass


class MentorMatchUpdate(BaseModel):
    """更新导师匹配"""
    status: Optional[MatchStatus] = None
    mentor_viewed_at: Optional[datetime] = None
    mentee_viewed_at: Optional[datetime] = None
    mentor_responded_at: Optional[datetime] = None
    mentee_responded_at: Optional[datetime] = None


class MentorMatchRead(MentorMatchBase):
    """导师匹配读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    mentor_viewed_at: Optional[datetime] = None
    mentee_viewed_at: Optional[datetime] = None
    mentor_responded_at: Optional[datetime] = None
    mentee_responded_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class MentorshipRelationshipBase(BaseModel):
    """导师关系基础模型"""
    mentor_id: int = Field(..., description="导师ID")
    mentee_id: int = Field(..., description="学员ID")
    skill_id: Optional[int] = Field(None, description="技能ID")
    match_id: Optional[int] = Field(None, description="匹配ID")
    title: str = Field(..., min_length=1, max_length=200, description="关系标题")
    description: Optional[str] = Field(None, description="关系描述")
    learning_goals: Optional[str] = Field(None, description="学习目标")
    success_criteria: Optional[str] = Field(None, description="成功标准")
    start_date: date = Field(default_factory=lambda: date.today(), description="开始日期")
    estimated_end_date: Optional[date] = Field(None, description="预计结束日期")
    total_sessions_planned: Optional[int] = Field(None, ge=1, description="计划总会话数")
    session_duration_minutes: int = Field(default=60, ge=15, le=480, description="会话时长(分钟)")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="小时费率")
    currency: str = Field(default="CNY", description="货币类型")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="总金额")
    payment_schedule: str = Field(default="per_session", description="支付计划")
    relationship_type: str = Field(default="paid", description="关系类型")
    preferred_communication: Optional[str] = Field(None, description="偏好沟通方式")
    meeting_frequency: Optional[str] = Field(None, description="会议频率")
    timezone: Optional[str] = Field(None, description="时区")
    status: RelationshipStatus = Field(default=RelationshipStatus.pending, description="关系状态")


class MentorshipRelationshipCreate(MentorshipRelationshipBase):
    """创建导师关系"""
    pass


class MentorshipRelationshipUpdate(BaseModel):
    """更新导师关系"""
    title: Optional[str] = None
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    success_criteria: Optional[str] = None
    estimated_end_date: Optional[date] = None
    total_sessions_planned: Optional[int] = None
    session_duration_minutes: Optional[int] = None
    hourly_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    total_amount: Optional[Decimal] = None
    payment_schedule: Optional[str] = None
    relationship_type: Optional[str] = None
    preferred_communication: Optional[str] = None
    meeting_frequency: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[RelationshipStatus] = None
    cancellation_reason: Optional[str] = None
    completed_at: Optional[datetime] = None


class MentorshipRelationshipRead(MentorshipRelationshipBase):
    """导师关系读取模型"""
    id: int
    cancellation_reason: Optional[str] = None
    sessions_completed: int = 0
    total_hours_spent: Decimal = Field(default=Decimal('0'), description="总时长")
    last_session_at: Optional[datetime] = None
    next_session_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class MentorshipReviewBase(BaseModel):
    """导师评价基础模型"""
    relationship_id: int = Field(..., description="关系ID")
    reviewer_id: int = Field(..., description="评价者ID")
    reviewee_id: int = Field(..., description="被评价者ID")
    reviewer_role: str = Field(..., description="评价者角色(mentor/mentee)")
    overall_rating: int = Field(..., ge=1, le=5, description="总体评分")
    communication_rating: Optional[int] = Field(None, ge=1, le=5, description="沟通评分")
    expertise_rating: Optional[int] = Field(None, ge=1, le=5, description="专业评分")
    timeliness_rating: Optional[int] = Field(None, ge=1, le=5, description="及时性评分")
    value_rating: Optional[int] = Field(None, ge=1, le=5, description="价值评分")
    professionalism_rating: Optional[int] = Field(None, ge=1, le=5, description="专业性评分")
    comment: Optional[str] = Field(None, description="评价内容")
    pros: Optional[str] = Field(None, description="优点")
    areas_for_improvement: Optional[str] = Field(None, description="改进领域")
    would_recommend: bool = Field(default=True, description="是否推荐")
    would_work_again: bool = Field(default=True, description="是否再次合作")
    positive_tags: Optional[List[str]] = Field(None, description="正面标签")
    negative_tags: Optional[List[str]] = Field(None, description="负面标签")
    learning_objectives_met: Optional[int] = Field(None, ge=1, le=5, description="学习目标达成度")
    skill_improvement: Optional[int] = Field(None, ge=1, le=5, description="技能提升程度")
    is_public: bool = Field(default=True, description="是否公开")
    is_verified: bool = Field(default=False, description="是否验证")
    verification_notes: Optional[str] = Field(None, description="验证备注")


class MentorshipReviewCreate(MentorshipReviewBase):
    """创建导师评价"""
    pass


class MentorshipReviewUpdate(BaseModel):
    """更新导师评价"""
    comment: Optional[str] = None
    pros: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    would_recommend: Optional[bool] = None
    would_work_again: Optional[bool] = None
    positive_tags: Optional[List[str]] = None
    negative_tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class MentorshipReviewRead(MentorshipReviewBase):
    """导师评价读取模型"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MentorshipSessionBase(BaseModel):
    """导师会话基础模型"""
    relationship_id: int = Field(..., description="关系ID")
    session_number: int = Field(..., ge=1, description="会话编号")
    scheduled_at: datetime = Field(..., description="计划开始时间")
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, description="持续时长(分钟)")
    agenda: Optional[str] = Field(None, description="议程")
    status: SessionStatus = Field(default=SessionStatus.scheduled, description="会话状态")


class MentorshipSessionCreate(MentorshipSessionBase):
    """创建导师会话"""
    pass


class MentorshipSessionUpdate(BaseModel):
    """更新导师会话"""
    scheduled_at: Optional[datetime] = None
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    agenda: Optional[str] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None
    key_topics: Optional[List[str]] = None
    homework_assigned: Optional[str] = None
    next_session_plan: Optional[str] = None
    status: Optional[SessionStatus] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[datetime] = None
    mentor_satisfaction: Optional[int] = None
    mentee_satisfaction: Optional[int] = None
    mentor_feedback: Optional[str] = None
    mentee_feedback: Optional[str] = None
    progress_percentage: Optional[int] = None
    milestones_achieved: Optional[List[str]] = None


class MentorshipSessionRead(MentorshipSessionBase):
    """导师会话读取模型"""
    id: int
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None
    key_topics: Optional[List[str]] = None
    homework_assigned: Optional[str] = None
    resources_shared: Optional[List[str]] = None
    next_session_plan: Optional[str] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[datetime] = None
    mentor_satisfaction: Optional[int] = None
    mentee_satisfaction: Optional[int] = None
    mentor_feedback: Optional[str] = None
    mentee_feedback: Optional[str] = None
    progress_percentage: int = 0
    milestones_achieved: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MentorshipTransactionBase(BaseModel):
    """导师交易基础模型"""
    relationship_id: int = Field(..., description="关系ID")
    session_id: Optional[int] = Field(None, description="会话ID")
    transaction_type: TransactionType = Field(..., description="交易类型")
    amount: Decimal = Field(..., ge=0, description="金额")
    currency: str = Field(default="CNY", description="货币")
    payment_method: Optional[str] = Field(None, description="支付方式")
    payment_status: PaymentStatus = Field(default=PaymentStatus.pending, description="支付状态")
    external_transaction_id: Optional[str] = Field(None, description="外部交易ID")
    payment_gateway: Optional[str] = Field(None, description="支付网关")
    description: Optional[str] = Field(None, description="描述")
    reference_number: str = Field(..., description="参考编号")


class MentorshipTransactionCreate(MentorshipTransactionBase):
    """创建导师交易"""
    pass


class MentorshipTransactionUpdate(BaseModel):
    """更新导师交易"""
    payment_status: Optional[PaymentStatus] = None
    gateway_response: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None


class MentorshipTransactionRead(MentorshipTransactionBase):
    """导师交易读取模型"""
    id: int
    gateway_response: Optional[Dict[str, Any]] = None
    platform_fee_rate: float = 0.05
    platform_fee_amount: Decimal = Field(default=Decimal('0'), description="平台费用")
    mentor_amount: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class MentorshipDashboard(BaseModel):
    """导师关系仪表板"""
    active_relationships: int = 0
    completed_relationships: int = 0
    total_sessions: int = 0
    completed_sessions: int = 0
    total_earnings: Decimal = Field(default=Decimal('0'))
    average_rating: Optional[float] = None
    next_session: Optional[datetime] = None


class MentorshipStats(BaseModel):
    """导师统计信息"""
    total_relationships: int = 0
    active_relationships: int = 0
    completed_relationships: int = 0
    total_sessions: int = 0
    completed_sessions: int = 0
    total_hours: float = 0
    average_rating: Optional[float] = None
    total_earnings: Decimal = Field(default=Decimal('0'))
    success_rate: float = 0

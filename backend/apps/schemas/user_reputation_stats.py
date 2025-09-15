"""
用户声誉统计系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TrustLevel(str, Enum):
    """信任等级"""
    newcomer = "newcomer"
    learner = "learner"
    contributor = "contributor"
    mentor = "mentor"
    expert = "expert"
    master = "master"


class UserReputationStatsBase(BaseModel):
    """用户声誉统计基础模型"""
    user_id: int = Field(..., description="用户ID")
    mentor_rating_avg: Decimal = Field(default=Decimal('0'), ge=0, le=5, description="导师平均评分")
    mentor_rating_count: int = Field(default=0, ge=0, description="导师评分次数")
    mentor_relationships_total: int = Field(default=0, ge=0, description="导师关系总数")
    mentor_relationships_completed: int = Field(default=0, ge=0, description="导师关系完成数")
    mentor_sessions_completed: int = Field(default=0, ge=0, description="导师会话完成数")
    mentor_hours_taught: Decimal = Field(default=Decimal('0'), ge=0, description="导师教学时长")
    mentor_success_rate: Decimal = Field(default=Decimal('0'), ge=0, le=1, description="导师成功率")
    mentor_response_rate: Decimal = Field(default=Decimal('0'), ge=0, le=1, description="导师响应率")
    mentor_punctuality_rate: Decimal = Field(default=Decimal('0'), ge=0, le=1, description="导师准时率")
    mentee_rating_avg: Decimal = Field(default=Decimal('0'), ge=0, le=5, description="学员平均评分")
    mentee_rating_count: int = Field(default=0, ge=0, description="学员评分次数")
    mentee_relationships_total: int = Field(default=0, ge=0, description="学员关系总数")
    mentee_relationships_completed: int = Field(default=0, ge=0, description="学员关系完成数")
    mentee_sessions_attended: int = Field(default=0, ge=0, description="学员会话出席数")
    mentee_hours_learned: Decimal = Field(default=Decimal('0'), ge=0, description="学员学习时长")
    mentee_completion_rate: Decimal = Field(default=Decimal('0'), ge=0, le=1, description="学员完成率")
    mentee_attendance_rate: Decimal = Field(default=Decimal('0'), ge=0, le=1, description="学员出席率")
    reputation_score: int = Field(default=0, ge=0, description="声誉分数")
    trust_level: TrustLevel = Field(default=TrustLevel.newcomer, description="信任等级")
    last_active_as_mentor: Optional[datetime] = Field(None, description="最后作为导师活跃时间")
    last_active_as_mentee: Optional[datetime] = Field(None, description="最后作为学员活跃时间")


class UserReputationStatsCreate(UserReputationStatsBase):
    """创建用户声誉统计"""
    badges: Optional[List[str]] = Field(default=[], description="徽章列表")


class UserReputationStatsUpdate(BaseModel):
    """更新用户声誉统计"""
    mentor_rating_avg: Optional[Decimal] = None
    mentor_rating_count: Optional[int] = None
    mentor_relationships_total: Optional[int] = None
    mentor_relationships_completed: Optional[int] = None
    mentor_sessions_completed: Optional[int] = None
    mentor_hours_taught: Optional[Decimal] = None
    mentor_success_rate: Optional[Decimal] = None
    mentor_response_rate: Optional[Decimal] = None
    mentor_punctuality_rate: Optional[Decimal] = None
    mentee_rating_avg: Optional[Decimal] = None
    mentee_rating_count: Optional[int] = None
    mentee_relationships_total: Optional[int] = None
    mentee_relationships_completed: Optional[int] = None
    mentee_sessions_attended: Optional[int] = None
    mentee_hours_learned: Optional[Decimal] = None
    mentee_completion_rate: Optional[Decimal] = None
    mentee_attendance_rate: Optional[Decimal] = None
    reputation_score: Optional[int] = None
    trust_level: Optional[TrustLevel] = None
    badges: Optional[List[str]] = None
    last_active_as_mentor: Optional[datetime] = None
    last_active_as_mentee: Optional[datetime] = None


class UserReputationStatsRead(UserReputationStatsBase):
    """用户声誉统计读取模型"""
    badges: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserReputationStatsDetail(UserReputationStatsRead):
    """用户声誉统计详情"""
    username: Optional[str] = None
    user_avatar: Optional[str] = None
    user_role: Optional[str] = None


class ReputationBadge(BaseModel):
    """声誉徽章"""
    name: str
    description: str
    icon_url: Optional[str] = None
    earned_at: datetime


class ReputationMetrics(BaseModel):
    """声誉指标"""
    overall_score: int = 0
    mentor_score: int = 0
    mentee_score: int = 0
    badges: List[ReputationBadge] = []
    trust_level: TrustLevel
    level_progress: float = 0  # 0-1, 等级进度


class ReputationLeaderboard(BaseModel):
    """声誉排行榜"""
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    reputation_score: int
    trust_level: TrustLevel
    rank: int


class ReputationStatsSummary(BaseModel):
    """声誉统计摘要"""
    total_users: int = 0
    average_score: float = 0
    top_performers: List[ReputationLeaderboard] = []
    distribution: dict = {}  # 各等级用户分布

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


class MatchingFilter(BaseModel):
    """匹配筛选条件"""
    skill_ids: List[UUID] = Field(default_factory=list, description="技能ID列表")
    min_experience: Optional[int] = Field(None, ge=0, description="最小经验年限")
    max_hourly_rate: Optional[Decimal] = Field(None, ge=0, description="最高时薪")
    location: Optional[str] = Field(None, description="所在地")
    availability: Optional[str] = Field(None, description="可用性")


class RecommendationRequest(BaseModel):
    """推荐请求"""
    context: str = Field(..., description="推荐上下文：homepage, search, profile, service")
    limit: int = Field(10, ge=1, le=50, description="推荐数量")


class MatchingRequest(BaseModel):
    """匹配请求"""
    user_id: UUID = Field(..., description="发起匹配的用户ID")
    target_skills: List[UUID] = Field(..., description="目标技能ID列表")
    # Omitting other fields for brevity as they are domain-specific
    # and don't need refactoring with common models.


class MatchingResult(BaseModel):
    """匹配结果"""
    request_id: UUID = Field(..., description="请求ID")
    user_id: UUID = Field(..., description="用户ID")
    matches: List[dict] = Field(default_factory=list, description="匹配结果列表")  # This would contain mentor profiles and match scores
    total_matches: int = Field(0, description="总匹配数量")
    filters_applied: dict = Field(default_factory=dict, description="应用的筛选条件")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class MatchingHistory(IDModel, TimestampModel):
    """匹配历史记录"""
    user_id: UUID
    mentor_id: UUID
    match_score: float
    status: str = Field(...)

    class Config(IDModel.Config):
        from_attributes = True

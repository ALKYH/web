"""
用户技能系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class UserSkillBase(BaseModel):
    """用户技能基础模型"""
    user_id: int = Field(..., description="用户ID")
    skill_id: int = Field(..., description="技能ID")
    proficiency_level: int = Field(default=1, ge=1, le=5, description="熟练度等级(1-5)")
    years_experience: int = Field(default=0, ge=0, description="经验年数")
    can_mentor: bool = Field(default=False, description="是否可以指导")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="小时费率")
    currency: str = Field(default="CNY", description="货币类型")
    description: Optional[str] = Field(None, description="技能描述")
    verified: bool = Field(default=False, description="是否验证")
    is_active: bool = Field(default=True, description="是否激活")


class UserSkillCreate(UserSkillBase):
    """创建用户技能"""
    verified_by: Optional[int] = Field(None, description="验证者ID")


class UserSkillUpdate(BaseModel):
    """更新用户技能"""
    proficiency_level: Optional[int] = None
    years_experience: Optional[int] = None
    can_mentor: Optional[bool] = None
    hourly_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    verified: Optional[bool] = None
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class UserSkillRead(UserSkillBase):
    """用户技能读取模型"""
    id: int
    verified_at: Optional[datetime] = None
    verified_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserSkillDetail(UserSkillRead):
    """用户技能详情"""
    username: Optional[str] = None
    user_avatar: Optional[str] = None
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
    verified_by_username: Optional[str] = None


class UserSkillListResponse(BaseModel):
    """用户技能列表响应"""
    skills: List[UserSkillDetail]
    total: int
    has_next: bool


class SkillVerificationRequest(BaseModel):
    """技能验证请求"""
    skill_id: int = Field(..., description="技能ID")
    evidence_urls: Optional[List[str]] = Field(None, description="证据URL列表")
    notes: Optional[str] = Field(None, description="验证备注")


class SkillEndorsement(BaseModel):
    """技能认可"""
    user_id: int = Field(..., description="认可者ID")
    endorsement_text: Optional[str] = Field(None, description="认可文字")
    created_at: datetime


class UserSkillWithEndorsements(UserSkillDetail):
    """带有认可的用户技能"""
    endorsements: List[SkillEndorsement] = []
    endorsement_count: int = 0


class SkillStats(BaseModel):
    """技能统计"""
    total_users: int = 0
    verified_users: int = 0
    mentor_users: int = 0
    average_proficiency: float = 0
    average_hourly_rate: Optional[Decimal] = None
    popular_skills: List[dict] = []  # [{"skill_id": 1, "skill_name": "Python", "user_count": 50}]


class SkillSearchFilter(BaseModel):
    """技能搜索筛选器"""
    skill_categories: Optional[List[int]] = None
    proficiency_levels: Optional[List[int]] = None
    can_mentor: Optional[bool] = None
    verified_only: Optional[bool] = None
    price_range: Optional[dict] = None  # {"min": 50, "max": 200}
    experience_years: Optional[dict] = None  # {"min": 1, "max": 5}

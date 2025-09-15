"""
用户学习需求系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class LearningFormat(str, Enum):
    """学习格式"""
    online = "online"
    offline = "offline"
    hybrid = "hybrid"


class LearningDuration(str, Enum):
    """学习时长"""
    short_term = "short_term"  # 短期(1-3个月)
    medium_term = "medium_term"  # 中期(3-6个月)
    long_term = "long_term"  # 长期(6个月以上)


class UserLearningNeedBase(BaseModel):
    """用户学习需求基础模型"""
    user_id: int = Field(..., description="用户ID")
    skill_id: int = Field(..., description="技能ID")
    urgency_level: int = Field(default=1, ge=1, le=5, description="紧急程度(1-5)")
    budget_min: Optional[Decimal] = Field(None, ge=0, description="预算下限")
    budget_max: Optional[Decimal] = Field(None, ge=0, description="预算上限")
    currency: str = Field(default="CNY", description="货币类型")
    preferred_format: LearningFormat = Field(default=LearningFormat.online, description="偏好格式")
    preferred_duration: Optional[LearningDuration] = Field(None, description="偏好时长")
    description: Optional[str] = Field(None, description="需求描述")
    learning_goals: Optional[str] = Field(None, description="学习目标")
    current_level: int = Field(default=1, ge=1, le=5, description="当前水平(1-5)")
    target_level: int = Field(default=2, ge=1, le=5, description="目标水平(1-5)")
    is_active: bool = Field(default=True, description="是否激活")


class UserLearningNeedCreate(UserLearningNeedBase):
    """创建用户学习需求"""
    pass


class UserLearningNeedUpdate(BaseModel):
    """更新用户学习需求"""
    urgency_level: Optional[int] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    currency: Optional[str] = None
    preferred_format: Optional[LearningFormat] = None
    preferred_duration: Optional[LearningDuration] = None
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    current_level: Optional[int] = None
    target_level: Optional[int] = None
    is_active: Optional[bool] = None


class UserLearningNeedRead(UserLearningNeedBase):
    """用户学习需求读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserLearningNeedDetail(UserLearningNeedRead):
    """用户学习需求详情"""
    username: Optional[str] = None
    user_avatar: Optional[str] = None
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
    matching_mentors_count: int = 0


class UserLearningNeedListResponse(BaseModel):
    """用户学习需求列表响应"""
    needs: List[UserLearningNeedDetail]
    total: int
    has_next: bool


class LearningNeedStats(BaseModel):
    """学习需求统计"""
    total_needs: int = 0
    active_needs: int = 0
    expired_needs: int = 0
    average_budget: Optional[Decimal] = None
    popular_skills: List[dict] = []  # [{"skill_id": 1, "skill_name": "Python", "count": 10}]


class LearningNeedFilter(BaseModel):
    """学习需求筛选器"""
    skill_categories: Optional[List[int]] = None
    urgency_levels: Optional[List[int]] = None
    budget_range: Optional[dict] = None  # {"min": 100, "max": 1000}
    preferred_formats: Optional[List[LearningFormat]] = None
    current_level_range: Optional[dict] = None  # {"min": 1, "max": 3}
    target_level_range: Optional[dict] = None  # {"min": 2, "max": 4}
    is_active: Optional[bool] = None

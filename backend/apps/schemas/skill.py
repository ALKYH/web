"""
技能中心 - 数据模型
"""
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 技能分类 (SkillCategory) ============
class SkillCategoryBase(BaseModel):
    """技能分类基础模型"""

    name: str = Field(..., max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")


class SkillCategoryCreate(SkillCategoryBase):
    """技能分类创建模型"""

    pass


class SkillCategoryUpdate(BaseModel):
    """技能分类更新模型"""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class SkillCategory(IDModel, TimestampModel, SkillCategoryBase):
    """技能分类完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 技能 (Skill) ============
class SkillBase(BaseModel):
    """技能基础模型"""

    name: str = Field(..., max_length=100, description="技能名称")
    category_id: UUID = Field(..., description="所属分类ID")


class SkillCreate(SkillBase):
    """技能创建模型"""

    pass


class SkillUpdate(BaseModel):
    """技能更新模型"""

    name: Optional[str] = Field(None, max_length=100)
    category_id: Optional[UUID] = None


class Skill(IDModel, TimestampModel, SkillBase):
    """技能完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 用户技能 (UserSkill) ============
class UserSkillBase(BaseModel):
    """用户技能基础模型"""

    user_id: UUID = Field(..., description="用户ID")
    skill_id: UUID = Field(..., description="技能ID")
    proficiency_level: int = Field(1, ge=1, le=5, description="熟练度 (1-5)")
    years_experience: int = Field(0, ge=0, description="经验年限")


class UserSkillCreate(UserSkillBase):
    """用户技能创建模型"""

    pass


class UserSkillUpdate(BaseModel):
    """用户技能更新模型"""

    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    years_experience: Optional[int] = Field(None, ge=0)


class UserSkill(IDModel, TimestampModel, UserSkillBase):
    """用户技能完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 导师技能/服务 (MentorSkill) ============
class MentorSkillBase(BaseModel):
    """导师技能/服务基础模型"""

    user_skill_id: UUID = Field(..., description="关联的用户技能ID")
    can_mentor: bool = Field(False, description="是否可提供指导")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="时薪 (CNY)")
    description: Optional[str] = Field(None, description="服务描述")
    is_active: bool = Field(True, description="是否激活")


class MentorSkillCreate(MentorSkillBase):
    """导师技能/服务创建模型"""

    pass


class MentorSkillUpdate(BaseModel):
    """导师技能/服务更新模型"""

    can_mentor: Optional[bool] = None
    hourly_rate: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MentorSkill(IDModel, TimestampModel, MentorSkillBase):
    """导师技能/服务完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 技能认可 (SkillEndorsement) ============

class SkillEndorsementBase(BaseModel):
    """技能认可基础模型"""

    user_skill_id: UUID = Field(..., description="被认可的用户技能ID")
    endorser_id: UUID = Field(..., description="认可者用户ID")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分 (1-5)")
    comment: Optional[str] = Field(None, max_length=500, description="认可评论")


class SkillEndorsementCreate(SkillEndorsementBase):
    """技能认可创建模型"""

    pass


class SkillEndorsementUpdate(BaseModel):
    """技能认可更新模型"""

    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class SkillEndorsement(IDModel, TimestampModel, SkillEndorsementBase):
    """技能认可完整模型"""

    class Config(IDModel.Config):
        from_attributes = True

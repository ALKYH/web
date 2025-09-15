"""
技能系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillCategoryBase(BaseModel):
    """技能分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon_url: Optional[str] = Field(None, description="图标URL")
    sort_order: int = Field(default=0, description="排序顺序")
    is_active: bool = Field(default=True, description="是否激活")


class SkillCategoryCreate(SkillCategoryBase):
    """创建技能分类"""
    pass


class SkillCategoryUpdate(BaseModel):
    """更新技能分类"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class SkillCategoryRead(SkillCategoryBase):
    """技能分类读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class SkillBase(BaseModel):
    """技能基础模型"""
    category_id: int = Field(..., description="分类ID")
    name: str = Field(..., min_length=1, max_length=100, description="技能名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    description: Optional[str] = Field(None, description="技能描述")
    difficulty_level: int = Field(default=1, ge=1, le=5, description="难度等级(1-5)")
    sort_order: int = Field(default=0, description="排序顺序")
    is_active: bool = Field(default=True, description="是否激活")


class SkillCreate(SkillBase):
    """创建技能"""
    pass


class SkillUpdate(BaseModel):
    """更新技能"""
    category_id: Optional[int] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class SkillRead(SkillBase):
    """技能读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class SkillDetail(SkillRead):
    """技能详情"""
    category_name: Optional[str] = None
    category_name_en: Optional[str] = None
    mentor_count: int = 0
    average_rating: Optional[float] = None


class SkillCategoryDetail(SkillCategoryRead):
    """技能分类详情"""
    skills: List[SkillDetail] = []
    skill_count: int = 0


class SkillListResponse(BaseModel):
    """技能列表响应"""
    skills: List[SkillDetail]
    total: int
    has_next: bool


class SkillCategoryListResponse(BaseModel):
    """技能分类列表响应"""
    categories: List[SkillCategoryDetail]
    total: int

"""
用户中心 - 统一数据模型
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .common import IDModel, TimestampModel


# ============ 用户核心模型 ============
class UserBase(BaseModel):
    """用户基础模型，包含通用字段"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    role: str = Field("user", description="用户角色: user, student, mentor, admin")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    is_active: bool = Field(True, description="账户是否激活")


class UserCreate(UserBase):
    """用户创建模型"""

    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    """用户更新模型，所有字段可选"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class User(IDModel, TimestampModel, UserBase):
    """用户完整模型，用于API响应和数据库记录"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 用户画像模型 (Profile) ============
class ProfileBase(BaseModel):
    """用户画像基础模型"""

    bio: Optional[str] = Field(None, description="个人简介")
    location: Optional[str] = Field(None, max_length=100, description="所在地")
    website: Optional[str] = Field(None, description="个人网站")
    birth_date: Optional[date] = Field(None, description="出生日期")


class StudentProfile(ProfileBase):
    """学生特定画像字段"""

    urgency_level: Optional[int] = Field(None, ge=1, le=5, description="紧急程度 (1-5)")
    budget_min: Optional[Decimal] = Field(None, ge=0, description="最小预算")
    budget_max: Optional[Decimal] = Field(None, ge=0, description="最大预算")
    learning_goals: Optional[str] = Field(None, description="学习目标")


class MentorProfile(ProfileBase):
    """导师特定画像字段"""

    title: Optional[str] = Field(None, description="导师标题/职位")
    expertise: List[str] = Field(default_factory=list, description="专业领域")
    experience_years: Optional[int] = Field(None, ge=0, description="经验年限")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="时薪 (CNY)")


class ProfileUpdate(StudentProfile, MentorProfile):
    """
    统一的用户画像更新模型
    允许一次性更新学生和导师的所有可选字段
    """

    pass


class Profile(IDModel, TimestampModel, StudentProfile, MentorProfile):
    """统一的用户画像完整模型"""

    user_id: str = Field(..., description="关联的用户ID")

    class Config(IDModel.Config):
        from_attributes = True


# ============ 认证相关模型 ============
class UserLogin(BaseModel):
    """用户登录请求模型"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
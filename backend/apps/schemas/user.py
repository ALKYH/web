"""
用户相关的数据模型
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date


class UserBase(BaseModel):
    """用户基础数据模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")


class UserCreate(UserBase):
    """用户创建数据模型"""
    password: str = Field(..., min_length=6, description="密码")
    role: Optional[str] = Field(default="user", description="用户角色: user, student, mentor, admin")
    # 与数据库一致：users 表存储 password_hash，不直接暴露；此处维持输入密码


class UserUpdate(BaseModel):
    """用户更新数据模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    """用户登录数据模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserRead(UserBase):
    """用户读取数据模型"""
    id: int
    role: str = Field(default="user", description="用户角色")
    is_active: bool = Field(default=True, description="用户是否激活")  # 数据库可空，默认 true
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class ProfileBase(BaseModel):
    """用户资料基础数据模型 - 匹配 profiles 表"""
    user_id: int = Field(..., description="用户ID")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    location: Optional[str] = Field(None, max_length=100, description="所在地")
    website: Optional[str] = Field(None, description="个人网站")
    birth_date: Optional[date] = Field(None, description="出生日期")


class ProfileCreate(ProfileBase):
    """创建用户资料"""
    pass


class ProfileUpdate(BaseModel):
    """用户资料更新数据模型"""
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None
    birth_date: Optional[date] = None


class ProfileRead(ProfileBase):
    """用户资料读取数据模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProfileDetail(ProfileRead):
    """用户资料详情"""
    username: str
    email: Optional[str] = None
    role: str
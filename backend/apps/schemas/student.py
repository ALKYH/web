from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class StudentBase(BaseModel):
    """申请者基础模型 - 匹配 user_learning_needs 表"""
    urgency_level: Optional[int] = Field(default=1, ge=1, le=5, description="紧急程度1-5")
    budget_min: Optional[Decimal] = Field(None, ge=0, description="最小预算")  # numeric 类型
    budget_max: Optional[Decimal] = Field(None, ge=0, description="最大预算")  # numeric 类型
    description: Optional[str] = Field(None, description="学习需求描述")  # 可空
    learning_goals: Optional[str] = Field(None, description="学习目标")  # 可空
    preferred_format: Optional[str] = Field(default="online", description="偏好形式")  # 可空
    
class StudentProfile(StudentBase):
    """完整的申请者资料 - 匹配 user_learning_needs 表"""
    id: int
    user_id: Optional[int] = None  # 可空，与数据库一致
    skill_id: Optional[int] = None
    currency: Optional[str] = Field(default="CNY", description="货币类型")  # 可空
    preferred_duration: Optional[str] = None  # varchar 类型，与数据库一致
    current_level: Optional[int] = Field(default=1, description="当前水平")  # 可空
    target_level: Optional[int] = Field(default=2, description="目标水平")  # 可空
    is_active: Optional[bool] = Field(default=True, description="是否激活")  # 可空
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None  # 可空，与数据库一致
    updated_at: Optional[datetime] = None  # 可空，与数据库一致
    
    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    """更新申请者资料"""
    urgency_level: Optional[int] = None
    budget_min: Optional[Decimal] = None  # numeric 类型
    budget_max: Optional[Decimal] = None  # numeric 类型
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    preferred_format: Optional[str] = None
    preferred_duration: Optional[str] = None  # varchar 类型
    current_level: Optional[int] = None
    target_level: Optional[int] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None

class StudentCreate(StudentBase):
    """创建申请者资料"""
    user_id: Optional[int] = None
    skill_id: Optional[int] = None
    currency: Optional[str] = Field(default="CNY")
    preferred_duration: Optional[str] = None
    current_level: Optional[int] = Field(default=1)
    target_level: Optional[int] = Field(default=2)
    is_active: Optional[bool] = Field(default=True)

class StudentPublic(BaseModel):
    """公开的申请者信息"""
    id: int
    user_id: Optional[int] = None  # 可空，与数据库一致
    description: Optional[str] = None  # 可空
    learning_goals: Optional[str] = None  # 可空
    urgency_level: Optional[int] = None  # 可空
    preferred_format: Optional[str] = None  # 可空
    
    class Config:
        from_attributes = True
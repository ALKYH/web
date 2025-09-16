"""
通用工具 - 数据模型
"""
from datetime import date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 文件上传 (UploadedFile) ============
class UploadedFileBase(BaseModel):
    """上传文件基础模型"""
    user_id: UUID = Field(..., description="上传用户ID")
    file_path: str = Field(..., description="文件存储路径")
    file_url: str = Field(..., description="文件访问URL")
    original_filename: str = Field(..., description="原始文件名")
    content_type: str = Field(..., description="文件MIME类型")
    file_size: int = Field(..., ge=0, description="文件大小（字节）")


class UploadedFileCreate(UploadedFileBase):
    """上传文件创建模型"""
    pass


class UploadedFile(IDModel, TimestampModel, UploadedFileBase):
    """上传文件完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 用户可用时间 (UserAvailability) ============
class UserAvailabilityBase(BaseModel):
    """用户常规可用时间基础模型"""
    user_id: UUID = Field(..., description="用户ID")
    day_of_week: int = Field(..., ge=0, le=6, description="星期几 (0=Sunday, 6=Saturday)")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")


class UserAvailabilityCreate(UserAvailabilityBase):
    """用户可用时间创建模型"""
    pass


class UserAvailabilityUpdate(BaseModel):
    """用户可用时间更新模型"""
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class UserAvailability(IDModel, TimestampModel, UserAvailabilityBase):
    """用户可用时间完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 用户不可用时段 (UnavailablePeriod) ============
class UnavailablePeriodBase(BaseModel):
    """用户特定不可用时段基础模型"""
    user_id: UUID = Field(..., description="用户ID")
    start_datetime: date = Field(..., description="开始日期时间")
    end_datetime: date = Field(..., description="结束日期时间")
    reason: Optional[str] = Field(None, description="不可用原因")


class UnavailablePeriodCreate(UnavailablePeriodBase):
    """用户不可用时段创建模型"""
    pass


class UnavailablePeriodUpdate(BaseModel):
    """用户不可用时段更新模型"""
    start_datetime: Optional[date] = None
    end_datetime: Optional[date] = None
    reason: Optional[str] = None


class UnavailablePeriod(IDModel, TimestampModel, UnavailablePeriodBase):
    """用户不可用时段完整模型"""
    class Config(IDModel.Config):
        from_attributes = True

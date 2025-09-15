"""
文件上传系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UploadedFileBase(BaseModel):
    """上传文件基础模型"""
    user_id: int = Field(..., description="用户ID")
    filename: str = Field(..., min_length=1, max_length=255, description="文件名")
    original_filename: str = Field(..., min_length=1, max_length=255, description="原始文件名")
    file_path: str = Field(..., min_length=1, description="文件路径")
    file_url: str = Field(..., min_length=1, description="文件URL")
    file_size: int = Field(..., ge=0, description="文件大小(字节)")
    content_type: str = Field(..., min_length=1, max_length=100, description="内容类型")
    file_type: str = Field(..., min_length=1, max_length=50, description="文件类型")
    description: Optional[str] = Field(None, description="文件描述")


class UploadedFileCreate(UploadedFileBase):
    """创建上传文件"""
    pass


class UploadedFileUpdate(BaseModel):
    """更新上传文件"""
    filename: Optional[str] = None
    description: Optional[str] = None


class UploadedFileRead(UploadedFileBase):
    """上传文件读取模型"""
    id: int
    file_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UploadedFileDetail(UploadedFileRead):
    """上传文件详情"""
    user_username: Optional[str] = None
    user_avatar: Optional[str] = None


class UploadedFileListResponse(BaseModel):
    """上传文件列表响应"""
    files: List[UploadedFileDetail]
    total: int
    total_size: int = 0
    has_next: bool


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: UUID
    file_url: str
    filename: str
    file_size: int
    content_type: str


class FileTypeStats(BaseModel):
    """文件类型统计"""
    file_type: str
    count: int
    total_size: int

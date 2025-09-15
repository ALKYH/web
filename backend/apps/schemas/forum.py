"""
论坛系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ForumPostBase(BaseModel):
    """论坛帖子基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="帖子标题")
    content: str = Field(..., min_length=1, description="帖子内容")
    category: str = Field(..., min_length=1, max_length=50, description="帖子分类")
    tags: Optional[List[str]] = Field(default=[], description="标签数组")
    is_anonymous: Optional[bool] = Field(default=False, description="是否匿名发布")


class ForumPostCreate(ForumPostBase):
    """创建论坛帖子"""
    pass


class ForumPostUpdate(BaseModel):
    """更新论坛帖子"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_hot: Optional[bool] = None


class ForumPostRead(ForumPostBase):
    """论坛帖子读取模型"""
    id: int
    author_id: int
    replies_count: int = 0
    likes_count: int = 0
    views_count: int = 0
    is_pinned: bool = False
    is_hot: bool = False
    created_at: datetime
    updated_at: datetime
    last_activity: datetime

    model_config = {
        "from_attributes": True
    }


class ForumPostDetail(ForumPostRead):
    """论坛帖子详情"""
    author_username: Optional[str] = None
    author_avatar: Optional[str] = None
    is_liked_by_user: Optional[bool] = None


class ForumReplyBase(BaseModel):
    """论坛回复基础模型"""
    post_id: int = Field(..., description="帖子ID")
    content: str = Field(..., min_length=1, description="回复内容")
    parent_id: Optional[int] = Field(None, description="父回复ID")
    parent_reply_id: Optional[int] = Field(None, description="父回复ID")


class ForumReplyCreate(ForumReplyBase):
    """创建论坛回复"""
    pass


class ForumReplyUpdate(BaseModel):
    """更新论坛回复"""
    content: Optional[str] = Field(None, min_length=1)


class ForumReplyRead(ForumReplyBase):
    """论坛回复读取模型"""
    id: int
    author_id: int
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ForumReplyDetail(ForumReplyRead):
    """论坛回复详情"""
    author_username: Optional[str] = None
    author_avatar: Optional[str] = None
    is_liked_by_user: Optional[bool] = None
    child_replies: List['ForumReplyDetail'] = []


class ForumLikeBase(BaseModel):
    """论坛点赞基础模型"""
    user_id: int = Field(..., description="用户ID")
    post_id: Optional[int] = Field(None, description="帖子ID")
    reply_id: Optional[int] = Field(None, description="回复ID")


class ForumLikeCreate(ForumLikeBase):
    """创建论坛点赞"""
    pass


class ForumLikeRead(ForumLikeBase):
    """论坛点赞读取模型"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ForumReplyLikeBase(BaseModel):
    """论坛回复点赞基础模型"""
    reply_id: int = Field(..., description="回复ID")
    user_id: int = Field(..., description="用户ID")


class ForumReplyLikeCreate(ForumReplyLikeBase):
    """创建论坛回复点赞"""
    pass


class ForumReplyLikeRead(ForumReplyLikeBase):
    """论坛回复点赞读取模型"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ForumPostListResponse(BaseModel):
    """论坛帖子列表响应"""
    posts: List[ForumPostDetail]
    total: int
    has_next: bool


class ForumReplyListResponse(BaseModel):
    """论坛回复列表响应"""
    replies: List[ForumReplyDetail]
    total: int
    has_next: bool


class ForumCategoryStats(BaseModel):
    """论坛分类统计"""
    category: str
    post_count: int
    reply_count: int
    last_activity: Optional[datetime] = None

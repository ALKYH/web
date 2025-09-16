"""
论坛中心 - 数据模型
"""
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 论坛帖子 (ForumPost) ============
class ForumPostBase(BaseModel):
    """论坛帖子基础模型"""
    author_id: UUID = Field(..., description="作者ID")
    title: str = Field(..., min_length=1, max_length=200, description="帖子标题")
    content: str = Field(..., min_length=1, description="帖子内容")
    category: str = Field(..., max_length=50, description="帖子分类")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class ForumPostCreate(ForumPostBase):
    """论坛帖子创建模型"""
    pass


class ForumPostUpdate(BaseModel):
    """论坛帖子更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None


class ForumPost(IDModel, TimestampModel, ForumPostBase):
    """论坛帖子完整模型"""
    views_count: int = Field(0, description="浏览次数")

    class Config(IDModel.Config):
        from_attributes = True


# ============ 帖子回复 (PostReply) ============
class PostReplyBase(BaseModel):
    """帖子回复基础模型"""
    post_id: UUID = Field(..., description="所属帖子ID")
    author_id: UUID = Field(..., description="回复者ID")
    content: str = Field(..., min_length=1, description="回复内容")
    parent_reply_id: Optional[UUID] = Field(None, description="父回复ID，用于嵌套回复")


class PostReplyCreate(PostReplyBase):
    """帖子回复创建模型"""
    pass


class PostReplyUpdate(BaseModel):
    """帖子回复更新模型"""
    content: Optional[str] = Field(None, min_length=1)


class PostReply(IDModel, TimestampModel, PostReplyBase):
    """帖子回复完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 点赞 (Like) ============
class LikeBase(BaseModel):
    """点赞基础模型"""
    user_id: UUID = Field(..., description="点赞用户ID")
    post_id: Optional[UUID] = Field(None, description="被点赞的帖子ID")
    reply_id: Optional[UUID] = Field(None, description="被点赞的回复ID")


class LikeCreate(LikeBase):
    """点赞创建模型"""
    pass


class Like(IDModel, TimestampModel, LikeBase):
    """点赞完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 复合响应模型 ============
class ForumPostDetail(ForumPost):
    """论坛帖子详情模型（包含作者信息）"""
    author_name: Optional[str] = Field(None, description="作者姓名")
    author_avatar: Optional[str] = Field(None, description="作者头像")
    reply_count: int = Field(0, description="回复数量")
    like_count: int = Field(0, description="点赞数量")


class ForumReplyDetail(PostReply):
    """帖子回复详情模型（包含作者信息）"""
    author_name: Optional[str] = Field(None, description="作者姓名")
    author_avatar: Optional[str] = Field(None, description="作者头像")
    like_count: int = Field(0, description="点赞数量")


class ForumPostListResponse(BaseModel):
    """论坛帖子列表响应"""
    posts: List[ForumPostDetail] = Field(default_factory=list, description="帖子列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页")
    page_size: int = Field(10, description="每页数量")


class ForumReplyListResponse(BaseModel):
    """帖子回复列表响应"""
    replies: List[ForumReplyDetail] = Field(default_factory=list, description="回复列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页")
    page_size: int = Field(10, description="每页数量")

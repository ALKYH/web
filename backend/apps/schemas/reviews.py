"""
评价系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewBase(BaseModel):
    """评价基础模型 - 匹配 reviews 表"""
    order_id: int = Field(..., description="订单ID")
    reviewer_id: int = Field(..., description="评价者ID")
    rating: int = Field(..., ge=1, le=5, description="评分(1-5)")
    comment: Optional[str] = Field(None, description="评价内容")


class ReviewCreate(ReviewBase):
    """创建评价"""
    pass


class ReviewUpdate(BaseModel):
    """更新评价"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewRead(ReviewBase):
    """评价读取模型"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ReviewDetail(ReviewRead):
    """评价详情"""
    reviewer_username: Optional[str] = None
    reviewer_avatar: Optional[str] = None
    order_title: Optional[str] = None
    service_title: Optional[str] = None


class ReviewListResponse(BaseModel):
    """评价列表响应"""
    reviews: List[ReviewDetail]
    total: int
    average_rating: float = 0
    has_next: bool


class ReviewStats(BaseModel):
    """评价统计"""
    total_reviews: int = 0
    average_rating: float = 0
    rating_distribution: dict = {}  # {1: 5, 2: 10, 3: 20, 4: 15, 5: 30}

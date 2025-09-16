"""
匹配相关的 API 路由
包括智能推荐、筛选、匹配历史等功能
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from apps.api.v1.deps import get_current_user, require_student_role, get_database, AuthenticatedUser
from apps.schemas.matching import (
    MatchingRequest, MatchingFilter, RecommendationRequest, MatchingResult, MatchingHistory
)
from apps.schemas.common import GeneralResponse
from apps.api.v1.services import matching as matching_service
from libs.database.adapters import DatabaseAdapter

router = APIRouter()


@router.post(
    "/recommend",
    response_model=GeneralResponse[MatchingResult],
    summary="基于需求推荐指导者",
    description="基于申请者的具体需求智能推荐匹配的指导者"
)
async def recommend_mentors(
    request: MatchingRequest,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """基于需求推荐指导者"""
    result = await matching_service.recommend_mentors(db, current_user.id, request)
    return GeneralResponse(data=result)


@router.get(
    "/filters",
    response_model=GeneralResponse[dict],
    summary="获取筛选条件",
    description="获取所有可用的筛选条件（学校/专业列表等）"
)
async def get_filters(
    db: DatabaseAdapter = Depends(get_database)
):
    """获取筛选条件"""
    filters = await matching_service.get_filters(db)
    return GeneralResponse(data=filters)


@router.post(
    "/filter",
    response_model=GeneralResponse[List[dict]],
    summary="高级筛选指导者",
    description="使用高级筛选条件查找指导者"
)
async def filter_mentors(
    filters: MatchingFilter,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """高级筛选指导者"""
    mentors = await matching_service.filter_mentors(db, filters, limit, offset)
    return GeneralResponse(data=mentors)


@router.get(
    "/history",
    response_model=GeneralResponse[List[MatchingHistory]],
    summary="查看匹配历史",
    description="查看申请者的匹配历史记录"
)
async def get_matching_history(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """查看匹配历史"""
    history = await matching_service.get_matching_history(db, current_user.id, limit)
    return GeneralResponse(data=history)


@router.post(
    "/recommendations",
    response_model=GeneralResponse[dict],
    summary="上下文推荐",
    description="根据不同上下文（首页/搜索/个人资料/服务）获取推荐"
)
async def get_contextual_recommendations(
    request: RecommendationRequest,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """上下文推荐"""
    recommendations = await matching_service.get_contextual_recommendations(db, request, current_user.id)
    return GeneralResponse(data=recommendations)


@router.get(
    "/popular",
    response_model=GeneralResponse[List[dict]],
    summary="热门指导者",
    description="获取平台上最受欢迎的指导者"
)
async def get_popular_mentors(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    exclude_ids: Optional[List[int]] = Query(None, description="排除的指导者ID"),
    db: DatabaseAdapter = Depends(get_database)
):
    """获取热门指导者"""
    mentors = await matching_service.get_popular_mentors(db, limit, exclude_ids)
    return GeneralResponse(data=mentors)


@router.get(
    "/similar",
    response_model=GeneralResponse[List[dict]],
    summary="相似背景推荐",
    description="基于申请者背景推荐相似经历的指导者"
)
async def get_similar_background_mentors(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    exclude_ids: Optional[List[int]] = Query(None, description="排除的指导者ID"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """相似背景推荐"""
    mentors = await matching_service.get_similar_background_mentors(db, current_user.id, limit, exclude_ids)
    return GeneralResponse(data=mentors)


@router.get(
    "/by-service",
    response_model=GeneralResponse[List[dict]],
    summary="服务相关推荐",
    description="基于特定服务类型推荐指导者"
)
async def get_service_related_mentors(
    service_category: str = Query(..., description="服务分类"),
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    exclude_ids: Optional[List[int]] = Query(None, description="排除的指导者ID"),
    db: DatabaseAdapter = Depends(get_database)
):
    """服务相关推荐"""
    preferences = {"service_category": service_category}
    mentors = await matching_service.get_service_related_mentors(db, preferences, limit, exclude_ids)
    return GeneralResponse(data=mentors)
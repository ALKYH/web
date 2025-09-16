"""
导师制 & 服务 - API 路由
包括服务发布、管理和导师关系处理
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from apps.api.v1.deps import (
    get_current_user,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.mentorship import (
    Service, ServiceCreate, ServiceUpdate,
    Mentorship, MentorshipCreate, MentorshipUpdate,
    Session, SessionCreate, SessionUpdate,
    Review, ReviewCreate, ReviewUpdate
)
from apps.schemas.common import GeneralResponse, PaginatedResponse
from apps.api.v1.services import mentorship as mentorship_service

router = APIRouter()


# ============ 服务管理 ============

@router.get(
    "/services",
    response_model=GeneralResponse[List[Service]],
    summary="浏览指导服务",
    description="浏览平台上的所有可用指导服务"
)
async def list_services(
    skill_id: Optional[UUID] = Query(None, description="技能ID筛选"),
    mentor_id: Optional[UUID] = Query(None, description="导师ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[List[Service]]:
    """
    浏览指导服务列表
    """
    services = await mentorship_service.get_services(
        db=db,
        skill_id=skill_id,
        mentor_id=mentor_id,
        page=page,
        page_size=page_size
    )
    return GeneralResponse(data=services)


@router.post(
    "/services",
    response_model=GeneralResponse[Service],
    summary="发布指导服务",
    description="导师发布新的指导服务"
)
async def create_service(
    service_data: ServiceCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Service]:
    """
    创建指导服务
    """
    service = await mentorship_service.create_service(
        db=db,
        user_id=current_user.id,
        service_data=service_data
    )
    if not service:
        raise HTTPException(status_code=400, detail="创建服务失败")

    return GeneralResponse(data=service)


@router.get(
    "/services/{service_id}",
    response_model=GeneralResponse[Service],
    summary="获取服务详情",
    description="获取指定服务的详细信息"
)
async def get_service(
    service_id: UUID,
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Service]:
    """
    获取服务详情
    """
    service = await mentorship_service.get_service_by_id(
        db=db,
        service_id=service_id
    )
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")

    return GeneralResponse(data=service)


@router.put(
    "/services/{service_id}",
    response_model=GeneralResponse[Service],
    summary="更新服务信息",
    description="导师更新自己的服务信息"
)
async def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Service]:
    """
    更新服务信息
    """
    service = await mentorship_service.update_service(
        db=db,
        service_id=service_id,
        user_id=current_user.id,
        service_data=service_data
    )
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在或无权限")

    return GeneralResponse(data=service)


@router.delete(
    "/services/{service_id}",
    response_model=GeneralResponse[dict],
    summary="删除服务",
    description="导师删除自己的服务"
)
async def delete_service(
    service_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[dict]:
    """
    删除服务
    """
    success = await mentorship_service.delete_service(
        db=db,
        service_id=service_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="服务不存在或无权限")

    return GeneralResponse(data={"message": "服务已删除"})


@router.get(
    "/my/services",
    response_model=GeneralResponse[List[Service]],
    summary="获取我的服务",
    description="获取当前用户发布的所有服务"
)
async def get_my_services(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[List[Service]]:
    """
    获取我的服务
    """
    services = await mentorship_service.get_services_by_mentor(
        db=db,
        mentor_id=current_user.id
    )
    return GeneralResponse(data=services)


# ============ 导师关系管理 ============

@router.post(
    "/mentorships",
    response_model=GeneralResponse[Mentorship],
    summary="申请导师关系",
    description="学员申请与导师建立指导关系"
)
async def create_mentorship(
    mentorship_data: MentorshipCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Mentorship]:
    """
    创建导师关系申请
    """
    mentorship = await mentorship_service.create_mentorship(
        db=db,
        mentorship_data=mentorship_data
    )
    if not mentorship:
        raise HTTPException(status_code=400, detail="创建导师关系失败")

    return GeneralResponse(data=mentorship)


@router.get(
    "/mentorships/{mentorship_id}",
    response_model=GeneralResponse[Mentorship],
    summary="获取导师关系详情",
    description="获取指定导师关系的详细信息"
)
async def get_mentorship(
    mentorship_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Mentorship]:
    """
    获取导师关系详情
    """
    mentorship = await mentorship_service.get_mentorship(
        db=db,
        mentorship_id=mentorship_id,
        user_id=current_user.id
    )
    if not mentorship:
        raise HTTPException(status_code=404, detail="导师关系不存在或无权限")

    return GeneralResponse(data=mentorship)


@router.put(
    "/mentorships/{mentorship_id}",
    response_model=GeneralResponse[Mentorship],
    summary="更新导师关系状态",
    description="导师或学员更新导师关系的状态"
)
async def update_mentorship(
    mentorship_id: UUID,
    mentorship_data: MentorshipUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Mentorship]:
    """
    更新导师关系状态
    """
    mentorship = await mentorship_service.update_mentorship(
        db=db,
        mentorship_id=mentorship_id,
        user_id=current_user.id,
        mentorship_data=mentorship_data
    )
    if not mentorship:
        raise HTTPException(status_code=404, detail="导师关系不存在或无权限")

    return GeneralResponse(data=mentorship)


# ============ 会话管理 ============

@router.post(
    "/sessions",
    response_model=GeneralResponse[Session],
    summary="创建会话",
    description="为导师关系创建新的会话"
)
async def create_session(
    session_data: SessionCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Session]:
    """
    创建会话
    """
    session = await mentorship_service.create_session(
        db=db,
        session_data=session_data,
        user_id=current_user.id
    )
    if not session:
        raise HTTPException(status_code=400, detail="创建会话失败")

    return GeneralResponse(data=session)


@router.get(
    "/sessions/{session_id}",
    response_model=GeneralResponse[Session],
    summary="获取会话详情",
    description="获取指定会话的详细信息"
)
async def get_session(
    session_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Session]:
    """
    获取会话详情
    """
    session = await mentorship_service.get_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或无权限")

    return GeneralResponse(data=session)


@router.put(
    "/sessions/{session_id}",
    response_model=GeneralResponse[Session],
    summary="更新会话信息",
    description="更新会话信息和状态"
)
async def update_session(
    session_id: UUID,
    session_data: SessionUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Session]:
    """
    更新会话信息
    """
    session = await mentorship_service.update_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        session_data=session_data
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或无权限")

    return GeneralResponse(data=session)


# ============ 评价管理 ============

@router.post(
    "/reviews",
    response_model=GeneralResponse[Review],
    summary="创建评价",
    description="为完成的导师关系创建评价"
)
async def create_review(
    review_data: ReviewCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Review]:
    """
    创建评价
    """
    review = await mentorship_service.create_review(
        db=db,
        review_data=review_data,
        reviewer_id=current_user.id
    )
    if not review:
        raise HTTPException(status_code=400, detail="创建评价失败")

    return GeneralResponse(data=review)


@router.get(
    "/reviews/{review_id}",
    response_model=GeneralResponse[Review],
    summary="获取评价详情",
    description="获取指定评价的详细信息"
)
async def get_review(
    review_id: UUID,
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Review]:
    """
    获取评价详情
    """
    review = await mentorship_service.get_review_by_id(
        db=db,
        review_id=review_id
    )
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")

    return GeneralResponse(data=review)
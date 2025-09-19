"""
服务管理端点
只包含服务相关的API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from apps.api.v1.deps import (
    get_current_user,
    require_mentor_role,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.service import Service, ServiceCreate, ServiceUpdate
from apps.schemas.common import GeneralResponse, PaginatedResponse
from apps.api.v1.services import service as service_service

router = APIRouter()


# ============ 服务管理 ============

@router.get(
    "",
    response_model=GeneralResponse[List[Service]],
    summary="浏览指导服务",
    description="浏览平台上的所有可用指导服务"
)
async def get_services(
    skill_id: Optional[UUID] = Query(None, description="按技能筛选"),
    mentor_id: Optional[UUID] = Query(None, description="按导师筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[List[Service]]:
    """
    浏览指导服务列表
    """
    services = await service_service.get_services(
        db=db,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    return GeneralResponse(data=services)


@router.post(
    "",
    response_model=GeneralResponse[Service],
    summary="创建指导服务",
    description="导师创建新的指导服务"
)
async def create_service(
    service_data: ServiceCreate,
    current_user: AuthenticatedUser = Depends(require_mentor_role()),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Service]:
    """
    创建指导服务
    """
    service = await service_service.create_service(
        db=db,
        service_in=service_data
    )
    if not service:
        raise HTTPException(status_code=400, detail="创建服务失败")

    return GeneralResponse(data=service)


@router.get(
    "/{service_id}",
    response_model=GeneralResponse[Service],
    summary="获取服务详情",
    description="获取指定服务的详细信息"
)
async def get_service(
    service_id: int,
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Service]:
    """
    获取服务详情
    """
    service = await service_service.get_service_by_id(
        db=db,
        service_id=service_id
    )
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")

    return GeneralResponse(data=service)


@router.put(
    "/{service_id}",
    response_model=GeneralResponse[Service],
    summary="更新服务信息",
    description="导师更新自己服务的价格、描述等信息"
)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    current_user: AuthenticatedUser = Depends(require_mentor_role()),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Service]:
    """
    更新服务信息
    """
    service = await service_service.update_service(
        db=db,
        service_id=service_id,
        service_in=service_data
    )
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")

    return GeneralResponse(data=service)


@router.delete(
    "/{service_id}",
    response_model=GeneralResponse[dict],
    summary="删除服务",
    description="导师删除自己的服务"
)
async def delete_service(
    service_id: int,
    current_user: AuthenticatedUser = Depends(require_mentor_role()),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[dict]:
    """
    删除服务
    """
    success = await service_service.delete_service(
        db=db,
        service_id=service_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="服务不存在")

    return GeneralResponse(data={"message": "删除成功"})


@router.get(
    "/my-services",
    response_model=GeneralResponse[List[Service]],
    summary="获取我的服务",
    description="导师获取自己发布的所有服务"
)
async def get_my_services(
    current_user: AuthenticatedUser = Depends(require_mentor_role()),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[List[Service]]:
    """
    获取我的服务
    """
    services = await service_service.get_services_by_mentor(
        db=db,
        mentor_id=current_user.id
    )
    return GeneralResponse(data=services)

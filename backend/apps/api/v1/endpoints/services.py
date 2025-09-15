from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from apps.api.v1.deps import (
    get_current_user, 
    AuthenticatedUser, 
    require_mentor_role,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceRead, ServicePublic
)
from apps.api.v1.repositories import service

router = APIRouter()

@router.get(
    "",
    response_model=List[ServicePublic],
    summary="浏览所有指导服务",
    description="浏览平台上的所有可用指导服务",
)
async def get_services(
    category: Optional[str] = Query(None, description="服务分类"),
    search_query: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database)
):
    """浏览指导服务"""
    try:
        services = await service.search(
            db=db,
            category=category,
            search_query=search_query,
            limit=limit,
            offset=offset
        )
        return [ServicePublic(**service_item) for service_item in services]
    except Exception as e:
        print(f"搜索服务失败: {e}")
        return []  # 返回空列表而不是抛出异常

@router.post(
    "",
    response_model=ServiceRead,
    summary="发布指导服务",
    description="指导者发布新的指导服务",
)
async def create_service(
    service_data: ServiceCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
):
    """创建指导服务"""
    try:
        # 检查用户角色权限
        if current_user.role not in ["mentor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有导师可以发布服务"
            )
        
        service_result = await service.create(db, int(current_user.id), service_data)
        if not service_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建服务失败"
            )
        return service_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建服务失败: {str(e)}"
        )

@router.get(
    "/{service_id}",
    response_model=ServiceRead,
    summary="获取服务详情",
    description="获取指定服务的详细信息",
)
async def get_service(service_id: int, db: DatabaseAdapter = Depends(get_database)):
    """获取服务详情"""
    try:
        service_result = await service.get_by_id(db, service_id)
        if not service_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在",
            )
        return service_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务失败: {str(e)}"
        )

@router.put(
    "/{service_id}",
    response_model=ServiceRead,
    summary="更新服务信息",
    description="指导者更新自己的服务信息"
)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
):
    """更新服务信息"""
    try:
        # 检查服务是否存在及权限
        service_result = await service.get_by_id(db, service_id)
        if not service_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在",
            )
        
        # 检查是否为服务所有�?
        if service_result.get("navigator_id") != int(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己的服务",
            )
        
        updated_service = await service.update_service(service_id, service_data)
        if not updated_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新服务失败"
            )
        return updated_service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新服务失败: {str(e)}"
        )

@router.delete(
    "/{service_id}",
    summary="删除服务",
    description="指导者删除自己的服务"
)
async def delete_service(
    service_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
):
    """删除服务"""
    try:
        # 检查服务是否存在及权限
        service_result = await service.get_by_id(db, service_id)
        if not service_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在",
            )
        
        # 检查是否为服务所有�?
        if service_result.get("navigator_id") != int(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己的服务",
            )
        
        success = await service.delete_service(service_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="删除服务失败"
            )
        return {"message": "服务已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除服务失败: {str(e)}"
        )

@router.get(
    "/my/services",
    response_model=List[ServiceRead],
    summary="获取我的服务",  
    description="获取当前用户发布的所有服务",
)
async def get_my_services(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取我的服务"""
    try:
        services = await service.get_services_by_navigator(int(current_user.id))
        return services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务列表失败: {str(e)}"
        )

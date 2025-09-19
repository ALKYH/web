"""
服务业务逻辑层
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.service import Service, ServiceCreate, ServiceUpdate
from apps.schemas.session import SessionCreate
from apps.api.v1.repositories import service as service_repo
from apps.api.v1.repositories import session as session_repo
from libs.database.adapters import DatabaseAdapter


# ============ 服务管理 ============
async def get_services(db: DatabaseAdapter, skip: int = 0, limit: int = 100) -> List[Service]:
    """获取所有服务列表"""
    return await service_repo.get_all(db, skip, limit)


async def create_service(db: DatabaseAdapter, service_in: ServiceCreate) -> Optional[Service]:
    """创建新服务"""
    return await service_repo.create(db, service_in)


async def get_service_by_id(db: DatabaseAdapter, service_id: int) -> Optional[Service]:
    """根据ID获取服务"""
    return await service_repo.get_by_id(db, service_id)


async def update_service(db: DatabaseAdapter, service_id: int, service_in: ServiceUpdate) -> Optional[Service]:
    """更新服务信息"""
    return await service_repo.update(db, service_id, service_in)


async def delete_service(db: DatabaseAdapter, service_id: int) -> bool:
    """删除服务"""
    return await service_repo.delete(db, service_id)


async def get_services_by_mentor(db: DatabaseAdapter, mentor_id: UUID) -> List[Service]:
    """获取导师的所有服务"""
    return await service_repo.get_by_mentor_id(db, mentor_id)


# ============ 会话管理 ============
async def create_session(db: DatabaseAdapter, session_in: SessionCreate) -> Optional[dict]:
    """创建新会话"""
    return await session_repo.create(db, session_in)

"""
文件上传服务层
处理文件上传相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status
from apps.schemas.uploaded_files import UploadedFileCreate, UploadedFileDetail, UploadedFileListResponse, FileUploadResponse, FileTypeStats
from apps.api.v1.repositories import uploaded_files as files_repo
from libs.database.adapters import DatabaseAdapter
import uuid


async def upload_file(db: DatabaseAdapter, file_data: UploadedFileCreate) -> FileUploadResponse:
    """
    上传文件
    1. 生成文件ID
    2. 保存文件记录
    3. 返回上传结果
    """
    # 生成UUID
    file_id = uuid.uuid4()

    # 更新文件数据
    file_data.file_id = file_id

    # 保存到数据库
    result = await files_repo.create_file_record(db, file_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="保存文件记录失败"
        )

    return FileUploadResponse(
        file_id=file_id,
        file_url=result['file_url'],
        filename=result['filename'],
        file_size=result['file_size'],
        content_type=result['content_type']
    )


async def get_user_files(db: DatabaseAdapter, user_id: int, file_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> UploadedFileListResponse:
    """
    获取用户的文件列表
    """
    files = await files_repo.get_user_files(db, user_id, file_type, skip, limit)

    file_details = [UploadedFileDetail(**file) for file in files]

    # 获取总大小
    total_size = sum(file.file_size for file in file_details)

    return UploadedFileListResponse(
        files=file_details,
        total=len(file_details),
        total_size=total_size,
        has_next=len(file_details) == limit
    )


async def delete_file(db: DatabaseAdapter, file_id: str, user_id: int) -> bool:
    """
    删除文件
    1. 检查权限
    2. 删除文件记录
    """
    # 解析UUID
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件ID"
        )

    # 获取文件信息
    file_info = await files_repo.get_file_by_uuid(db, file_id)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 检查权限
    if file_info['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文件"
        )

    return await files_repo.delete_file_record(db, file_uuid)

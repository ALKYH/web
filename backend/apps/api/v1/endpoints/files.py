"""
文件上传相关API 路由
包括头像、文档等文件上传功能
基于MinIO对象存储
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from typing import List, Optional
import os
import uuid
import mimetypes
from datetime import datetime

from apps.api.v1.deps import get_current_user
from apps.api.v1.deps import AuthenticatedUser
from apps.schemas.common import GeneralResponse
from libs.config.settings import settings
from libs.storage.minio_manager import minio_storage_manager

router = APIRouter()

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"
}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf", "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

# 文件大小限制 (使用MinIO配置)
MAX_IMAGE_SIZE = settings.minio.MAX_AVATAR_SIZE
MAX_DOCUMENT_SIZE = settings.minio.MAX_DOCUMENT_SIZE

def validate_file_type(file: UploadFile, allowed_types: set) -> bool:
    """验证文件类型"""
    content_type = file.content_type
    if content_type in allowed_types:
        return True
    
    # 如果content_type检测失败，尝试通过文件扩展名判�?
    if file.filename:
        mime_type, _ = mimetypes.guess_type(file.filename)
        return mime_type in allowed_types
    
    return False

def validate_file_size(file_size: int, max_size: int) -> bool:
    """验证文件大小"""
    return file_size <= max_size

def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    if not original_filename:
        return f"{uuid.uuid4()}.bin"
    
    name, ext = os.path.splitext(original_filename)
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name

@router.post(
    "/upload/avatar",
    response_model=dict,
    summary="上传头像",
    description="上传用户头像图片"
)
async def upload_avatar(
    request: Request,
    file: UploadFile = File(..., description="头像图片文件"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    上传用户头像
    
    - **file**: 图片文件 (支持 jpg, jpeg, png, gif, webp)
    - 文件大小限制: 5MB
    """
    try:
        # 验证文件类型
        if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型。仅支持 jpg, jpeg, png, gif, webp 格式"
            )
        
        # 读取文件内容以验证大�?
        contents = await file.read()
        file_size = len(contents)
        
        # 验证文件大小
        if not validate_file_size(file_size, MAX_IMAGE_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制。最大允�?{MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # 使用MinIO存储管理器上传文件
        upload_result = await minio_storage_manager.upload_file(
            file_content=contents,
            original_filename=file.filename,
            file_type="avatar",
            user_id=str(current_user.id)
        )

        file_url = upload_result["file_url"]
        unique_filename = upload_result["unique_filename"]
        
        return {
            "file_id": upload_result["file_id"],
            "filename": file.filename,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": file.content_type,
            "bucket_name": upload_result["bucket_name"],
            "object_name": upload_result["object_name"],
            "uploaded_at": upload_result["uploaded_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post(
    "/upload/document",
    response_model=dict,
    summary="上传文档",
    description="上传用户文档文件"
)
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="文档文件"),
    description: Optional[str] = Form(None, description="文件描述"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    上传用户文档
    
    - **file**: 文档文件 (支持 pdf, doc, docx, txt)
    - **description**: 文件描述 (可选)
    - 文件大小限制: 10MB
    """
    try:
        # 验证文件类型
        if not validate_file_type(file, ALLOWED_DOCUMENT_TYPES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型。仅支持 pdf, doc, docx, txt 格式"
            )
        
        # 读取文件内容以验证大�?
        contents = await file.read()
        file_size = len(contents)
        
        # 验证文件大小
        if not validate_file_size(file_size, MAX_DOCUMENT_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制。最大允�?{MAX_DOCUMENT_SIZE // (1024*1024)}MB"
            )
        
        # 使用MinIO存储管理器上传文件
        upload_result = await minio_storage_manager.upload_file(
            file_content=contents,
            original_filename=file.filename,
            file_type="document",
            user_id=str(current_user.id)
        )

        file_url = upload_result["file_url"]
        unique_filename = upload_result["unique_filename"]
        
        return {
            "file_id": upload_result["file_id"],
            "filename": file.filename,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": file.content_type,
            "description": description,
            "bucket_name": upload_result["bucket_name"],
            "object_name": upload_result["object_name"],
            "uploaded_at": upload_result["uploaded_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post(
    "/upload/multiple",
    response_model=GeneralResponse[List[dict]],
    summary="批量上传文件",
    description="批量上传多个文件"
)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="文件列表"),
    file_type: str = Form("document", description="文件类型: avatar �?document"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    批量上传文件
    
    - **files**: 文件列表
    - **file_type**: 文件类型 (avatar �?document)
    """
    if len(files) > 10:  # 限制批量上传数量
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="一次最多只能上传10个文件"
        )
    
    results = []
    errors = []
    
    for i, file in enumerate(files):
        try:
            if file_type == "avatar":
                # 验证图片文件
                if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
                    errors.append(f"文件{i+1}: 不支持的图片格式")
                    continue
                    
                contents = await file.read()
                if not validate_file_size(len(contents), MAX_IMAGE_SIZE):
                    errors.append(f"文件{i+1}: 图片大小超过限制")
                    continue
                    
                subdir = "avatars"
                
            else:  # document
                # 验证文档文件
                if not validate_file_type(file, ALLOWED_DOCUMENT_TYPES):
                    errors.append(f"文件{i+1}: 不支持的文档格式")
                    continue
                    
                contents = await file.read()
                if not validate_file_size(len(contents), MAX_DOCUMENT_SIZE):
                    errors.append(f"文件{i+1}: 文档大小超过限制")
                    continue
                    
                subdir = "documents"
            
            # 使用MinIO存储管理器上传文件
            file_type = "avatar" if file_type == "avatar" else "document"
            upload_result = await minio_storage_manager.upload_file(
                file_content=contents,
                original_filename=file.filename,
                file_type=file_type,
                user_id=str(current_user.id)
            )

            results.append({
                "file_id": upload_result["file_id"],
                "filename": file.filename,
                "file_url": upload_result["file_url"],
                "file_size": len(contents),
                "content_type": file.content_type,
                "bucket_name": upload_result["bucket_name"],
                "object_name": upload_result["object_name"],
                "uploaded_at": upload_result["uploaded_at"],
                "index": i
            })
            
        except Exception as e:
            errors.append(f"文件{i+1}: {str(e)}")
    
    if errors and not results:
        # 如果所有文件都失败�?
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"所有文件上传失�? {'; '.join(errors)}"
        )
    
    response = {"uploaded_files": results}
    if errors:
        response["errors"] = errors

    return GeneralResponse(data=results)

@router.delete(
    "/files/{bucket_name}/{object_name}",
    response_model=dict,
    summary="删除文件",
    description="删除已上传的文件"
)
async def delete_file(
    bucket_name: str,
    object_name: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除文件

    - **bucket_name**: 存储桶名称
    - **object_name**: 对象名称
    """
    try:
        # 验证存储桶名称是否有效
        valid_buckets = [
            settings.minio.MINIO_BUCKET_AVATARS,
            settings.minio.MINIO_BUCKET_DOCUMENTS,
            settings.minio.MINIO_BUCKET_GENERAL
        ]

        if bucket_name not in valid_buckets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的存储桶名称"
            )

        # 从MinIO删除文件
        success = await minio_storage_manager.delete_file(bucket_name, object_name)

        if success:
            return {
                "message": "文件删除成功",
                "bucket_name": bucket_name,
                "object_name": object_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在或已被删除"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )


@router.get(
    "/files/{bucket_name}/{object_name}",
    response_model=dict,
    summary="获取文件信息",
    description="获取已上传文件的信息"
)
async def get_file_info(
    bucket_name: str,
    object_name: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取文件信息

    - **bucket_name**: 存储桶名称
    - **object_name**: 对象名称
    """
    try:
        # 验证存储桶名称是否有效
        valid_buckets = [
            settings.minio.MINIO_BUCKET_AVATARS,
            settings.minio.MINIO_BUCKET_DOCUMENTS,
            settings.minio.MINIO_BUCKET_GENERAL
        ]

        if bucket_name not in valid_buckets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的存储桶名称"
            )

        # 获取文件信息
        file_info = await minio_storage_manager.get_file_info(bucket_name, object_name)

        return file_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件信息失败: {str(e)}"
        )


@router.post(
    "/files/{bucket_name}/{object_name}/refresh-url",
    response_model=dict,
    summary="刷新文件URL",
    description="刷新文件的预签名URL"
)
async def refresh_file_url(
    bucket_name: str,
    object_name: str,
    expires_minutes: int = 60,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    刷新文件URL

    - **bucket_name**: 存储桶名称
    - **object_name**: 对象名称
    - **expires_minutes**: URL过期时间（分钟）
    """
    try:
        # 验证存储桶名称是否有效
        valid_buckets = [
            settings.minio.MINIO_BUCKET_AVATARS,
            settings.minio.MINIO_BUCKET_DOCUMENTS,
            settings.minio.MINIO_BUCKET_GENERAL
        ]

        if bucket_name not in valid_buckets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的存储桶名称"
            )

        # 生成新的预签名URL
        file_url = await minio_storage_manager.get_file_url(
            bucket_name=bucket_name,
            object_name=object_name,
            expires_minutes=expires_minutes
        )

        return {
            "file_url": file_url,
            "bucket_name": bucket_name,
            "object_name": object_name,
            "expires_minutes": expires_minutes,
            "refreshed_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新文件URL失败: {str(e)}"
        )

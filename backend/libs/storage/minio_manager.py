"""
MinIO存储管理器
提供基于MinIO的文件上传、下载、删除等功能
"""
import os
import uuid
import mimetypes
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from libs.storage.minio_client import minio_client
from libs.config.settings import settings

logger = logging.getLogger(__name__)


class MinIOStorageManager:
    """MinIO存储管理器"""

    def __init__(self):
        """初始化存储管理器"""
        self.config = settings.minio
        self.client = minio_client

    def _get_bucket_for_file_type(self, file_type: str) -> str:
        """
        根据文件类型获取对应的存储桶

        Args:
            file_type: 文件类型 (avatar, document, general)

        Returns:
            存储桶名称
        """
        bucket_mapping = {
            "avatar": self.config.MINIO_BUCKET_AVATARS,
            "document": self.config.MINIO_BUCKET_DOCUMENTS,
            "general": self.config.MINIO_BUCKET_GENERAL
        }
        return bucket_mapping.get(file_type, self.config.MINIO_BUCKET_GENERAL)

    def _get_max_size_for_file_type(self, file_type: str) -> int:
        """
        根据文件类型获取最大文件大小限制

        Args:
            file_type: 文件类型

        Returns:
            最大文件大小（字节）
        """
        size_mapping = {
            "avatar": self.config.MAX_AVATAR_SIZE,
            "document": self.config.MAX_DOCUMENT_SIZE,
            "general": self.config.MAX_GENERAL_SIZE
        }
        return size_mapping.get(file_type, self.config.MAX_GENERAL_SIZE)

    def _get_url_expire_for_file_type(self, file_type: str) -> int:
        """
        根据文件类型获取URL过期时间

        Args:
            file_type: 文件类型

        Returns:
            URL过期时间（分钟）
        """
        expire_mapping = {
            "avatar": self.config.AVATAR_URL_EXPIRE_MINUTES,
            "document": self.config.DOCUMENT_URL_EXPIRE_MINUTES,
            "general": self.config.GENERAL_URL_EXPIRE_MINUTES
        }
        return expire_mapping.get(file_type, self.config.GENERAL_URL_EXPIRE_MINUTES)

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        生成唯一文件名

        Args:
            original_filename: 原始文件名

        Returns:
            唯一文件名
        """
        if not original_filename:
            return f"{uuid.uuid4()}.bin"

        name, ext = os.path.splitext(original_filename)
        unique_name = f"{uuid.uuid4()}{ext}"
        return unique_name

    def _get_content_type(self, filename: str) -> str:
        """
        获取文件的MIME类型

        Args:
            filename: 文件名

        Returns:
            MIME类型
        """
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    async def upload_file(
        self,
        file_content: bytes,
        original_filename: str,
        file_type: str = "general",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上传文件到MinIO

        Args:
            file_content: 文件内容
            original_filename: 原始文件名
            file_type: 文件类型 (avatar, document, general)
            user_id: 用户ID
            metadata: 额外的元数据

        Returns:
            上传结果信息
        """
        try:
            # 检查文件大小
            max_size = self._get_max_size_for_file_type(file_type)
            if len(file_content) > max_size:
                raise ValueError(f"文件大小超过限制。最大允许 {max_size // (1024*1024)}MB")

            # 获取存储桶
            bucket_name = self._get_bucket_for_file_type(file_type)

            # 生成唯一文件名
            unique_filename = self._generate_unique_filename(original_filename)

            # 构建对象名称（如果有用户ID，则按用户分组）
            if user_id:
                object_name = f"{user_id}/{unique_filename}"
            else:
                object_name = unique_filename

            # 获取内容类型
            content_type = self._get_content_type(original_filename)

            # 准备元数据
            file_metadata = {
                "original_filename": original_filename,
                "file_type": file_type,
                "user_id": user_id or "",
                "uploaded_at": datetime.now().isoformat()
            }
            if metadata:
                file_metadata.update(metadata)

            # 上传文件
            upload_result = self.client.upload_file(
                bucket_name=bucket_name,
                object_name=object_name,
                file_content=file_content,
                content_type=content_type,
                metadata=file_metadata
            )

            # 生成预签名URL
            expires_minutes = self._get_url_expire_for_file_type(file_type)
            file_url = self.client.get_file_url(
                bucket_name=bucket_name,
                object_name=object_name,
                expires_minutes=expires_minutes
            )

            result = {
                "file_id": str(uuid.uuid4()),
                "bucket_name": bucket_name,
                "object_name": object_name,
                "original_filename": original_filename,
                "unique_filename": unique_filename,
                "file_url": file_url,
                "file_size": len(file_content),
                "content_type": content_type,
                "file_type": file_type,
                "user_id": user_id,
                "uploaded_at": datetime.now().isoformat(),
                "url_expires_minutes": expires_minutes,
                "metadata": file_metadata
            }

            logger.info(f"File uploaded successfully: {result['file_id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise

    async def download_file(
        self,
        bucket_name: str,
        object_name: str
    ) -> bytes:
        """
        从MinIO下载文件

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称

        Returns:
            文件内容
        """
        try:
            content = self.client.download_file(bucket_name, object_name)
            logger.info(f"File downloaded successfully: {bucket_name}/{object_name}")
            return content

        except Exception as e:
            logger.error(f"Failed to download file {bucket_name}/{object_name}: {str(e)}")
            raise

    async def delete_file(
        self,
        bucket_name: str,
        object_name: str
    ) -> bool:
        """
        从MinIO删除文件

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称

        Returns:
            删除是否成功
        """
        try:
            success = self.client.delete_file(bucket_name, object_name)
            logger.info(f"File deleted successfully: {bucket_name}/{object_name}")
            return success

        except Exception as e:
            logger.error(f"Failed to delete file {bucket_name}/{object_name}: {str(e)}")
            raise

    async def get_file_info(
        self,
        bucket_name: str,
        object_name: str
    ) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称

        Returns:
            文件信息
        """
        try:
            info = self.client.get_file_info(bucket_name, object_name)

            # 生成新的预签名URL
            file_url = self.client.get_file_url(
                bucket_name=bucket_name,
                object_name=object_name,
                expires_minutes=60  # 默认1小时
            )

            info["file_url"] = file_url
            return info

        except Exception as e:
            logger.error(f"Failed to get file info {bucket_name}/{object_name}: {str(e)}")
            raise

    async def get_file_url(
        self,
        bucket_name: str,
        object_name: str,
        expires_minutes: int = 60
    ) -> str:
        """
        获取文件的预签名URL

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
            expires_minutes: URL过期时间

        Returns:
            预签名URL
        """
        try:
            url = self.client.get_file_url(
                bucket_name=bucket_name,
                object_name=object_name,
                expires_minutes=expires_minutes
            )
            return url

        except Exception as e:
            logger.error(f"Failed to get file URL {bucket_name}/{object_name}: {str(e)}")
            raise


# 全局MinIO存储管理器实例
minio_storage_manager = MinIOStorageManager()


# 便捷函数
async def upload_file(
    file_content: bytes,
    original_filename: str,
    file_type: str = "general",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """上传文件的便捷函数"""
    return await minio_storage_manager.upload_file(
        file_content, original_filename, file_type, user_id
    )


async def download_file(bucket_name: str, object_name: str) -> bytes:
    """下载文件的便捷函数"""
    return await minio_storage_manager.download_file(bucket_name, object_name)


async def delete_file(bucket_name: str, object_name: str) -> bool:
    """删除文件的便捷函数"""
    return await minio_storage_manager.delete_file(bucket_name, object_name)

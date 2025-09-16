"""
MinIO对象存储客户端
提供MinIO的基本操作功能
"""
import io
import logging
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
from urllib.parse import urlparse

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:
    raise ImportError("MinIO client not installed. Install with: pip install minio")

from libs.config.settings import settings

logger = logging.getLogger(__name__)


class MinIOClient:
    """MinIO客户端封装类"""

    def __init__(self):
        """初始化MinIO客户端"""
        self.config = settings.minio

        # 创建MinIO客户端
        self.client = Minio(
            endpoint=self.config.MINIO_ENDPOINT,
            access_key=self.config.MINIO_ACCESS_KEY,
            secret_key=self.config.MINIO_SECRET_KEY,
            secure=self.config.MINIO_SECURE,
            region=self.config.MINIO_REGION
        )

        logger.info(f"MinIO client initialized for endpoint: {self.config.minio_url}")

    def ensure_bucket_exists(self, bucket_name: str) -> None:
        """
        确保存储桶存在，如果不存在则创建

        Args:
            bucket_name: 存储桶名称
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            else:
                logger.debug(f"Bucket already exists: {bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to create bucket {bucket_name}: {e}")
            raise

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        上传文件到MinIO

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
            file_content: 文件内容
            content_type: 内容类型
            metadata: 元数据

        Returns:
            上传结果信息
        """
        try:
            # 确保存储桶存在
            self.ensure_bucket_exists(bucket_name)

            # 将字节内容转换为文件对象
            file_obj = io.BytesIO(file_content)

            # 上传文件
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_obj,
                length=len(file_content),
                content_type=content_type,
                metadata=metadata
            )

            upload_info = {
                "bucket_name": bucket_name,
                "object_name": object_name,
                "file_size": len(file_content),
                "content_type": content_type,
                "etag": result.etag,
                "uploaded_at": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            logger.info(f"File uploaded successfully: {bucket_name}/{object_name}")
            return upload_info

        except S3Error as e:
            logger.error(f"Failed to upload file {bucket_name}/{object_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading file {bucket_name}/{object_name}: {e}")
            raise

    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        从MinIO下载文件

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称

        Returns:
            文件内容
        """
        try:
            # 获取对象
            response = self.client.get_object(bucket_name, object_name)

            # 读取内容
            content = response.read()

            logger.info(f"File downloaded successfully: {bucket_name}/{object_name}")
            return content

        except S3Error as e:
            logger.error(f"Failed to download file {bucket_name}/{object_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading file {bucket_name}/{object_name}: {e}")
            raise

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """
        从MinIO删除文件

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称

        Returns:
            删除是否成功
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"File deleted successfully: {bucket_name}/{object_name}")
            return True

        except S3Error as e:
            logger.error(f"Failed to delete file {bucket_name}/{object_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting file {bucket_name}/{object_name}: {e}")
            raise

    def get_file_url(
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
            expires_minutes: URL过期时间（分钟）

        Returns:
            预签名URL
        """
        try:
            expires = timedelta(minutes=expires_minutes)
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )
            logger.debug(f"Generated presigned URL for {bucket_name}/{object_name}")
            return url

        except S3Error as e:
            logger.error(f"Failed to generate URL for {bucket_name}/{object_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating URL for {bucket_name}/{object_name}: {e}")
            raise

    def get_file_info(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称

        Returns:
            文件信息
        """
        try:
            stat = self.client.stat_object(bucket_name, object_name)

            info = {
                "bucket_name": bucket_name,
                "object_name": object_name,
                "size": stat.size,
                "content_type": stat.content_type,
                "etag": stat.etag,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "metadata": stat.metadata or {}
            }

            return info

        except S3Error as e:
            logger.error(f"Failed to get info for {bucket_name}/{object_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting info for {bucket_name}/{object_name}: {e}")
            raise


# 全局MinIO客户端实例
minio_client = MinIOClient()

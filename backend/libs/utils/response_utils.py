"""
响应工具模块

提供统一的响应格式处理工具函数。
"""

import uuid
from typing import Optional, List, Any, Dict
from datetime import datetime, timezone

from apps.schemas.common import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    ErrorCode,
    ErrorDetail
)


def create_success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
    request_id: Optional[str] = None
) -> SuccessResponse:
    """创建成功响应"""
    if request_id is None:
        request_id = str(uuid.uuid4())

    return SuccessResponse(
        data=data,
        message=message,
        code=code,
        request_id=request_id
    )


def create_error_response(
    error_code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None,
    path: Optional[str] = None
) -> ErrorResponse:
    """创建错误响应"""
    if request_id is None:
        request_id = str(uuid.uuid4())

    return ErrorResponse(
        code=error_code.code,
        message=message or error_code.message,
        details=details,
        request_id=request_id,
        path=path
    )


def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    request_id: Optional[str] = None,
    message: str = "success"
) -> PaginatedResponse:
    """创建分页响应"""
    if request_id is None:
        request_id = str(uuid.uuid4())

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        request_id=request_id
    )


def create_validation_error_response(
    field: str,
    message: str,
    code: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """创建验证错误响应"""
    details = [ErrorDetail(field=field, message=message, code=code)]
    return create_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        details=details,
        request_id=request_id
    )


def create_not_found_response(
    resource_type: str,
    resource_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """创建资源不存在错误响应"""
    if resource_id:
        message = f"{resource_type}不存在: {resource_id}"
    else:
        message = f"{resource_type}不存在"

    return create_error_response(
        error_code=ErrorCode.RESOURCE_NOT_FOUND,
        message=message,
        request_id=request_id
    )


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """格式化时间戳"""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()


def extract_request_id(request) -> str:
    """从请求中提取或生成请求ID"""
    # 尝试从请求头中获取
    if hasattr(request, 'headers'):
        request_id = request.headers.get('X-Request-ID')
        if request_id:
            return request_id

    # 生成新的请求ID
    return str(uuid.uuid4())

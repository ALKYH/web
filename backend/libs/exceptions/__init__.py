"""
统一异常处理模块

该模块定义了项目中使用的自定义异常类，确保统一的错误处理和响应格式。
"""

from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from apps.schemas.common import ErrorCode, ErrorDetail


class BaseAPIException(HTTPException):
    """API基础异常类"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_code = error_code
        self.details = details or []

        # 使用错误码中定义的消息，如果没有提供自定义消息
        final_message = message or error_code.message

        # 确定HTTP状态码
        if status_code is None:
            # 根据错误码范围确定默认HTTP状态码
            if 2000 <= error_code.code < 3000:  # 用户相关
                http_status = status.HTTP_404_NOT_FOUND
            elif 3000 <= error_code.code < 4000:  # 认证相关
                http_status = status.HTTP_401_UNAUTHORIZED
            elif 4000 <= error_code.code < 5000:  # 业务逻辑
                http_status = status.HTTP_400_BAD_REQUEST
            elif error_code.code == 1004:  # 权限不足
                http_status = status.HTTP_403_FORBIDDEN
            elif error_code.code == 1005:  # 请求过于频繁
                http_status = status.HTTP_429_TOO_MANY_REQUESTS
            else:
                http_status = status.HTTP_400_BAD_REQUEST
        else:
            http_status = status_code

        super().__init__(status_code=http_status, detail=final_message, headers=headers)


class ValidationException(BaseAPIException):
    """数据验证异常"""

    def __init__(
        self,
        message: str = "数据验证失败",
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details
        )


class ResourceNotFoundException(BaseAPIException):
    """资源不存在异常"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None
    ):
        if message is None:
            if resource_id:
                message = f"{resource_type}不存在: {resource_id}"
            else:
                message = f"{resource_type}不存在"

        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message
        )


class PermissionDeniedException(BaseAPIException):
    """权限不足异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            error_code=ErrorCode.PERMISSION_DENIED,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class AuthenticationException(BaseAPIException):
    """认证异常"""

    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            error_code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class BusinessLogicException(BaseAPIException):
    """业务逻辑异常"""

    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.BUSINESS_RULE_VIOLATION):
        super().__init__(
            error_code=error_code,
            message=message
        )


class RateLimitException(BaseAPIException):
    """请求频率限制异常"""

    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            error_code=ErrorCode.REQUEST_TOO_FREQUENT,
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


# 便捷函数
def create_validation_error(field: str, message: str, code: Optional[str] = None) -> ValidationException:
    """创建字段验证错误"""
    details = [ErrorDetail(field=field, message=message, code=code)]
    return ValidationException(details=details)


def create_user_not_found(user_id: str) -> ResourceNotFoundException:
    """创建用户不存在异常"""
    return ResourceNotFoundException("用户", user_id)


def create_insufficient_balance(required: float, available: float) -> BusinessLogicException:
    """创建余额不足异常"""
    message = f"余额不足，需要 {required}，当前余额 {available}"
    return BusinessLogicException(message, ErrorCode.INSUFFICIENT_BALANCE)

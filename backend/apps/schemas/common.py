
"""
通用 Pydantic 模型

该模块包含项目中广泛使用的通用 Pydantic 模型，旨在促进代码复用并确保一致性。
"""

from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from libs.utils.string_utils import to_camel

DataT = TypeVar("DataT")


class ErrorCode(Enum):
    """统一的错误码枚举"""

    # 通用错误 (1000-1999)
    SUCCESS = (200, "成功")
    UNKNOWN_ERROR = (1000, "未知错误")
    PARAMETER_ERROR = (1001, "参数错误")
    VALIDATION_ERROR = (1002, "数据验证失败")
    RESOURCE_NOT_FOUND = (1003, "资源不存在")
    PERMISSION_DENIED = (1004, "权限不足")
    REQUEST_TOO_FREQUENT = (1005, "请求过于频繁")

    # 用户相关错误 (2000-2999)
    USER_NOT_FOUND = (2000, "用户不存在")
    USER_ALREADY_EXISTS = (2001, "用户已存在")
    USER_DISABLED = (2002, "用户已被禁用")
    USER_NOT_VERIFIED = (2003, "用户未验证")

    # 认证相关错误 (3000-3999)
    UNAUTHORIZED = (3000, "未授权访问")
    TOKEN_EXPIRED = (3001, "令牌已过期")
    TOKEN_INVALID = (3002, "令牌无效")
    LOGIN_FAILED = (3003, "登录失败")

    # 业务逻辑错误 (4000-4999)
    BUSINESS_RULE_VIOLATION = (4000, "业务规则违反")
    INSUFFICIENT_BALANCE = (4001, "余额不足")
    OPERATION_NOT_ALLOWED = (4002, "操作不允许")

    # 智能体相关错误 (5000-5999)
    AGENT_NOT_AVAILABLE = (5000, "智能体不可用")
    AGENT_EXECUTION_FAILED = (5001, "智能体执行失败")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class ErrorDetail(BaseModel):
    """详细错误信息"""
    field: Optional[str] = Field(None, description="错误字段")
    message: str = Field(..., description="错误消息")
    code: Optional[str] = Field(None, description="字段错误码")


class ErrorResponse(BaseModel):
    """统一的错误响应格式"""
    success: bool = Field(False, description="是否成功")
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[List[ErrorDetail]] = Field(None, description="详细错误信息")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    path: Optional[str] = Field(None, description="请求路径")

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


def validate_uuidv7(v: UUID) -> UUID:
    """验证 UUID 是否为版本 7"""
    if v.version != 7:
        raise PydanticCustomError("uuid7", "UUID version 7 is required")
    return v


class IDModel(BaseModel):
    """
    提供标准化的 `id` 字段，使用 UUIDv7 作为唯一标识符。
    所有数据库实体模型都应继承此类。
    """

    id: UUID = Field(
        default_factory=lambda: uuid4(),  # 临时使用 uuid4，将在应用层替换为 uuid7
        description="资源的唯一标识符 (UUIDv7)",
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: UUID) -> UUID:
        """在 Pydantic v2 中，这是一个 before-validator"""
        # return validate_uuidv7(v) # 暂时禁用以兼容现有数据
        return v

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {UUID: str}


class TimestampModel(BaseModel):
    """
    提供标准化的 `created_at` 和 `updated_at` 时间戳字段。
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="记录创建时间 (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="记录最后更新时间 (UTC)"
    )


class Pagination(BaseModel):
    """
    定义分页查询的标准参数。
    """

    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(10, ge=1, le=100, description="每页项目数，范围在1到100之间")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """
    标准化的分页响应结构。
    """

    success: bool = Field(True, description="是否成功")
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Dict[str, Any] = Field(..., description="分页数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")

    @classmethod
    def create(
        cls,
        items: List[DataT],
        total: int,
        page: int,
        page_size: int,
        request_id: Optional[str] = None
    ) -> "PaginatedResponse[DataT]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return cls(
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            request_id=request_id
        )

    class Config:
        json_encoders = {UUID: str}


class LegacyPaginatedResponse(BaseModel, Generic[DataT]):
    """
    向后兼容的旧分页响应结构，建议逐渐迁移到 PaginatedResponse
    """

    total: int = Field(..., description="符合条件的项目总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页项目数")
    total_pages: int = Field(..., description="总页数")
    items: List[DataT] = Field(..., description="当前页的项目列表")

    class Config:
        json_encoders = {UUID: str}


class SuccessResponse(BaseModel, Generic[DataT]):
    """
    统一的成功响应格式
    """

    success: bool = Field(True, description="是否成功")
    code: int = Field(200, description="状态码，200表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[DataT] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class GeneralResponse(BaseModel, Generic[DataT]):
    """
    向后兼容的通用响应结构，建议逐渐迁移到 SuccessResponse
    """

    code: int = Field(200, description="状态码，200表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[DataT] = Field(None, description="响应数据")

    class Config:
        json_encoders = {UUID: str}

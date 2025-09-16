
"""
通用 Pydantic 模型

该模块包含项目中广泛使用的通用 Pydantic 模型，旨在促进代码复用并确保一致性。
"""

from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from libs.utils.string_utils import to_camel

DataT = TypeVar("DataT")


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
    定义标准化的分页响应结构。
    """

    total: int = Field(..., description="符合条件的项目总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页项目数")
    total_pages: int = Field(..., description="总页数")
    items: List[DataT] = Field(..., description="当前页的项目列表")


class GeneralResponse(BaseModel, Generic[DataT]):
    """
    定义标准化的 API 响应结构，用于封装返回数据。
    """

    code: int = Field(200, description="状态码，200表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[DataT] = Field(None, description="响应数据")

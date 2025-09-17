# API响应格式规范

本文档定义了本项目的统一API响应格式规范，确保所有API端点返回一致的响应结构。

## 概述

本项目采用统一的API响应格式，所有API响应都遵循以下结构：

### 成功响应格式

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    // 实际数据
  },
  "timestamp": "2024-01-01T12:00:00.000Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 错误响应格式

```json
{
  "success": false,
  "code": 1000,
  "message": "错误消息",
  "details": [
    {
      "field": "username",
      "message": "用户名不能为空",
      "code": "REQUIRED"
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/auth/login"
}
```

## 响应字段说明

### 通用字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `success` | boolean | 是 | 请求是否成功 |
| `code` | integer | 是 | 状态码 |
| `message` | string | 是 | 响应消息 |
| `timestamp` | string | 是 | 响应时间戳 (ISO 8601格式) |
| `request_id` | string | 是 | 请求ID，用于追踪 |

### 成功响应特有字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `data` | any | 否 | 响应数据 |

### 错误响应特有字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `details` | array | 否 | 详细错误信息 |
| `path` | string | 否 | 请求路径 |

## 错误码规范

### 通用错误码 (1000-1999)

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 1000 | 未知错误 | 500 |
| 1001 | 参数错误 | 400 |
| 1002 | 数据验证失败 | 422 |
| 1003 | 资源不存在 | 404 |
| 1004 | 权限不足 | 403 |
| 1005 | 请求过于频繁 | 429 |

### 用户相关错误码 (2000-2999)

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 2000 | 用户不存在 | 404 |
| 2001 | 用户已存在 | 409 |
| 2002 | 用户已被禁用 | 403 |
| 2003 | 用户未验证 | 403 |

### 认证相关错误码 (3000-3999)

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 3000 | 未授权访问 | 401 |
| 3001 | 令牌已过期 | 401 |
| 3002 | 令牌无效 | 401 |
| 3003 | 登录失败 | 401 |

### 业务逻辑错误码 (4000-4999)

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 4000 | 业务规则违反 | 400 |
| 4001 | 余额不足 | 402 |
| 4002 | 操作不允许 | 403 |

### 智能体相关错误码 (5000-5999)

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 5000 | 智能体不可用 | 503 |
| 5001 | 智能体执行失败 | 500 |

## 分页响应格式

分页响应使用以下格式：

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      // 数据列表
    ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  },
  "timestamp": "2024-01-01T12:00:00.000Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## 使用示例

### Python代码示例

```python
from apps.schemas.common import SuccessResponse, ErrorResponse
from libs.utils.response_utils import create_success_response, create_error_response

# 创建成功响应
success_response = create_success_response(
    data={"user_id": 123, "username": "test"},
    message="用户创建成功"
)

# 创建错误响应
error_response = create_error_response(
    error_code=ErrorCode.USER_NOT_FOUND,
    message="用户不存在"
)
```

### 异常处理示例

```python
from libs.exceptions import ValidationException, ResourceNotFoundException

# 抛出验证异常
raise ValidationException("数据验证失败")

# 抛出资源不存在异常
raise ResourceNotFoundException("用户", "user123")
```

## 向后兼容性

为了确保向后兼容性，项目提供了以下过渡机制：

1. **GeneralResponse**: 旧的通用响应格式，建议逐渐迁移到 SuccessResponse
2. **LegacyPaginatedResponse**: 旧的分页响应格式，建议逐渐迁移到 PaginatedResponse

## 最佳实践

1. **统一使用响应工具函数**: 使用 `create_success_response` 和 `create_error_response` 创建响应
2. **使用自定义异常**: 优先使用项目定义的异常类，而不是直接抛出 HTTPException
3. **提供详细错误信息**: 在错误响应中包含尽可能详细的错误信息
4. **请求ID追踪**: 所有响应都应包含请求ID以便问题追踪
5. **时间戳格式**: 使用ISO 8601格式的时间戳

## 工具函数

项目提供了以下工具函数来简化响应创建：

- `create_success_response()`: 创建成功响应
- `create_error_response()`: 创建错误响应
- `create_paginated_response()`: 创建分页响应
- `create_validation_error_response()`: 创建验证错误响应
- `create_not_found_response()`: 创建资源不存在响应
- `extract_request_id()`: 提取或生成请求ID

## 更新历史

- **2024-01-XX**: 初始版本，定义统一的响应格式规范
- **2024-01-XX**: 添加错误码规范和异常处理机制
- **2024-01-XX**: 添加分页响应格式和向后兼容性支持

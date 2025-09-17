"""
认证相关的 API 路由
包括用户注册、登录等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from apps.api.v1.deps import get_database, get_current_user
from apps.schemas.user import UserCreate, User
from apps.schemas.token import Token, AuthenticatedUser
from apps.schemas.common import SuccessResponse
from apps.api.v1.services import user as user_service
from libs.database.adapters import DatabaseAdapter
from libs.utils.response_utils import create_success_response, extract_request_id

router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse[User],
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账户"
)
async def register(
    user_in: UserCreate,
    request: Request,
    db: DatabaseAdapter = Depends(get_database)
) -> SuccessResponse[User]:
    """
    用户注册端点

    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱地址（可选，但推荐）
    - **password**: 密码（最少8字符）
    """
    user = await user_service.register_user(db, user_in)
    request_id = extract_request_id(request)

    return create_success_response(
        data=user,
        message="用户注册成功",
        code=201,
        request_id=request_id
    )


@router.post(
    "/login",
    response_model=SuccessResponse[Token],
    summary="用户登录",
    description="使用用户名和密码登录获取访问令牌"
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DatabaseAdapter = Depends(get_database)
) -> SuccessResponse[Token]:
    """
    用户登录端点

    - **username**: 用户名
    - **password**: 密码

    返回JWT访问令牌
    """
    token_data = await user_service.login_user(db, form_data.username, form_data.password)
    request_id = extract_request_id(request)

    token = Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"]
    )

    return create_success_response(
        data=token,
        message="登录成功",
        request_id=request_id
    )


@router.post(
    "/refresh",
    response_model=SuccessResponse[Token],
    summary="刷新令牌",
    description="使用有效令牌刷新获取新的访问令牌"
)
async def refresh_token(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> SuccessResponse[Token]:
    """
    令牌刷新端点

    使用当前有效的令牌获取新的访问令牌
    """
    token_data = await user_service.refresh_user_token(current_user.username)
    request_id = extract_request_id(request)

    token = Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"]
    )

    return create_success_response(
        data=token,
        message="令牌刷新成功",
        request_id=request_id
    )
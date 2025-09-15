"""
认证相关的 API 路由
包括用户注册、登录等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from apps.api.v1.deps import get_database, AuthenticatedUser, get_current_user
from apps.schemas.user import UserCreate, UserRead
from apps.schemas.token import Token
from apps.api.v1.services import user as user_service
from libs.database.adapters import DatabaseAdapter

router = APIRouter()


@router.post(
    "/register", 
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账户"
)
async def register(
    user_in: UserCreate,
    db: DatabaseAdapter = Depends(get_database)
):
    """
    用户注册端点
    
    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱地址（可选，但推荐）  
    - **password**: 密码（最少8字符）
    """
    user = await user_service.register_user(db, user_in)
    
    # 返回用户信息（不包含密码）
    return UserRead(
        id=user["id"],
        username=user["username"],
        email=user.get("email"),
        role=user.get("role", "user"),
        is_active=user.get("is_active", True),
        created_at=user["created_at"]
    )


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名和密码登录获取访问令牌"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    用户登录端点
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT访问令牌
    """
    token_data = await user_service.login_user(db, form_data.username, form_data.password)
    
    return Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"]
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新令牌",
    description="使用有效令牌刷新获取新的访问令牌"
)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """
    令牌刷新端点
    
    使用当前有效的令牌获取新的访问令牌
    """
    # 验证用户是否还有效
    if not current_user or not current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = await user_service.refresh_user_token(current_user.username)
    
    return Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"]
    )
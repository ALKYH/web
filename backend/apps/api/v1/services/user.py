"""
用户中心 - 服务层
包括用户资料管理和认证相关业务逻辑
"""
from typing import Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from apps.schemas.user import (
    User, UserCreate, UserUpdate,
    Profile, ProfileUpdate
)
from apps.schemas.token import Token
from apps.api.v1.repositories import user as user_repo
from libs.database.adapters import DatabaseAdapter
from libs.config.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


async def get_user_by_id(db: DatabaseAdapter, user_id: UUID) -> Optional[User]:
    """根据ID获取用户"""
    return await user_repo.get_user_by_id(db, user_id)


async def get_user_by_username(db: DatabaseAdapter, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return await user_repo.get_user_by_username(db, username)


async def register_user(db: DatabaseAdapter, user_data: UserCreate) -> User:
    """注册新用户"""
    # 检查用户名是否已存在
    existing_user = await user_repo.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = await user_repo.get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )

    # 哈希密码
    hashed_password = get_password_hash(user_data.password)

    # 创建用户
    user = await user_repo.create_user(db, user_data, hashed_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

    return user


async def authenticate_user(db: DatabaseAdapter, username: str, password: str) -> Optional[User]:
    """用户认证"""
    user = await user_repo.get_user_by_username(db, username)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


async def login_user(db: DatabaseAdapter, username: str, password: str) -> dict:
    """用户登录"""
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒
    }


async def refresh_user_token(username: str) -> dict:
    """刷新用户令牌"""
    # 这里简化实现，实际应该验证当前的token
    # 创建新的访问令牌
    access_token = create_access_token(data={"sub": username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒
    }


async def update_user(db: DatabaseAdapter, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    return await user_repo.update_user(db, user_id, user_data)


async def get_user_profile(db: DatabaseAdapter, user_id: UUID) -> Optional[Profile]:
    """获取用户画像"""
    return await user_repo.get_user_profile(db, user_id)


async def update_user_profile(db: DatabaseAdapter, user_id: UUID, profile_data: ProfileUpdate) -> Optional[Profile]:
    """更新用户画像"""
    return await user_repo.update_user_profile(db, user_id, profile_data)
"""
用户相关的服务层
包括认证、注册、资料管理等核心业务逻辑
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status

from apps.schemas.user import UserCreate, UserUpdate, ProfileUpdate
from apps.api.v1.repositories import user as user_repo
from libs.database.adapters import DatabaseAdapter
from libs.config.settings import settings


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def register_user(db: DatabaseAdapter, user_in: UserCreate) -> Dict:
    """
    用户注册业务逻辑
    1. 检查用户名和邮箱是否已存在
    2. 创建新用户
    """
    # 1. 检查用户名是否已存在
    existing_user = await user_repo.get_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 2. 检查邮箱是否已存在
    if user_in.email:
        existing_email = await user_repo.get_by_email(db, user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在",
            )
    
    # 3. 创建用户
    user = await user_repo.create(db, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户时发生数据库错误"
        )
        
    return user


async def authenticate_user(db: DatabaseAdapter, username: str, password: str) -> Dict:
    """
    用户认证业务逻辑
    """
    user = await user_repo.authenticate(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def login_user(db: DatabaseAdapter, username: str, password: str) -> Dict:
    """
    用户登录业务逻辑，包含token生成
    """
    # 验证用户
    user = await authenticate_user(db, username, password)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


async def refresh_user_token(username: str) -> Dict:
    """
    刷新用户token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


async def get_user_profile(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取用户完整资料"""
    profile = await user_repo.get_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="用户资料未找到"
        )
    return profile


async def get_user_basic_info(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取用户基本信息"""
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    return user


async def update_user_profile(db: DatabaseAdapter, user_id: int, profile_in: ProfileUpdate) -> Dict:
    """更新用户资料"""
    # 先检查用户是否存在
    existing_user = await user_repo.get_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    # 更新资料
    profile = await user_repo.update_profile(db, user_id, profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到或更新失败"
        )
    
    return profile


async def get_public_profile(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取用户公开资料（隐藏敏感信息）"""
    profile = await user_repo.get_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到"
        )
    
    # 隐藏敏感信息
    public_profile = profile.copy()
    public_profile["email"] = None
    public_profile["phone"] = None
    public_profile["birth_date"] = None
    
    return public_profile
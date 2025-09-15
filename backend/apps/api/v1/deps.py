"""
V1 API依赖注入
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional

from libs.config.settings import settings
from libs.database.connection import get_database_adapter
from libs.database.adapters import DatabaseAdapter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AuthenticatedUser:
    """认证用户类"""
    def __init__(self, id: str, username: str, email: Optional[str] = None, role: str = "user"):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: DatabaseAdapter = Depends(get_database_adapter)
) -> AuthenticatedUser:
    """
    解码JWT并验证用户，返回当前用户信息
    从数据库中获取完整的用户资料，包括角色
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.fetch_one(
        "SELECT id, username, email, role, is_active FROM users WHERE username = $1",
        username
    )
    
    if user is None:
        raise credentials_exception
    
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="账户已被禁用")
        
    return AuthenticatedUser(
        id=str(user['id']),
        username=user['username'],
        email=user.get('email'),
        role=user.get('role', 'user')
    )

async def get_database(db: DatabaseAdapter = Depends(get_database_adapter)) -> DatabaseAdapter:
    """获取数据库连接适配器"""
    return db


# --- 新增的角色验证依赖 ---

def require_role(required_role: str):
    """
    角色检查依赖工厂，用于验证用户是否具有特定角色
    """
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要'{required_role}' 角色权限",
            )
        return current_user
    return role_checker

def require_admin_role():
    """要求管理员角色的依赖"""
    return require_role("admin")

def require_mentor_role():
    """要求指导者（学长学姐）角色的依赖"""
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in ["mentor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此功能仅限认证的学长学姐或管理员使用",
            )
        return current_user
    return role_checker

def require_student_role():
    """要求申请者（学弟学妹）角色的依赖"""
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此功能仅限申请留学的学弟学妹或管理员使用",
            )
        return current_user
    return role_checker
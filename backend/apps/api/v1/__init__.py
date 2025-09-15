"""
V1 API路由管理器
"""
from fastapi import APIRouter

def create_v1_router() -> APIRouter:
    """创建V1 API路由"""
    v1_router = APIRouter()
    
    try:
        from .endpoints import auth, users
        v1_router.include_router(auth.router, prefix="/auth", tags=["认证"])
        v1_router.include_router(users.router, prefix="/users", tags=["用户"])
    except ImportError as e:
        print(f"Warning: Could not import auth/users routes: {e}")
    
    try:
        from .endpoints import mentors, students, services
        v1_router.include_router(mentors.router, prefix="/mentors", tags=["导师"])
        v1_router.include_router(students.router, prefix="/students", tags=["学生"])
        v1_router.include_router(services.router, prefix="/services", tags=["服务"])
    except ImportError as e:
        print(f"Warning: Could not import mentor/student/service routes: {e}")
    
    try:
        from .endpoints import sessions, messages, files, matchings
        v1_router.include_router(sessions.router, prefix="/sessions", tags=["会话"])
        v1_router.include_router(messages.router, prefix="/messages", tags=["消息"])
        v1_router.include_router(files.router, prefix="/files", tags=["文件"])
        v1_router.include_router(matchings.router, prefix="/matching", tags=["匹配"])
    except ImportError as e:
        print(f"Warning: Could not import session/message/file/matching routes: {e}")
    
    return v1_router
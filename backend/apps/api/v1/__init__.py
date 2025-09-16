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
        from .endpoints import services
        v1_router.include_router(services.router, prefix="/services", tags=["服务"])
    except ImportError as e:
        print(f"Warning: Could not import service routes: {e}")
    
    try:
        from .endpoints import sessions, messages, files, matchings, communication, forum, skills, transactions
        v1_router.include_router(sessions.router, prefix="/sessions", tags=["会话"])
        v1_router.include_router(messages.router, prefix="/messages", tags=["消息"])
        v1_router.include_router(files.router, prefix="/files", tags=["文件"])
        v1_router.include_router(matchings.router, prefix="/matching", tags=["匹配"])
        v1_router.include_router(communication.router, prefix="/communication", tags=["通信"])
        v1_router.include_router(forum.router, prefix="/forum", tags=["论坛"])
        v1_router.include_router(skills.router, prefix="/skills", tags=["技能"])
        v1_router.include_router(transactions.router, prefix="/transactions", tags=["交易"])
    except ImportError as e:
        print(f"Warning: Could not import routes: {e}")
    
    return v1_router
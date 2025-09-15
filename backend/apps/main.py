"""
PeerPortal FastAPI应用入口
重构后的简化版本，采用libs/app分离架构
"""
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 导入新的配置和连接管理
from libs.config.settings import settings
from libs.database.connection import lifespan

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="重构后的留学双边信息平台API - 采用libs/app分离架构",
    lifespan=lifespan
)

# CORS配置（支持前端跨域访问）
# 开发环境和生产环境的动态配置
allowed_origins = [
    "http://localhost:3000",  # Next.js 开发服务器
    "http://127.0.0.1:3000", # 本地回环地址
    "http://localhost:8080",  # 备用前端端口
    "https://offerin.vercel.app",  # OfferIn Vercel 部署
    "*.vercel.app", # 生产环境域名
    "*.com", # 生产环境 www 域名
]

# 如果是开发环境，允许更多本地端口
if settings.DEBUG:
    allowed_origins.extend([
        "http://localhost:3001",
        "http://localhost:3002", 
        "http://localhost:4173",  # Vite preview
        "http://localhost:5173",  # Vite dev server
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "Cache-Control",
    ],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=3600,  # 预检请求缓存时间
)

# 移除信任主机中间件，简化配置

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    留学平台全局异常处理器
    保护用户隐私，记录错误日志，返回友好错误信息
    """
    # 在生产环境中应使用专业的日志系统
    print(f"🚨 平台错误: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误，请稍后重试",
            "error_id": f"{hash(str(exc)) % 10000000000:010d}"  # 生成错误ID便于追踪
        },
    )

# 注册V1 API路由
try:
    from apps.api.v1 import create_v1_router
    app.include_router(create_v1_router(), prefix="/api/v1")
    logger.info("✅ V1 API路由注册成功")
except Exception as e:
    logger.error(f"❌ V1 API路由注册失败: {e}")

# 注册AI智能体路由（保持兼容性）
try:
    from apps.api.v1.endpoints.agents import router as v2_agents_router
    app.include_router(v2_agents_router, prefix="/api/v2/agents", tags=["AI智能体v2.0"])
    logger.info("✅ V2 AI智能体路由注册成功")
except Exception as e:
    logger.warning(f"⚠️ V2 AI智能体路由注册失败: {e}")

# 静态文件服务(用于提供上传的文件)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/", summary="API首页")
async def read_root():
    return {
        "message": "欢迎使用PeerPortal API",
        "version": settings.VERSION,
        "status": "运行中",
        "architecture": "重构后的模块化架构(libs/app分离)",
        "features": [
            "🎓 学长学姐指导服务",
            "🎯 智能匹配算法", 
            "📚 专业留学指导",
            "💬 实时沟通交流",
            "🤖 AI智能体系统"
        ],
        "api_docs": "/docs",
        "health_check": "/health"
    }

@app.get("/health", summary="健康检查")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "architecture": "libs/app分离架构"
    }


# 中间件：请求日志记录
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"收到请求: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 记录响应信息
    process_time = time.time() - start_time
    logger.info(
        f"请求处理完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - 耗时: {process_time:.4f}s"
    )
    
    return response


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    logger.info(f"🔄 {settings.APP_NAME} 正在关闭...")


# 导入缺失的模块
import time


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    ) 

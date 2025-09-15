"""
数据库连接管理
"""
try:
    import asyncpg
except ImportError:
    asyncpg = None

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
import logging
from .adapters import DatabaseAdapter, PostgreSQLAdapter, SupabaseAdapter
from libs.config.settings import settings

logger = logging.getLogger(__name__)
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时创建连接池，关闭时释放。"""
    global db_pool
    logger.info("初始化数据库连接池...")
    
    try:
        if not asyncpg:
            raise ImportError("asyncpg not available")
            
        postgres_url = settings.postgres_url
        db_pool = await asyncpg.create_pool(
            dsn=postgres_url,
            min_size=settings.database.DB_POOL_MIN_SIZE,
            max_size=settings.database.DB_POOL_MAX_SIZE,
            command_timeout=30,
            server_settings={'jit': 'off'},
            timeout=10,
        )
        
        async with db_pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
            
        logger.info("数据库连接池创建成功")
        
    except Exception as e:
        logger.error(f"数据库连接池创建失败: {e}")
        db_pool = None
    
    yield
    
    if db_pool:
        logger.info("关闭数据库连接池...")
        await db_pool.close()

async def get_database_adapter() -> AsyncGenerator[DatabaseAdapter, None]:
    """按请求提供数据库适配器，确保连接自动释放。"""
    if db_pool:
        async with db_pool.acquire() as connection:
            adapter = PostgreSQLAdapter(connection)
            yield adapter
    else:
        # 降级到Supabase：此适配器不支持原生SQL，仅为占位
        from supabase import create_client
        client = create_client(settings.database.SUPABASE_URL, settings.database.SUPABASE_KEY)
        yield SupabaseAdapter(client)

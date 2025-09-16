#!/usr/bin/env python3
"""
测试Supabase数据库连接
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append('/home/dev/web/backend')

from libs.config.settings import settings

async def test_connection():
    """测试数据库连接"""
    try:
        import asyncpg

        # 获取数据库URL
        postgres_url = settings.postgres_url
        print(f"📍 数据库URL: {postgres_url}")

        # 创建连接池
        print("🔄 正在创建数据库连接池...")
        pool = await asyncpg.create_pool(
            dsn=postgres_url,
            min_size=1,
            max_size=5,
            command_timeout=30,
            server_settings={'jit': 'off'},
            timeout=10,
        )

        # 测试连接
        print("🧪 正在测试数据库连接...")
        async with pool.acquire() as connection:
            result = await connection.fetchval("SELECT version()")
            print(f"✅ 数据库连接成功！PostgreSQL版本: {result}")

        await pool.close()
        print("✅ 连接池关闭成功")

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"❌ 错误类型: {type(e).__name__}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if not success:
        print("\n🔧 可能的问题:")
        print("1. 检查网络连接是否正常")
        print("2. 验证SUPABASE_DB_PASSWORD是否正确")
        print("3. 检查Supabase项目是否正常运行")
        print("4. 确认防火墙设置")
        sys.exit(1)

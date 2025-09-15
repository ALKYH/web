"""
数据库适配器抽象层
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class DatabaseAdapter(ABC):
    """数据库适配器抽象基类"""
    
    @abstractmethod
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """获取单条记录"""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        """获取多条记录"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, *args) -> str:
        """执行SQL命令"""
        pass

    async def fetch_value(self, query: str, *args) -> Any:
        """获取单个标量值，默认基于 fetch_one 实现"""
        row = await self.fetch_one(query, *args)
        if not row:
            return None
        # 返回第一列的值
        return next(iter(row.values()))

    async def execute_many(self, query: str, args_seq: List[tuple]) -> List[str]:
        """批量执行，默认逐条执行；具体适配器可覆盖以提升性能"""
        results = []
        for args in args_seq:
            results.append(await self.execute(query, *args))
        return results

class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL适配器"""
    
    def __init__(self, connection):
        self.connection = connection
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        result = await self.connection.fetchrow(query, *args)
        return dict(result) if result else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        results = await self.connection.fetch(query, *args)
        return [dict(row) for row in results]
    
    async def execute(self, query: str, *args) -> str:
        return await self.connection.execute(query, *args)

    async def fetch_value(self, query: str, *args) -> Any:
        return await self.connection.fetchval(query, *args)

    async def execute_many(self, query: str, args_seq: List[tuple]) -> List[str]:
        # 使用批处理事务提升性能
        results: List[str] = []
        async with self.connection.transaction():
            for args in args_seq:
                results.append(await self.connection.execute(query, *args))
        return results

class SupabaseAdapter(DatabaseAdapter):
    """Supabase适配器"""
    
    def __init__(self, client):
        self.client = client
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        # 提示：当前适配器不支持原生SQL；请在仓储层避免在降级到 Supabase 时使用原生SQL
        raise NotImplementedError("SupabaseAdapter 不支持原生SQL，请提供表驱动实现")
    
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        raise NotImplementedError("SupabaseAdapter 不支持原生SQL，请提供表驱动实现")
    
    async def execute(self, query: str, *args) -> str:
        raise NotImplementedError("SupabaseAdapter 不支持原生SQL，请提供表驱动实现")

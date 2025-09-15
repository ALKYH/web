"""
订单系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.orders import OrderCreate, OrderUpdate
from libs.database.adapters import DatabaseAdapter


async def get_order_by_id(db: DatabaseAdapter, order_id: int) -> Optional[Dict]:
    """根据ID获取订单"""
    query = """
        SELECT o.*, u1.username as client_username, u2.username as navigator_username,
               s.title as service_title, s.description as service_description
        FROM orders o
        JOIN users u1 ON o.client_id = u1.id
        JOIN users u2 ON o.navigator_id = u2.id
        LEFT JOIN services s ON o.service_id = s.id
        WHERE o.id = $1
    """
    return await db.fetch_one(query, order_id)


async def get_orders_for_user(db: DatabaseAdapter, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的订单"""
    where_clause = "WHERE client_id = $1 OR navigator_id = $1"
    params = [user_id]

    if status:
        where_clause += " AND status = $2"
        params.append(status)

    query = f"""
        SELECT o.*, u1.username as client_username, u2.username as navigator_username,
               s.title as service_title, s.description as service_description
        FROM orders o
        JOIN users u1 ON o.client_id = u1.id
        JOIN users u2 ON o.navigator_id = u2.id
        LEFT JOIN services s ON o.service_id = s.id
        {where_clause}
        ORDER BY o.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_order(db: DatabaseAdapter, order: OrderCreate) -> Optional[Dict]:
    """创建订单"""
    query = """
        INSERT INTO orders (
            service_id, client_id, navigator_id, status, scheduled_at,
            total_price, notes, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        RETURNING *
    """
    values = (
        order.service_id, order.client_id, order.navigator_id, order.status,
        order.scheduled_at, order.total_price, order.notes
    )
    return await db.fetch_one(query, *values)


async def update_order(db: DatabaseAdapter, order_id: int, order: OrderUpdate) -> Optional[Dict]:
    """更新订单"""
    update_data = order.model_dump(exclude_unset=True)
    if not update_data:
        return await get_order_by_id(db, order_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE orders SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, order_id, *update_data.values())


async def delete_order(db: DatabaseAdapter, order_id: int) -> bool:
    """删除订单"""
    query = "DELETE FROM orders WHERE id = $1"
    result = await db.execute(query, order_id)
    return result == "DELETE 1"


async def get_order_stats(db: DatabaseAdapter, user_id: Optional[int] = None) -> Dict[str, Any]:
    """获取订单统计"""
    where_clause = ""
    params = []

    if user_id:
        where_clause = "WHERE client_id = $1 OR navigator_id = $1"
        params = [user_id]

    query = f"""
        SELECT
            COUNT(*) as total_orders,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
            COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_orders,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_orders,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
            COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
            COALESCE(SUM(total_price), 0) as total_revenue,
            AVG(total_price) as average_order_value
        FROM orders
        {where_clause}
    """

    result = await db.fetch_one(query, *params)
    return result or {}


async def get_orders_by_service(db: DatabaseAdapter, service_id: int, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取服务的订单"""
    query = """
        SELECT o.*, u1.username as client_username, u2.username as navigator_username
        FROM orders o
        JOIN users u1 ON o.client_id = u1.id
        JOIN users u2 ON o.navigator_id = u2.id
        WHERE o.service_id = $1
        ORDER BY o.created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_all(query, service_id, limit, skip)

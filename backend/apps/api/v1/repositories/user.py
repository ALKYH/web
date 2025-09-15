"""
用户相关的CRUD操作
使用新的数据库适配器模式
"""
from passlib.context import CryptContext
from typing import Optional, Dict, Any

from apps.schemas.user import UserCreate, UserUpdate, ProfileUpdate
from libs.database.adapters import DatabaseAdapter

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

# --- 通用数据库操作函数(已重构) ---

async def get_by_id(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """根据ID获取用户"""
    query = "SELECT id, username, email, password_hash, role, is_active, created_at FROM users WHERE id = $1"
    return await db.fetch_one(query, user_id)

async def get_by_username(db: DatabaseAdapter, username: str) -> Optional[Dict]:
    """根据用户名获取用户"""
    query = "SELECT id, username, email, password_hash, role, is_active, created_at FROM users WHERE username = $1"
    return await db.fetch_one(query, username)

async def get_by_email(db: DatabaseAdapter, email: str) -> Optional[Dict]:
    """根据邮箱获取用户"""
    query = "SELECT id, username, email, password_hash, role, is_active, created_at FROM users WHERE email = $1"
    return await db.fetch_one(query, email)

async def create(db: DatabaseAdapter, user: UserCreate) -> Optional[Dict]:
    """创建新用户(纯数据操作)"""
    # 哈希密码
    hashed_password = get_password_hash(user.password)
    
    query = """
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, username, email, role, is_active, created_at
    """
    values = (
        user.username, 
        user.email, 
        hashed_password, 
        getattr(user, 'role', 'user'), 
        True
    )
    
    try:
        return await db.fetch_one(query, *values)
    except Exception as e:
        # 在仓库层，我们可以选择记录日志或重新抛出更具体的数据库异常
        print(f"数据库创建用户失败: {e}")
        # 最好是raise一个自定义的DBException
        raise ValueError(f"数据库操作失败: {e}")


async def authenticate(db: DatabaseAdapter, username: str, password: str) -> Optional[Dict]:
    """验证用户登录"""
    user = await get_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    if not user.get('is_active', True):
        return None
    return user

async def update(db: DatabaseAdapter, user_id: int, user_update: UserUpdate) -> Optional[Dict]:
    """更新用户信息"""
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        return await get_by_id(db, user_id)
    
    # 如果要更新密码，需要哈希
    if 'password' in update_data:
        update_data['password_hash'] = get_password_hash(update_data.pop('password'))
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE users SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING id, username, email, role, is_active, created_at
    """
    return await db.fetch_one(query, user_id, *update_data.values())

async def delete(db: DatabaseAdapter, user_id: int) -> bool:
    """删除用户"""
    query = "DELETE FROM users WHERE id = $1"
    result = await db.execute(query, user_id)
    return result == "DELETE 1"

# --- Profile 相关操作 (已重构) ---

async def get_profile(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """获取用户资料"""
    query = """
        SELECT
            u.id, u.username, u.email, u.role, u.is_active, u.created_at,
            p.id as profile_id, p.user_id, p.full_name, p.avatar_url, p.bio, p.phone, p.location, p.website, p.birth_date, p.created_at as profile_created_at, p.updated_at
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.id = $1
    """
    return await db.fetch_one(query, user_id)

async def update_profile(db: DatabaseAdapter, user_id: int, profile: ProfileUpdate) -> Optional[Dict]:
    """更新用户资料"""
    update_data = profile.model_dump(exclude_unset=True)
    if not update_data:
        return await get_profile(db, user_id)
    
    # 先检查profile是否存在
    existing_query = "SELECT id FROM profiles WHERE user_id = $1"
    existing = await db.fetch_one(existing_query, user_id)
    
    if existing:
        # 更新现有profile
        set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
        query = f"""
            UPDATE profiles SET {set_clause}, updated_at = NOW()
            WHERE user_id = $1
        """
        await db.execute(query, user_id, *update_data.values())
    else:
        # 创建新profile
        update_data['user_id'] = user_id
        columns = ", ".join(update_data.keys())
        placeholders = ", ".join([f"${i+1}" for i in range(len(update_data))])
        query = f"INSERT INTO profiles ({columns}) VALUES ({placeholders})"
        await db.execute(query, *update_data.values())
            
    return await get_profile(db, user_id) 

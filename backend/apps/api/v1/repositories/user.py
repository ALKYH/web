"""
用户中心 - 仓库层
提供用户和用户画像的数据库操作
"""
from typing import Optional
from uuid import UUID

from apps.schemas.user import User, UserCreate, UserUpdate, Profile, ProfileUpdate
from libs.database.adapters import DatabaseAdapter


async def get_user_by_id(db: DatabaseAdapter, user_id: UUID) -> Optional[User]:
    """根据ID获取用户"""
    query = """
        SELECT id, username, email, password_hash, role, full_name, avatar_url, phone, is_active, created_at, updated_at
        FROM users
        WHERE id = $1
    """
    row = await db.fetch_one(query, user_id)
    return User(**row) if row else None


async def get_user_by_username(db: DatabaseAdapter, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    query = """
        SELECT id, username, email, password_hash, role, full_name, avatar_url, phone, is_active, created_at, updated_at
        FROM users
        WHERE username = $1
    """
    row = await db.fetch_one(query, username)
    return User(**row) if row else None


async def get_user_by_email(db: DatabaseAdapter, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    query = """
        SELECT id, username, email, password_hash, role, full_name, avatar_url, phone, is_active, created_at, updated_at
        FROM users
        WHERE email = $1
    """
    row = await db.fetch_one(query, email)
    return User(**row) if row else None


async def create_user(db: DatabaseAdapter, user_data: UserCreate, hashed_password: str) -> Optional[User]:
    """创建新用户"""
    query = """
        INSERT INTO users (username, email, password_hash, role, full_name, avatar_url, phone, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id, username, email, password_hash, role, full_name, avatar_url, phone, is_active, created_at, updated_at
    """
    values = (
        user_data.username,
        user_data.email,
        hashed_password,
        user_data.role,
        user_data.full_name,
        user_data.avatar_url,
        user_data.phone,
        user_data.is_active
    )
    row = await db.fetch_one(query, *values)
    return User(**row) if row else None


async def update_user(db: DatabaseAdapter, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if user_data.username is not None:
        set_parts.append(f"username = ${param_index}")
        values.append(user_data.username)
        param_index += 1

    if user_data.email is not None:
        set_parts.append(f"email = ${param_index}")
        values.append(user_data.email)
        param_index += 1

    if user_data.role is not None:
        set_parts.append(f"role = ${param_index}")
        values.append(user_data.role)
        param_index += 1

    if user_data.full_name is not None:
        set_parts.append(f"full_name = ${param_index}")
        values.append(user_data.full_name)
        param_index += 1

    if user_data.avatar_url is not None:
        set_parts.append(f"avatar_url = ${param_index}")
        values.append(user_data.avatar_url)
        param_index += 1

    if user_data.phone is not None:
        set_parts.append(f"phone = ${param_index}")
        values.append(user_data.phone)
        param_index += 1

    if user_data.is_active is not None:
        set_parts.append(f"is_active = ${param_index}")
        values.append(user_data.is_active)
        param_index += 1

    if not set_parts:
        return await get_user_by_id(db, user_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE users
        SET {', '.join(set_parts)}
        WHERE id = ${param_index}
        RETURNING id, username, email, password_hash, role, full_name, avatar_url, phone, is_active, created_at, updated_at
    """
    values.append(user_id)

    row = await db.fetch_one(query, *values)
    return User(**row) if row else None


async def get_user_profile(db: DatabaseAdapter, user_id: UUID) -> Optional[Profile]:
    """获取用户画像"""
    query = """
        SELECT id, user_id, bio, location, website, birth_date,
               urgency_level, budget_min, budget_max, learning_goals,
               title, expertise, experience_years, hourly_rate,
               created_at, updated_at
        FROM profiles
        WHERE user_id = $1
    """
    row = await db.fetch_one(query, user_id)
    if row:
        # 确保 user_id 是字符串类型
        row['user_id'] = str(row['user_id'])
        return Profile(**row)
    return None


async def update_user_profile(db: DatabaseAdapter, user_id: UUID, profile_data: ProfileUpdate) -> Optional[Profile]:
    """更新用户画像"""
    # 首先检查是否存在画像记录
    existing_profile = await get_user_profile(db, user_id)

    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    # 基础字段
    if hasattr(profile_data, 'bio') and profile_data.bio is not None:
        set_parts.append(f"bio = ${param_index}")
        values.append(profile_data.bio)
        param_index += 1

    if hasattr(profile_data, 'location') and profile_data.location is not None:
        set_parts.append(f"location = ${param_index}")
        values.append(profile_data.location)
        param_index += 1

    if hasattr(profile_data, 'website') and profile_data.website is not None:
        set_parts.append(f"website = ${param_index}")
        values.append(profile_data.website)
        param_index += 1

    if hasattr(profile_data, 'birth_date') and profile_data.birth_date is not None:
        set_parts.append(f"birth_date = ${param_index}")
        values.append(profile_data.birth_date)
        param_index += 1

    # 学生特定字段
    if hasattr(profile_data, 'urgency_level') and profile_data.urgency_level is not None:
        set_parts.append(f"urgency_level = ${param_index}")
        values.append(profile_data.urgency_level)
        param_index += 1

    if hasattr(profile_data, 'budget_min') and profile_data.budget_min is not None:
        set_parts.append(f"budget_min = ${param_index}")
        values.append(profile_data.budget_min)
        param_index += 1

    if hasattr(profile_data, 'budget_max') and profile_data.budget_max is not None:
        set_parts.append(f"budget_max = ${param_index}")
        values.append(profile_data.budget_max)
        param_index += 1

    if hasattr(profile_data, 'learning_goals') and profile_data.learning_goals is not None:
        set_parts.append(f"learning_goals = ${param_index}")
        values.append(profile_data.learning_goals)
        param_index += 1

    # 导师特定字段
    if hasattr(profile_data, 'title') and profile_data.title is not None:
        set_parts.append(f"title = ${param_index}")
        values.append(profile_data.title)
        param_index += 1

    if hasattr(profile_data, 'expertise') and profile_data.expertise is not None:
        set_parts.append(f"expertise = ${param_index}")
        values.append(profile_data.expertise)
        param_index += 1

    if hasattr(profile_data, 'experience_years') and profile_data.experience_years is not None:
        set_parts.append(f"experience_years = ${param_index}")
        values.append(profile_data.experience_years)
        param_index += 1

    if hasattr(profile_data, 'hourly_rate') and profile_data.hourly_rate is not None:
        set_parts.append(f"hourly_rate = ${param_index}")
        values.append(profile_data.hourly_rate)
        param_index += 1

    if not set_parts:
        return existing_profile

    set_parts.append("updated_at = NOW()")

    if existing_profile:
        # 更新现有记录
        query = f"""
            UPDATE profiles
            SET {', '.join(set_parts)}
            WHERE user_id = ${param_index}
            RETURNING id, user_id, bio, location, website, birth_date,
                     urgency_level, budget_min, budget_max, learning_goals,
                     title, expertise, experience_years, hourly_rate,
                     created_at, updated_at
        """
        values.append(user_id)
    else:
        # 创建新记录
        # 首先设置所有字段的默认值
        all_fields = {
            'user_id': user_id,
            'bio': None, 'location': None, 'website': None, 'birth_date': None,
            'urgency_level': None, 'budget_min': None, 'budget_max': None, 'learning_goals': None,
            'title': None, 'expertise': [], 'experience_years': None, 'hourly_rate': None
        }

        # 应用更新数据
        for field, value in profile_data.__dict__.items():
            if value is not None:
                all_fields[field] = value

        query = """
            INSERT INTO profiles (user_id, bio, location, website, birth_date,
                                urgency_level, budget_min, budget_max, learning_goals,
                                title, expertise, experience_years, hourly_rate)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id, user_id, bio, location, website, birth_date,
                     urgency_level, budget_min, budget_max, learning_goals,
                     title, expertise, experience_years, hourly_rate,
                     created_at, updated_at
        """
        values = (
            all_fields['user_id'], all_fields['bio'], all_fields['location'], all_fields['website'], all_fields['birth_date'],
            all_fields['urgency_level'], all_fields['budget_min'], all_fields['budget_max'], all_fields['learning_goals'],
            all_fields['title'], all_fields['expertise'], all_fields['experience_years'], all_fields['hourly_rate']
        )

    row = await db.fetch_one(query, *values)
    if row:
        # 确保 user_id 是字符串类型
        row['user_id'] = str(row['user_id'])
        return Profile(**row)
    return None
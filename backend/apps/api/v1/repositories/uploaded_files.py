"""
文件上传系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.uploaded_files import UploadedFileCreate, UploadedFileUpdate
from libs.database.adapters import DatabaseAdapter
from uuid import UUID


async def get_file_by_id(db: DatabaseAdapter, file_id: UUID) -> Optional[Dict]:
    """根据ID获取文件"""
    query = """
        SELECT uf.*, u.username as user_username, u.avatar_url as user_avatar
        FROM uploaded_files uf
        JOIN users u ON uf.user_id = u.id
        WHERE uf.file_id = $1
    """
    return await db.fetch_one(query, str(file_id))


async def get_file_by_uuid(db: DatabaseAdapter, file_id: str) -> Optional[Dict]:
    """根据UUID字符串获取文件"""
    query = """
        SELECT uf.*, u.username as user_username, u.avatar_url as user_avatar
        FROM uploaded_files uf
        JOIN users u ON uf.user_id = u.id
        WHERE uf.file_id = $1::uuid
    """
    return await db.fetch_one(query, file_id)


async def get_user_files(db: DatabaseAdapter, user_id: int, file_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的文件列表"""
    where_clause = "WHERE uf.user_id = $1"
    params = [user_id]

    if file_type:
        where_clause += " AND uf.file_type = $2"
        params.append(file_type)

    query = f"""
        SELECT uf.*, u.username as user_username, u.avatar_url as user_avatar
        FROM uploaded_files uf
        JOIN users u ON uf.user_id = u.id
        {where_clause}
        ORDER BY uf.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_file_record(db: DatabaseAdapter, file: UploadedFileCreate) -> Optional[Dict]:
    """创建文件记录"""
    query = """
        INSERT INTO uploaded_files (
            file_id, user_id, filename, original_filename, file_path,
            file_url, file_size, content_type, file_type, description,
            created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
        RETURNING *
    """
    values = (
        str(file.file_id), file.user_id, file.filename, file.original_filename,
        file.file_path, file.file_url, file.file_size, file.content_type,
        file.file_type, file.description
    )
    return await db.fetch_one(query, *values)


async def update_file_record(db: DatabaseAdapter, file_id: UUID, file: UploadedFileUpdate) -> Optional[Dict]:
    """更新文件记录"""
    update_data = file.model_dump(exclude_unset=True)
    if not update_data:
        return await get_file_by_id(db, file_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE uploaded_files SET {set_clause}, updated_at = NOW()
        WHERE file_id = $1
        RETURNING *
    """
    return await db.fetch_one(query, str(file_id), *update_data.values())


async def delete_file_record(db: DatabaseAdapter, file_id: UUID) -> bool:
    """删除文件记录"""
    query = "DELETE FROM uploaded_files WHERE file_id = $1"
    result = await db.execute(query, str(file_id))
    return result == "DELETE 1"


async def get_file_stats_by_user(db: DatabaseAdapter, user_id: int) -> Dict[str, Any]:
    """获取用户的文件统计"""
    query = """
        SELECT
            COUNT(*) as total_files,
            COALESCE(SUM(file_size), 0) as total_size,
            COUNT(CASE WHEN file_type = 'image' THEN 1 END) as image_count,
            COUNT(CASE WHEN file_type = 'document' THEN 1 END) as document_count,
            COUNT(CASE WHEN file_type = 'video' THEN 1 END) as video_count,
            COUNT(CASE WHEN file_type = 'audio' THEN 1 END) as audio_count,
            MAX(created_at) as last_upload
        FROM uploaded_files
        WHERE user_id = $1
    """
    result = await db.fetch_one(query, user_id)
    return result or {}


async def get_file_stats_by_type(db: DatabaseAdapter) -> List[Dict]:
    """按类型统计文件"""
    query = """
        SELECT
            file_type,
            COUNT(*) as count,
            COALESCE(SUM(file_size), 0) as total_size,
            COUNT(DISTINCT user_id) as user_count
        FROM uploaded_files
        GROUP BY file_type
        ORDER BY count DESC
    """
    return await db.fetch_all(query)


async def search_files(db: DatabaseAdapter, user_id: Optional[int] = None, filename: Optional[str] = None, file_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """搜索文件"""
    where_clause = "WHERE 1=1"
    params = []

    if user_id:
        params.append(user_id)
        where_clause += f" AND uf.user_id = ${len(params)}"

    if filename:
        params.append(f"%{filename}%")
        where_clause += f" AND (uf.filename ILIKE ${len(params)} OR uf.original_filename ILIKE ${len(params)})"

    if file_type:
        params.append(file_type)
        where_clause += f" AND uf.file_type = ${len(params)}"

    query = f"""
        SELECT uf.*, u.username as user_username, u.avatar_url as user_avatar
        FROM uploaded_files uf
        JOIN users u ON uf.user_id = u.id
        {where_clause}
        ORDER BY uf.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)

"""
匹配系统仓库层
提供智能匹配算法和推荐系统的数据库操作
统一管理所有匹配相关的数据访问操作
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from apps.schemas.matching import MatchingRequest, MatchingFilter, RecommendationRequest, MatchingResult
import uuid
from datetime import datetime
import difflib
from libs.database.adapters import DatabaseAdapter


# ============ 匹配算法辅助函数 ============

def _calculate_string_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度(0-1)"""
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def _are_related_majors(major1: str, major2: str) -> bool:
    """检查两个专业是否相关"""
    related_majors = {
        'computer science': ['software engineering', 'information technology', 'data science', 'artificial intelligence'],
        'business administration': ['management', 'marketing', 'finance', 'economics'],
        'electrical engineering': ['computer engineering', 'electronics', 'telecommunications'],
        'mechanical engineering': ['aerospace engineering', 'automotive engineering', 'robotics'],
        'psychology': ['cognitive science', 'behavioral science', 'neuroscience'],
        'biology': ['biotechnology', 'biochemistry', 'bioinformatics', 'molecular biology'],
        'chemistry': ['chemical engineering', 'materials science', 'pharmaceutical science'],
        'mathematics': ['statistics', 'actuarial science', 'applied mathematics', 'data science'],
        'physics': ['astronomy', 'astrophysics', 'engineering physics', 'materials science']
    }

    major1_lower = major1.lower()
    major2_lower = major2.lower()

    for base_major, related_list in related_majors.items():
        if ((major1_lower == base_major and major2_lower in related_list) or
            (major2_lower == base_major and major1_lower in related_list) or
            (major1_lower in related_list and major2_lower in related_list)):
            return True

    return False


def _are_adjacent_degrees(degree1: str, degree2: str) -> bool:
    """检查两个学位是否相邻"""
    degree_hierarchy = ['bachelor', 'master', 'phd']

    try:
        idx1 = degree_hierarchy.index(degree1.lower())
        idx2 = degree_hierarchy.index(degree2.lower())
        return abs(idx1 - idx2) == 1
    except ValueError:
        return False


# ============ 匹配请求管理 ============

async def create_matching_request(db: DatabaseAdapter, student_user_id: int, request: MatchingRequest) -> Optional[str]:
    """创建匹配请求并返回请求ID"""
    request_id = str(uuid.uuid4())

    query = """
        INSERT INTO mentor_matches (
            id, student_id, target_universities, target_majors, degree_level,
            service_categories, budget_min, budget_max, preferred_languages,
            urgency, status, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'pending', NOW(), NOW())
    """

    values = (
        request_id, student_user_id, request.target_universities, request.target_majors,
        request.degree_level, request.service_categories, request.budget_min,
        request.budget_max, request.preferred_languages, request.urgency
    )

    result = await db.execute(query, *values)
    return request_id if "INSERT 1" in result else None


async def get_matching_request(db: DatabaseAdapter, request_id: str) -> Optional[Dict]:
    """获取匹配请求详情"""
    query = "SELECT * FROM mentor_matches WHERE id = $1"
    return await db.fetch_one(query, request_id)


async def update_matching_status(db: DatabaseAdapter, request_id: str, status: str) -> bool:
    """更新匹配请求状态"""
    query = "UPDATE mentor_matches SET status = $1, updated_at = NOW() WHERE id = $2"
    result = await db.execute(query, status, request_id)
    return "UPDATE 1" in result


# ============ 智能匹配算法 ============

async def calculate_match_scores(db: DatabaseAdapter, request: MatchingRequest) -> List[MatchingResult]:
    """计算匹配分数并返回结果"""
    query = """
        SELECT
            mr.id, mr.university, mr.major, mr.degree_level, mr.rating,
            mr.languages, mr.specialties, mr.total_sessions,
            u.username, p.full_name, p.avatar_url,
            -- 大学匹配分数
            CASE
                WHEN mr.university = ANY($1) THEN 0.3
                WHEN EXISTS (
                    SELECT 1 FROM unnest($1) AS target_uni
                    WHERE LOWER(mr.university) LIKE '%' || LOWER(target_uni) || '%' OR
                          LOWER(target_uni) LIKE '%' || LOWER(mr.university) || '%'
                ) THEN 0.2
                ELSE 0.0
            END as university_score,
            -- 专业匹配分数
            CASE
                WHEN mr.major = ANY($2) THEN 0.25
                WHEN EXISTS (
                    SELECT 1 FROM unnest($2) AS target_major
                    WHERE LOWER(mr.major) LIKE '%' || LOWER(target_major) || '%' OR
                          LOWER(target_major) LIKE '%' || LOWER(mr.major) || '%'
                ) THEN 0.15
                ELSE 0.0
            END as major_score,
            -- 学位匹配分数
            CASE
                WHEN mr.degree_level = $3 THEN 0.2
                WHEN $3 = 'master' AND mr.degree_level = 'phd' THEN 0.1
                WHEN $3 = 'phd' AND mr.degree_level = 'master' THEN 0.1
                WHEN $3 = 'bachelor' AND mr.degree_level = 'master' THEN 0.05
                WHEN $3 = 'master' AND mr.degree_level = 'bachelor' THEN 0.05
                ELSE 0.0
            END as degree_score,
            -- 语言匹配分数
            CASE
                WHEN $4 IS NULL THEN 0.1
                WHEN mr.languages && $4 THEN 0.1
                ELSE 0.0
            END as language_score,
            -- 经验加分
            CASE
                WHEN mr.total_sessions >= 50 THEN 0.05
                WHEN mr.total_sessions >= 20 THEN 0.03
                WHEN mr.total_sessions >= 5 THEN 0.01
                ELSE 0.0
            END as experience_bonus,
            -- 专长加分
            CASE
                WHEN mr.specialties && $5 THEN 0.05
                ELSE 0.0
            END as specialty_bonus
        FROM mentorship_relationships mr
        JOIN users u ON mr.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE mr.verification_status = 'verified'
        ORDER BY (
            CASE WHEN mr.university = ANY($1) THEN 0.3 ELSE 0.0 END +
            CASE WHEN mr.major = ANY($2) THEN 0.25 ELSE 0.0 END +
            CASE WHEN mr.degree_level = $3 THEN 0.2 ELSE 0.0 END +
            COALESCE(mr.rating / 5.0, 0) * 0.15 +
            CASE WHEN $4 IS NULL THEN 0.1 WHEN mr.languages && $4 THEN 0.1 ELSE 0.0 END +
            CASE WHEN mr.total_sessions >= 50 THEN 0.05 WHEN mr.total_sessions >= 20 THEN 0.03 WHEN mr.total_sessions >= 5 THEN 0.01 ELSE 0.0 END +
            CASE WHEN mr.specialties && $5 THEN 0.05 ELSE 0.0 END
        ) DESC, mr.rating DESC, mr.total_sessions DESC
        LIMIT 50
    """

    values = (
        request.target_universities, request.target_majors, request.degree_level,
        request.preferred_languages, request.service_categories or []
    )

    rows = await db.fetch_all(query, *values)

    results = []
    for row in rows:
        total_score = (
            row['university_score'] + row['major_score'] + row['degree_score'] +
            (row['rating'] / 5.0) * 0.15 + row['language_score'] +
            row['experience_bonus'] + row['specialty_bonus']
        )

        result = MatchingResult(
            mentor_id=row['id'],
            mentor_name=row['full_name'] or row['username'],
            mentor_avatar=row['avatar_url'],
            university=row['university'],
            major=row['major'],
            degree_level=row['degree_level'],
            rating=row['rating'],
            total_sessions=row['total_sessions'],
            university_match=row['university_score'],
            major_match=row['major_score'],
            degree_match=row['degree_score'],
            language_match=row['language_score'],
            experience_bonus=row['experience_bonus'],
            specialty_bonus=row['specialty_bonus'],
            total_score=round(total_score, 3)
        )
        results.append(result)

    return results


# ============ 匹配结果管理 ============

async def save_matching_result(db: DatabaseAdapter, request_id: str, student_id: int, matches: List[MatchingResult]) -> bool:
    """保存匹配结果"""
    # 更新请求状态
    await update_matching_status(db, request_id, 'completed')

    # 保存匹配历史
    for match in matches[:20]:  # 只保存前20个结果
        query = """
            INSERT INTO mentorship_relationships
            (student_id, mentor_id, match_score, status, created_at, updated_at)
            VALUES ($1, $2, $3, 'pending', NOW(), NOW())
            ON CONFLICT (student_id, mentor_id) DO UPDATE SET
            match_score = $3, updated_at = NOW()
        """
        await db.execute(query, student_id, match.mentor_id, match.total_score)

    return True


async def get_matching_history(db: DatabaseAdapter, student_user_id: int, limit: int = 20) -> List[Dict]:
    """获取匹配历史"""
    query = """
        SELECT
            mr_rel.id, mr_rel.match_score, mr_rel.status, mr_rel.created_at,
            mr.university, mr.major, mr.degree_level, mr.rating,
            u.username, p.full_name, p.avatar_url
        FROM mentorship_relationships mr_rel
        JOIN mentorship_relationships mr ON mr_rel.mentor_id = mr.id
        JOIN users u ON mr.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE mr_rel.student_id = $1
        ORDER BY mr_rel.created_at DESC
        LIMIT $2
    """
    return await db.fetch_all(query, student_user_id, limit)


# ============ 高级筛选 ============

async def get_advanced_filters(db: DatabaseAdapter) -> Dict[str, Any]:
    """获取高级筛选选项"""
    universities_query = "SELECT DISTINCT university FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY university"
    majors_query = "SELECT DISTINCT major FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY major"
    degrees_query = "SELECT DISTINCT degree_level FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY degree_level"

    universities = await db.fetch_all(universities_query)
    majors = await db.fetch_all(majors_query)
    degrees = await db.fetch_all(degrees_query)

    return {
        'universities': [row['university'] for row in universities],
        'majors': [row['major'] for row in majors],
        'degree_levels': [row['degree_level'] for row in degrees],
        'rating_range': {'min': 1, 'max': 5},
        'graduation_year_range': {'min': 2015, 'max': 2030}
    }


async def apply_advanced_filters(db: DatabaseAdapter, filters: MatchingFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """应用高级筛选"""
    where_clauses = ["mr.verification_status = 'verified'"]
    params = []

    if filters.universities:
        params.append(filters.universities)
        where_clauses.append(f"mr.university = ANY(${len(params)})")

    if filters.majors:
        params.append(filters.majors)
        where_clauses.append(f"mr.major = ANY(${len(params)})")

    if filters.degree_levels:
        params.append(filters.degree_levels)
        where_clauses.append(f"mr.degree_level = ANY(${len(params)})")

    if filters.graduation_year_min:
        params.append(filters.graduation_year_min)
        where_clauses.append(f"mr.graduation_year >= ${len(params)}")

    if filters.graduation_year_max:
        params.append(filters.graduation_year_max)
        where_clauses.append(f"mr.graduation_year <= ${len(params)}")

    if filters.rating_min:
        params.append(filters.rating_min)
        where_clauses.append(f"mr.rating >= ${len(params)}")

    if filters.min_sessions:
        params.append(filters.min_sessions)
        where_clauses.append(f"mr.total_sessions >= ${len(params)}")

    if filters.specialties:
        params.append(filters.specialties)
        where_clauses.append(f"mr.specialties && ${len(params)}")

    if filters.languages:
        params.append(filters.languages)
        where_clauses.append(f"mr.languages && ${len(params)}")

    where_clause = " AND ".join(where_clauses)
    params.extend([limit, offset])

    query = f"""
        SELECT mr.*, u.username, p.full_name, p.avatar_url
        FROM mentorship_relationships mr
        JOIN users u ON mr.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE {where_clause}
        ORDER BY mr.rating DESC, mr.total_sessions DESC
        LIMIT ${len(params) - 1} OFFSET ${len(params)}
    """

    return await db.fetch_all(query, *params[:-2], limit, offset)


# ============ 推荐系统 ============

async def get_recommendations(db: DatabaseAdapter, user_id: int, context: str = "general", limit: int = 10) -> List[Dict]:
    """获取个性化推荐"""
    if context == "popular":
        return await _get_popular_mentors(db, limit)
    elif context == "similar":
        return await _get_similar_mentors(db, user_id, limit)
    else:
        return await _get_general_recommendations(db, user_id, limit)


async def _get_popular_mentors(db: DatabaseAdapter, limit: int) -> List[Dict]:
    """获取热门导师"""
    query = """
        SELECT mr.*, u.username, p.full_name, p.avatar_url
        FROM mentorship_relationships mr
        JOIN users u ON mr.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE mr.verification_status = 'verified'
        ORDER BY mr.rating DESC, mr.total_sessions DESC
        LIMIT $1
    """
    return await db.fetch_all(query, limit)


async def _get_similar_mentors(db: DatabaseAdapter, user_id: int, limit: int) -> List[Dict]:
    """获取相似背景的导师"""
    # 获取用户学习需求
    user_needs_query = "SELECT target_universities, target_majors FROM user_learning_needs WHERE user_id = $1"
    user_needs = await db.fetch_one(user_needs_query, user_id)

    if not user_needs:
        return await _get_popular_mentors(db, limit)

    query = """
        SELECT mr.*, u.username, p.full_name, p.avatar_url
        FROM mentorship_relationships mr
        JOIN users u ON mr.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE mr.verification_status = 'verified'
        AND (mr.university = ANY($1) OR mr.major = ANY($2))
        ORDER BY mr.rating DESC
        LIMIT $3
    """
    return await db.fetch_all(query, user_needs['target_universities'], user_needs['target_majors'], limit)


async def _get_general_recommendations(db: DatabaseAdapter, user_id: int, limit: int) -> List[Dict]:
    """获取通用推荐"""
    return await _get_popular_mentors(db, limit)
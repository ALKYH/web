"""
匹配系统仓库层
提供智能匹配算法和推荐系统的数据库操作
统一管理所有匹配相关的数据访问操作

使用现有表结构：
- profiles: 导师信息
- skills, user_skills, mentor_skills: 技能信息
- mentorships: 导师关系/匹配历史
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from apps.schemas.matching import MatchingRequest, MatchingFilter, RecommendationRequest, MatchingResult, MatchingHistory
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

async def create_matching_request(db: DatabaseAdapter, student_user_id: UUID, request: MatchingRequest) -> Optional[str]:
    """创建匹配请求并返回请求ID（简化实现，直接返回模拟ID）"""
    # 简化实现：暂时不存储匹配请求，只返回ID
    from libs.database.adapters import generate_uuid7
    request_id = str(generate_uuid7())
    return request_id


async def get_matching_request(db: DatabaseAdapter, request_id: str) -> Optional[Dict]:
    """获取匹配请求详情（简化实现）"""
    # 简化实现：返回空结果
    return None


async def update_matching_status(db: DatabaseAdapter, request_id: str, status: str) -> bool:
    """更新匹配请求状态（简化实现）"""
    # 简化实现：总是返回成功
    return True


# ============ 智能匹配算法 ============

async def calculate_match_scores(db: DatabaseAdapter, request: MatchingRequest) -> List[MatchingResult]:
    """计算匹配分数并返回结果（使用现有表结构）"""
    # 查询导师信息及其技能
    query = """
        SELECT
            u.id, u.username, p.full_name, p.title, p.expertise,
            p.experience_years, p.hourly_rate, u.avatar_url,
            array_agg(DISTINCT s.name) as skills
        FROM users u
        JOIN profiles p ON u.id = p.user_id
        LEFT JOIN user_skills us ON u.id = us.user_id
        LEFT JOIN skills s ON us.skill_id = s.id
        WHERE u.role = 'mentor' AND u.is_active = true
        GROUP BY u.id, u.username, p.full_name, p.title, p.expertise, p.experience_years, p.hourly_rate, u.avatar_url
        LIMIT 50
    """

    rows = await db.fetch_all(query)

    results = []
    for row in rows:
        # 计算匹配分数
        match_score = _calculate_match_score(row, request)

        from libs.database.adapters import generate_uuid7
        result = MatchingResult(
            request_id=generate_uuid7(),
            user_id=request.user_id,
            matches=[{
                'mentor_id': str(row['id']),
                'mentor_name': row['full_name'] or row['username'],
                'title': row['title'],
                'expertise': row['expertise'] or [],
                'skills': row['skills'] if row['skills'] and row['skills'][0] else [],
                'experience_years': row['experience_years'] or 0,
                'hourly_rate': float(row['hourly_rate'] or 0),
                'match_score': round(match_score, 3)
            }],
            total_matches=1,  # 每个结果包含一个导师
            filters_applied={
                'target_skills': request.target_skills,
                'budget_range': getattr(request, 'budget_range', None)
            },
            created_at=datetime.now()
        )
        results.append(result)

    # 按匹配分数排序
    results.sort(key=lambda x: x.matches[0]['match_score'], reverse=True)
    return results[:20]  # 返回前20个结果


def _calculate_match_score(mentor_row: dict, request: MatchingRequest) -> float:
    """计算导师与请求的匹配分数"""
    score = 0.0

    # 技能匹配 (最高0.5分)
    mentor_skills = mentor_row.get('skills', [])
    if mentor_skills and request.target_skills:
        skill_matches = len(set(mentor_skills) & set(request.target_skills))
        skill_score = min(skill_matches * 0.2, 0.5)  # 每个匹配技能0.2分，最高0.5分
        score += skill_score

    # 经验匹配 (最高0.3分)
    experience_years = mentor_row.get('experience_years', 0)
    if experience_years >= 10:
        score += 0.3
    elif experience_years >= 5:
        score += 0.2
    elif experience_years >= 2:
        score += 0.1

    # 价格合理性 (最高0.2分)
    hourly_rate = mentor_row.get('hourly_rate', 0)
    if hasattr(request, 'budget_range') and request.budget_range:
        max_budget = request.budget_range.get('max', 1000)
        if hourly_rate <= max_budget:
            if hourly_rate <= max_budget * 0.7:  # 预算70%以内
                score += 0.2
            elif hourly_rate <= max_budget * 0.9:  # 预算90%以内
                score += 0.1

    # 基础分数
    score = max(score, 0.1)  # 最低0.1分

    return min(score, 1.0)  # 最高1.0分


# ============ 匹配结果管理 ============

async def save_matching_result(db: DatabaseAdapter, request_id: str, student_id: UUID, matches: List[MatchingResult]) -> bool:
    """保存匹配结果（简化实现）"""
    # 简化实现：暂时不保存匹配结果，只返回成功
    return True


async def get_matching_history(db: DatabaseAdapter, student_user_id: UUID, limit: int = 20) -> List[MatchingHistory]:
    """获取匹配历史（使用mentorships表）"""
    query = """
        SELECT
            m.id, m.student_id, m.mentor_id, m.status, m.created_at, m.updated_at,
            0.0 as match_score  -- 简化实现，没有匹配分数字段
        FROM mentorships m
        WHERE m.student_id = $1
        ORDER BY m.created_at DESC
        LIMIT $2
    """
    rows = await db.fetch_all(query, student_user_id, limit)
    return [MatchingHistory(**row) for row in rows]


# ============ 高级筛选 ============

async def get_advanced_filters(db: DatabaseAdapter) -> Dict[str, Any]:
    """获取高级筛选选项（简化实现）"""
    # 简化实现：返回固定的筛选选项
    return {
        'universities': ['清华大学', '北京大学', '复旦大学', '上海交通大学'],
        'majors': ['计算机科学', '软件工程', '人工智能', '数据科学'],
        'degree_levels': ['bachelor', 'master', 'phd'],
        'rating_range': {'min': 1, 'max': 5},
        'price_range': {'min': 50, 'max': 500}
    }


async def apply_advanced_filters(db: DatabaseAdapter, filters: MatchingFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """应用高级筛选"""
    where_clauses = ["u.role = 'mentor' AND u.is_active = true"]
    params = []

    if filters.skill_ids:
        # 筛选有特定技能的导师
        params.append(filters.skill_ids)
        where_clauses.append("""
            EXISTS (
                SELECT 1 FROM user_skills us
                WHERE us.user_id = u.id AND us.skill_id = ANY($1)
            )
        """)

    if filters.min_experience:
        params.append(filters.min_experience)
        where_clauses.append("p.experience_years >= $2")

    if filters.max_hourly_rate:
        rate_idx = len(params) + 1
        params.append(filters.max_hourly_rate)
        where_clauses.append(f"p.hourly_rate <= ${rate_idx}")

    if filters.location:
        loc_idx = len(params) + 1
        params.append(f"%{filters.location}%")
        where_clauses.append(f"p.location ILIKE ${loc_idx}")

    where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"
    params.extend([limit, offset])

    query = f"""
        SELECT
            u.id, u.username, p.full_name, p.title, p.expertise,
            p.experience_years, p.hourly_rate, u.avatar_url
        FROM users u
        JOIN profiles p ON u.id = p.user_id
        WHERE {where_clause}
        LIMIT ${len(params) - 1} OFFSET ${len(params)}
    """

    rows = await db.fetch_all(query, *params[:-2], limit, offset)
    return [dict(row) for row in rows]


# ============ 推荐系统 ============

async def get_recommendations(db: DatabaseAdapter, user_id: UUID, context: str = "general", limit: int = 10) -> List[Dict]:
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
        SELECT
            u.id, u.username, p.full_name, p.title, p.expertise,
            p.experience_years, p.hourly_rate, u.avatar_url
        FROM users u
        JOIN profiles p ON u.id = p.user_id
        WHERE u.role = 'mentor' AND u.is_active = true
        ORDER BY p.experience_years DESC, p.hourly_rate DESC
        LIMIT $1
    """
    rows = await db.fetch_all(query, limit)
    return [dict(row) for row in rows]


async def _get_similar_mentors(db: DatabaseAdapter, user_id: UUID, limit: int) -> List[Dict]:
    """获取相似背景的导师（简化实现）"""
    # 简化实现：返回热门导师
    return await _get_popular_mentors(db, limit)


async def _get_general_recommendations(db: DatabaseAdapter, user_id: UUID, limit: int) -> List[Dict]:
    """获取通用推荐"""
    return await _get_popular_mentors(db, limit)
"""
V1 API 服务模块
导出所有服务模块供端点层使用
"""

# 导入所有服务模块
from . import (
    communication,
    forum,
    matching,
    mentorship,
    skill,
    transaction,
    user_credit_logs,
    user,
    message
)

# 显式导出message服务
__all__ = [
    'communication',
    'forum',
    'matching',
    'mentorship',
    'skill',
    'transaction',
    'user_credit_logs',
    'user',
    'message'
]

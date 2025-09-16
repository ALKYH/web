"""
字符串工具函数
"""

import re
from typing import Any


def to_camel(s: str) -> str:
    """
    将字符串转换为驼峰命名法

    Args:
        s: 输入字符串

    Returns:
        驼峰命名格式的字符串
    """
    # 处理下划线分隔的字符串
    if '_' in s:
        parts = s.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    # 处理其他格式（如果需要的话）
    return s


def to_snake(s: str) -> str:
    """
    将字符串转换为蛇形命名法

    Args:
        s: 输入字符串

    Returns:
        蛇形命名格式的字符串
    """
    # 使用正则表达式在驼峰命名处插入下划线
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

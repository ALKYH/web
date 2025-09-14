#!/usr/bin/env python3
"""
导出OpenAPI文档脚本
从运行中的FastAPI应用导出OpenAPI规范文档
"""

import json
import requests
import sys
from pathlib import Path

def export_openapi(base_url="http://localhost:8000", output_file="openapi.json"):
    """
    从FastAPI应用导出OpenAPI文档
    
    Args:
        base_url: FastAPI应用的基础URL
        output_file: 输出文件路径
    """
    try:
        # 获取OpenAPI JSON
        response = requests.get(f"{base_url}/openapi.json")
        response.raise_for_status()
        
        openapi_data = response.json()
        
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存美化后的JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ OpenAPI文档已导出到: {output_path.absolute()}")
        print(f"📊 API信息:")
        print(f"   - 标题: {openapi_data.get('info', {}).get('title', 'N/A')}")
        print(f"   - 版本: {openapi_data.get('info', {}).get('version', 'N/A')}")
        print(f"   - 描述: {openapi_data.get('info', {}).get('description', 'N/A')}")
        
        # 统计路径数量
        paths_count = len(openapi_data.get('paths', {}))
        print(f"   - API路径数量: {paths_count}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到FastAPI服务器，请确保服务器正在运行")
        print("   启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

if __name__ == "__main__":
    # 支持命令行参数
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "docs/openapi.json"
    
    success = export_openapi(base_url, output_file)
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
留学项目搜索使用示例
展示如何使用现有的ChromaDB数据进行搜索
"""
import os
import sys

# 添加项目根路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接使用搜索模块
from libs.knowledge_base.study_program_search import get_study_program_search


def demo_basic_search():
    """基本搜索演示"""
    print("🔍 基本搜索演示")
    print("-" * 30)
    
    # 获取搜索实例
    search = get_study_program_search()
    
    # 搜索剑桥大学相关项目
    results = search.search_programs("剑桥大学计算机科学", top_k=3)
    
    print(f"搜索查询: {results['query']}")
    print(f"找到结果: {results['total_found']} 个")
    print(f"搜索耗时: {results['search_time_ms']}ms")
    print()
    
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result['program_name']} ({result['university']})")
        print(f"   地区: {result['region']}")
        print(f"   等级: {result['tier']}")
        print(f"   相似度: {result['score']}")
        print(f"   内容预览: {result['content'][:100]}...")
        print()


def demo_filtered_search():
    """过滤搜索演示"""
    print("🎯 过滤搜索演示")
    print("-" * 30)
    
    search = get_study_program_search()
    
    # 在英国地区搜索人工智能项目
    results = search.search_programs(
        query="人工智能",
        region_filter="英国",
        top_k=3
    )
    
    print("英国地区的人工智能项目:")
    for result in results['results']:
        print(f"- {result['program_name']} ({result['university']})")
        print(f"  等级: {result['tier']}, 相似度: {result['score']}")
    print()


def demo_program_listing():
    """项目列表演示"""
    print("📋 项目列表演示")
    print("-" * 30)
    
    search = get_study_program_search()
    
    # 获取所有T0级别的项目
    t0_programs = search.get_programs_by_filter(tier="T0", limit=5)
    
    print("T0级别的项目:")
    for program in t0_programs:
        print(f"- {program['program_name']} ({program['university']})")
        print(f"  地区: {program['region']}, 学位: {program['degree_type']}")
    print()


def demo_program_details():
    """项目详情演示"""
    print("📄 项目详情演示")
    print("-" * 30)
    
    search = get_study_program_search()
    
    # 先搜索一个项目
    results = search.search_programs("Cambridge ACS", top_k=1)
    if results['results']:
        program_id = results['results'][0]['program_id']
        
        # 获取详细信息
        details = search.get_program_by_id(program_id)
        if details:
            print(f"项目名称: {details['program_name']}")
            print(f"所属大学: {details['university']}")
            print(f"地区: {details['region']}")
            print(f"项目等级: {details['tier']}")
            print(f"学位类型: {details['degree_type']}")
            print(f"授课语言: {details['language']}")
            print(f"学制: {details['duration']}")
            print(f"需要论文: {details['thesis_required']}")
            print(f"需要实习: {details['internship_required']}")
            print(f"\n详细内容:")
            print(details['content'][:300] + "...")
    print()


def demo_statistics():
    """统计信息演示"""
    print("📈 统计信息演示")
    print("-" * 30)
    
    search = get_study_program_search()
    
    # 获取基本信息
    info = search.get_info()
    print(f"数据库: {info['collection_name']}")
    print(f"总项目数: {info['total_programs']}")
    print()
    
    # 获取统计信息
    stats = search.get_statistics()
    print(f"统计样本: {stats['total_sampled']} 个项目")
    print()
    
    # 地区分布
    print("地区分布:")
    for region, count in sorted(stats['regions'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {region}: {count}")
    print()
    
    # 等级分布
    print("等级分布:")
    for tier, count in sorted(stats['tiers'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {tier}: {count}")
    print()


def main():
    """主演示函数"""
    print("🚀 留学项目搜索系统使用演示")
    print("=" * 50)
    
    try:
        # 1. 基本搜索
        demo_basic_search()
        
        # 2. 过滤搜索
        demo_filtered_search()
        
        # 3. 项目列表
        demo_program_listing()
        
        # 4. 项目详情
        demo_program_details()
        
        # 5. 统计信息
        demo_statistics()
        
        print("✅ 演示完成!")
        
        # 显示API使用方法
        print("\n💻 API使用方法:")
        print("""
# 1. 获取搜索实例
from libs.knowledge_base.study_program_search import get_study_program_search
search = get_study_program_search()

# 2. 基本搜索
results = search.search_programs("剑桥大学计算机科学", top_k=5)

# 3. 带过滤的搜索  
results = search.search_programs("人工智能", region_filter="英国", top_k=5)

# 4. 获取项目列表
programs = search.get_programs_by_filter(tier="T0", limit=10)

# 5. 获取项目详情
details = search.get_program_by_id("program_0")

# 6. 获取统计信息
stats = search.get_statistics()
        """)
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

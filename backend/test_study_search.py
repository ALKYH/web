#!/usr/bin/env python3
"""
测试留学项目搜索功能
"""
import os
import sys

# 添加项目根路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libs.knowledge_base.study_program_search import get_study_program_search


def test_basic_functions():
    """测试基本功能"""
    print("🧪 测试留学项目搜索功能")
    print("=" * 50)
    
    try:
        # 获取搜索实例
        search = get_study_program_search()
        print("✅ 成功连接到ChromaDB")
        
        # 1. 获取基本信息
        print("\n📊 数据库信息:")
        info = search.get_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 2. 测试搜索功能
        print("\n🔍 搜索测试:")
        
        test_queries = [
            "剑桥大学计算机科学",
            "人工智能",
            "英国大学",
            "T0项目"
        ]
        
        for query in test_queries:
            print(f"\n   查询: '{query}'")
            results = search.search_programs(query, top_k=3)
            
            if results.get("results"):
                print(f"   ✅ 找到 {len(results['results'])} 个结果 (耗时: {results['search_time_ms']}ms)")
                for i, result in enumerate(results["results"], 1):
                    print(f"      {i}. {result['program_name']} ({result['university']})")
                    print(f"         地区: {result['region']}, 等级: {result['tier']}, 相似度: {result['score']}")
            else:
                print("   ❌ 没有找到结果")
                if results.get("error"):
                    print(f"      错误: {results['error']}")
        
        # 3. 测试过滤功能
        print("\n🎯 过滤测试:")
        
        # 按地区过滤
        uk_programs = search.get_programs_by_filter(region="英国", limit=5)
        print(f"   英国项目 ({len(uk_programs)} 个):")
        for prog in uk_programs[:3]:
            print(f"      - {prog['program_name']} ({prog['university']})")
        
        # 按等级过滤
        t0_programs = search.get_programs_by_filter(tier="T0", limit=5)
        print(f"   T0级项目 ({len(t0_programs)} 个):")
        for prog in t0_programs[:3]:
            print(f"      - {prog['program_name']} ({prog['university']})")
        
        # 4. 获取项目详情
        if uk_programs:
            print("\n📄 项目详情测试:")
            program_id = uk_programs[0]["program_id"]
            details = search.get_program_by_id(program_id)
            
            if details:
                print(f"   项目: {details['program_name']}")
                print(f"   大学: {details['university']}")
                print(f"   地区: {details['region']}")
                print(f"   等级: {details['tier']}")
                print(f"   学位: {details['degree_type']}")
                print(f"   语言: {details['language']}")
                print(f"   学制: {details['duration']}")
                print(f"   内容: {details['content'][:100]}...")
        
        # 5. 统计信息
        print("\n📈 统计信息:")
        stats = search.get_statistics()
        print(f"   样本数量: {stats.get('total_sampled', 0)}")
        
        regions = stats.get('regions', {})
        print(f"   地区分布: {dict(list(regions.items())[:5])}")
        
        tiers = stats.get('tiers', {})
        print(f"   等级分布: {dict(list(tiers.items())[:5])}")
        
        print("\n🎉 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_basic_functions()


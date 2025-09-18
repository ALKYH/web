#!/usr/bin/env python3
"""
PeerPortal 知识库测试脚本
演示如何使用 Chroma 云数据库构建和使用知识库
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libs.knowledge_base.chroma_knowledge_base import (
    ChromaKnowledgeBase, 
    initialize_knowledge_base
)


async def create_test_documents():
    """创建测试文档"""
    test_docs = []
    
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 创建测试文档目录: {temp_dir}")
    
    # 留学申请指南
    study_guide = temp_dir / "留学申请指南.txt"
    study_guide.write_text("""
留学申请完整指南

一、申请准备阶段
1. 确定目标国家和专业
   - 美国：世界顶尖教育资源，竞争激烈
   - 英国：学制短，历史悠久
   - 澳洲：移民政策友好，环境优美
   - 加拿大：性价比高，多元文化

2. 语言考试准备
   - 托福：美国主流，总分120分，建议100分以上
   - 雅思：英联邦国家，总分9分，建议7分以上
   - GRE：研究生入学考试，适用于大部分专业
   - GMAT：商科专业必考，满分800分

二、申请材料准备
1. 学术材料
   - 成绩单：需要官方认证
   - GPA：美国4.0制，建议3.5以上
   - 学位证书：需要公证翻译

2. 文书材料
   - 个人陈述：展现个人特色和目标
   - 推荐信：2-3封，来自教授或雇主
   - 简历：学术和实习经历

三、申请时间规划
提前1-2年开始准备，关键时间节点：
- 大三上学期：确定目标，开始语言考试准备
- 大三下学期：参加语言考试，准备文书
- 大四上学期：提交申请
- 大四下学期：等待录取结果
""", encoding='utf-8')
    test_docs.append(str(study_guide))
    
    # GPA计算说明
    gpa_guide = temp_dir / "GPA计算方法.md"
    gpa_guide.write_text("""
# GPA计算方法详解

## 什么是GPA？
GPA (Grade Point Average) 是学业成绩平均绩点，是国外大学评估学生学术能力的重要指标。

## 美国4.0制GPA对照表
| 成绩等级 | 百分制 | 4.0制GPA | 说明 |
|---------|--------|----------|------|
| A+ | 97-100 | 4.0 | 优秀 |
| A | 93-96 | 4.0 | 优秀 |
| A- | 90-92 | 3.7 | 良好 |
| B+ | 87-89 | 3.3 | 良好 |
| B | 83-86 | 3.0 | 中等 |
| B- | 80-82 | 2.7 | 中等 |
| C+ | 77-79 | 2.3 | 及格 |
| C | 73-76 | 2.0 | 及格 |
| C- | 70-72 | 1.7 | 及格 |
| D | 60-69 | 1.0 | 不及格 |
| F | 0-59 | 0.0 | 不及格 |

## 计算公式
GPA = (课程学分1 × 成绩绩点1 + 课程学分2 × 成绩绩点2 + ...) / 总学分

## 申请要求
- 顶尖学校：3.7以上
- 好学校：3.3以上
- 一般学校：3.0以上
""", encoding='utf-8')
    test_docs.append(str(gpa_guide))
    
    # 推荐信模板
    rec_letter = temp_dir / "推荐信写作指南.txt"
    rec_letter.write_text("""
推荐信写作完整指南

推荐信是留学申请中的重要组成部分，一封好的推荐信能够从第三方角度客观地评价申请者的能力和潜力。

一、推荐人选择
1. 学术推荐人
   - 专业课教授：了解学术能力
   - 导师：了解研究能力
   - 系主任：权威性强

2. 实习推荐人
   - 直接上司：了解工作能力
   - HR经理：了解综合素质
   - 项目负责人：了解团队合作

二、推荐信内容结构
1. 开头段落
   - 推荐人身份介绍
   - 与申请者的关系
   - 认识时间和背景

2. 主体段落
   - 具体事例说明能力
   - 学术表现或工作表现
   - 个人品质和特点

3. 结尾段落
   - 总结评价
   - 推荐强度
   - 联系方式

三、写作要点
1. 具体化：用具体事例而非空泛描述
2. 量化：用数据说话，如成绩排名
3. 对比：与同龄人的比较
4. 诚实：避免夸大其词
5. 个性化：突出申请者独特之处

四、常见问题
1. 推荐信雷同：每封信都要有不同侧重点
2. 内容空泛：缺乏具体事例支撑
3. 格式不规范：注意信头、日期、签名等
4. 语言问题：英文推荐信需要地道表达
""", encoding='utf-8')
    test_docs.append(str(rec_letter))
    
    print(f"✅ 创建了 {len(test_docs)} 个测试文档")
    return test_docs, temp_dir


async def test_knowledge_base():
    """测试知识库功能"""
    print("🧪 开始测试 PeerPortal 知识库系统")
    print("=" * 60)
    
    # 你的 Chroma 配置
    API_KEY = "ck-EoDTZTCRe9Qb3LaWGEQA2EGDXoqx5FmZ93Y2KGSfQniL"
    TENANT = "fd1cb388-55f9-432c-9fc3-b12811c67ee0"
    DATABASE = "test-global-cs"
    
    try:
        # 1. 初始化知识库
        print("\\n🚀 初始化知识库...")
        kb = initialize_knowledge_base(
            api_key=API_KEY,
            tenant=TENANT,
            database=DATABASE,
            collection_name="peerpotal_test",
            embedding_provider="sentence_transformers"  # 使用本地模型
        )
        
        # 2. 创建测试文档
        test_docs, temp_dir = await create_test_documents()
        
        # 3. 添加文档到知识库
        print("\\n📚 添加文档到知识库...")
        added_docs = []
        for doc_path in test_docs:
            result = await kb.add_document(
                file_path=doc_path,
                tenant_id="test_user",
                metadata={"category": "留学指南", "language": "中文"}
            )
            
            if result["success"]:
                print(f"✅ 添加成功: {result['filename']} ({result['chunks_count']} 个块)")
                added_docs.append(result)
            else:
                print(f"❌ 添加失败: {result['error']}")
        
        # 4. 获取知识库信息
        print("\\n📊 知识库信息:")
        info = kb.get_collection_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 5. 测试搜索功能
        print("\\n🔍 测试搜索功能...")
        
        test_queries = [
            "如何计算GPA？",
            "留学申请需要准备什么材料？",
            "托福和雅思的区别是什么？",
            "推荐信应该找谁写？",
            "美国大学GPA要求"
        ]
        
        for query in test_queries:
            print(f"\\n🔎 查询: {query}")
            results = await kb.search(
                query=query,
                top_k=3,
                tenant_id="test_user"
            )
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"   📄 结果{i} (相似度: {result['score']:.3f})")
                    print(f"      文件: {result['metadata'].get('filename', '未知')}")
                    print(f"      内容: {result['content'][:100]}...")
            else:
                print("   ❌ 没有找到相关结果")
        
        # 6. 列出所有文档
        print("\\n📋 文档列表:")
        documents = await kb.list_documents(tenant_id="test_user")
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc['filename']} (ID: {doc['document_id'][:8]}...)")
        
        # 7. 测试删除功能（可选）
        if added_docs and input("\\n❓ 是否测试删除功能？(y/N): ").lower() == 'y':
            doc_to_delete = added_docs[0]
            print(f"\\n🗑️ 删除文档: {doc_to_delete['filename']}")
            success = await kb.delete_document(doc_to_delete['document_id'])
            if success:
                print("✅ 删除成功")
            else:
                print("❌ 删除失败")
        
        print("\\n🎉 知识库测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时文件
        if 'temp_dir' in locals():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"🧹 清理临时文件: {temp_dir}")


async def demo_integration_with_agent():
    """演示与 Agent 系统的集成"""
    print("\\n🤖 演示知识库与 Agent 系统集成")
    print("-" * 40)
    
    # 模拟 Agent 查询知识库的场景
    kb = ChromaKnowledgeBase(
        api_key="ck-EoDTZTCRe9Qb3LaWGEQA2EGDXoqx5FmZ93Y2KGSfQniL",
        tenant="fd1cb388-55f9-432c-9fc3-b12811c67ee0",
        database="test-global-cs",
        collection_name="peerpotal_test"
    )
    
    # 模拟用户查询
    user_queries = [
        "我的GPA是3.2，能申请什么学校？",
        "推荐信应该包含哪些内容？",
        "托福需要考多少分？"
    ]
    
    for query in user_queries:
        print(f"\\n👤 用户问题: {query}")
        
        # 1. 搜索相关知识
        knowledge_results = await kb.search(
            query=query,
            top_k=2,
            tenant_id="test_user"
        )
        
        # 2. 构建上下文
        if knowledge_results:
            context = "\\n".join([
                f"参考资料 {i+1}: {result['content'][:200]}..."
                for i, result in enumerate(knowledge_results)
            ])
            
            print(f"🧠 Agent 获取的知识上下文:")
            print(f"   找到 {len(knowledge_results)} 条相关资料")
            
            # 3. 模拟 Agent 回答（这里简化处理）
            print(f"🤖 Agent 回答: 基于知识库中的资料，{query}")
            print(f"   相关度最高的资料来自: {knowledge_results[0]['metadata'].get('filename')}")
        else:
            print("❌ 知识库中没有找到相关信息")


async def main():
    """主函数"""
    print("🚀 PeerPortal 知识库系统测试")
    print("=" * 50)
    
    # 检查依赖
    missing_deps = []
    
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append("PyPDF2")
    
    if missing_deps:
        print(f"❌ 缺少依赖包: {', '.join(missing_deps)}")
        print("请安装: pip install chromadb PyPDF2 python-docx beautifulsoup4 markdown sentence-transformers")
        return
    
    try:
        # 运行测试
        await test_knowledge_base()
        
        # 演示集成
        if input("\\n❓ 是否演示 Agent 集成？(y/N): ").lower() == 'y':
            await demo_integration_with_agent()
        
    except KeyboardInterrupt:
        print("\\n👋 测试中断")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())


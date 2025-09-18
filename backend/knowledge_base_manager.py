#!/usr/bin/env python3
"""
PeerPortal 知识库管理工具
用于批量添加文档、搜索测试、管理知识库等操作
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
import json

# 添加项目根路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libs.knowledge_base.chroma_knowledge_base import (
    ChromaKnowledgeBase, 
    initialize_knowledge_base,
    get_knowledge_base
)


class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, api_key: str, tenant: str, database: str):
        self.kb = initialize_knowledge_base(
            api_key=api_key,
            tenant=tenant,
            database=database,
            collection_name="peerpotal_documents",
            embedding_provider="sentence_transformers"  # 使用本地模型，更稳定
        )
        print(f"✅ 知识库初始化成功")
        print(f"   - 租户: {tenant}")
        print(f"   - 数据库: {database}")
        print(f"   - 集合: peerpotal_documents")
    
    async def add_single_document(self, file_path: str, tenant_id: str = "default", metadata: Dict = None):
        """添加单个文档"""
        print(f"\\n📄 添加文档: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        result = await self.kb.add_document(
            file_path=file_path,
            tenant_id=tenant_id,
            metadata=metadata or {}
        )
        
        if result["success"]:
            print(f"✅ 添加成功!")
            print(f"   - 文档ID: {result['document_id']}")
            print(f"   - 文件名: {result['filename']}")
            print(f"   - 块数量: {result['chunks_count']}")
            print(f"   - 文件大小: {result.get('file_size', 0)} 字节")
            return True
        else:
            print(f"❌ 添加失败: {result['error']}")
            return False
    
    async def add_directory(self, directory_path: str, tenant_id: str = "default", recursive: bool = True):
        """批量添加目录中的文档"""
        print(f"\\n📁 批量添加目录: {directory_path}")
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ 目录不存在: {directory_path}")
            return
        
        # 支持的文件类型
        supported_extensions = {'.pdf', '.txt', '.md', '.docx', '.doc', '.html', '.htm'}
        
        # 查找文件
        if recursive:
            files = [f for f in directory.rglob("*") if f.suffix.lower() in supported_extensions]
        else:
            files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]
        
        if not files:
            print("❌ 没有找到支持的文档文件")
            return
        
        print(f"📋 找到 {len(files)} 个文档文件")
        
        success_count = 0
        for file_path in files:
            try:
                success = await self.add_single_document(
                    str(file_path), 
                    tenant_id=tenant_id,
                    metadata={"batch_import": True, "source_directory": str(directory)}
                )
                if success:
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
        
        print(f"\\n📊 批量添加完成: {success_count}/{len(files)} 个文件成功添加")
    
    async def search_documents(self, query: str, top_k: int = 5, tenant_id: str = None):
        """搜索文档"""
        print(f"\\n🔍 搜索查询: {query}")
        print(f"   - 返回数量: {top_k}")
        if tenant_id:
            print(f"   - 租户过滤: {tenant_id}")
        
        results = await self.kb.search(
            query=query,
            top_k=top_k,
            tenant_id=tenant_id
        )
        
        if not results:
            print("❌ 没有找到相关文档")
            return
        
        print(f"\\n📋 找到 {len(results)} 个相关结果:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\\n🏆 结果 {i} (相似度: {result['score']:.3f})")
            print(f"📄 文件: {result['metadata'].get('filename', '未知')}")
            print(f"📝 内容预览: {result['content'][:200]}...")
            
            # 显示元数据
            metadata = result['metadata']
            if metadata.get('chunk_index') is not None:
                print(f"📊 块信息: {metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}")
            
            print("-" * 40)
    
    async def list_documents(self, tenant_id: str = None, limit: int = 20):
        """列出文档"""
        print(f"\\n📚 文档列表 (限制: {limit})")
        if tenant_id:
            print(f"   - 租户过滤: {tenant_id}")
        
        documents = await self.kb.list_documents(tenant_id=tenant_id, limit=limit)
        
        if not documents:
            print("❌ 没有找到文档")
            return
        
        print(f"\\n📋 找到 {len(documents)} 个文档:")
        print("=" * 80)
        
        for i, doc in enumerate(documents, 1):
            print(f"\\n📄 文档 {i}")
            print(f"   ID: {doc.get('document_id', '未知')}")
            print(f"   文件名: {doc.get('filename', '未知')}")
            print(f"   块数量: {doc.get('total_chunks', 0)}")
            print(f"   文件大小: {doc.get('file_size', 0)} 字节")
            print(f"   创建时间: {doc.get('created_at', '未知')}")
            print(f"   租户: {doc.get('tenant_id', '未知')}")
    
    async def delete_document(self, document_id: str):
        """删除文档"""
        print(f"\\n🗑️ 删除文档: {document_id}")
        
        success = await self.kb.delete_document(document_id)
        
        if success:
            print("✅ 文档删除成功")
        else:
            print("❌ 文档删除失败")
        
        return success
    
    def get_collection_info(self):
        """获取集合信息"""
        print("\\n📊 知识库信息:")
        info = self.kb.get_collection_info()
        
        if info:
            print(f"   - 集合名称: {info.get('collection_name')}")
            print(f"   - 文档数量: {info.get('document_count', 0)}")
            print(f"   - 数据库: {info.get('database')}")
            print(f"   - 租户: {info.get('tenant')}")
        else:
            print("❌ 无法获取集合信息")
    
    async def interactive_mode(self):
        """交互模式"""
        print("\\n🎯 进入交互模式 (输入 'help' 查看命令)")
        
        while True:
            try:
                command = input("\\n> ").strip().lower()
                
                if command in ['exit', 'quit', 'q']:
                    print("👋 退出交互模式")
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'info':
                    self.get_collection_info()
                elif command.startswith('search '):
                    query = command[7:].strip()
                    if query:
                        await self.search_documents(query)
                    else:
                        print("❌ 请输入搜索查询")
                elif command.startswith('add '):
                    file_path = command[4:].strip()
                    if file_path:
                        await self.add_single_document(file_path)
                    else:
                        print("❌ 请输入文件路径")
                elif command == 'list':
                    await self.list_documents()
                elif command.startswith('delete '):
                    doc_id = command[7:].strip()
                    if doc_id:
                        await self.delete_document(doc_id)
                    else:
                        print("❌ 请输入文档ID")
                else:
                    print("❌ 未知命令，输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\\n👋 退出交互模式")
                break
            except Exception as e:
                print(f"❌ 命令执行失败: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\\n📖 可用命令:")
        print("  help                 - 显示此帮助信息")
        print("  info                 - 显示知识库信息")
        print("  search <query>       - 搜索文档")
        print("  add <file_path>      - 添加单个文档")
        print("  list                 - 列出所有文档")
        print("  delete <doc_id>      - 删除文档")
        print("  exit/quit/q          - 退出交互模式")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PeerPortal 知识库管理工具")
    parser.add_argument("--api-key", default="ck-EoDTZTCRe9Qb3LaWGEQA2EGDXoqx5FmZ93Y2KGSfQniL", help="Chroma API Key")
    parser.add_argument("--tenant", default="fd1cb388-55f9-432c-9fc3-b12811c67ee0", help="Chroma Tenant")
    parser.add_argument("--database", default="test-global-cs", help="Chroma Database")
    parser.add_argument("--tenant-id", default="default", help="文档租户ID")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加文档命令
    add_parser = subparsers.add_parser("add", help="添加文档")
    add_parser.add_argument("path", help="文件或目录路径")
    add_parser.add_argument("--recursive", "-r", action="store_true", help="递归处理目录")
    
    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索文档")
    search_parser.add_argument("query", help="搜索查询")
    search_parser.add_argument("--top-k", type=int, default=5, help="返回结果数量")
    
    # 列出文档命令
    list_parser = subparsers.add_parser("list", help="列出文档")
    list_parser.add_argument("--limit", type=int, default=20, help="限制数量")
    
    # 删除文档命令
    delete_parser = subparsers.add_parser("delete", help="删除文档")
    delete_parser.add_parser("document_id", help="文档ID")
    
    # 信息命令
    subparsers.add_parser("info", help="显示知识库信息")
    
    # 交互模式命令
    subparsers.add_parser("interactive", help="进入交互模式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 PeerPortal 知识库管理工具")
    print("=" * 50)
    
    try:
        # 初始化管理器
        manager = KnowledgeBaseManager(
            api_key=args.api_key,
            tenant=args.tenant,
            database=args.database
        )
        
        # 执行命令
        if args.command == "add":
            path = Path(args.path)
            if path.is_file():
                await manager.add_single_document(str(path), args.tenant_id)
            elif path.is_dir():
                await manager.add_directory(str(path), args.tenant_id, args.recursive)
            else:
                print(f"❌ 路径不存在: {args.path}")
        
        elif args.command == "search":
            await manager.search_documents(args.query, args.top_k, args.tenant_id)
        
        elif args.command == "list":
            await manager.list_documents(args.tenant_id, args.limit)
        
        elif args.command == "delete":
            await manager.delete_document(args.document_id)
        
        elif args.command == "info":
            manager.get_collection_info()
        
        elif args.command == "interactive":
            await manager.interactive_mode()
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


"""
留学项目搜索模块
直接连接现有的ChromaDB云端数据进行搜索
"""
import logging
import time
import chromadb
from typing import Dict, List, Any, Optional
from datetime import datetime


class StudyProgramSearch:
    """留学项目搜索类 - 连接现有ChromaDB数据"""
    
    def __init__(
        self,
        api_key: str = "ck-EoDTZTCRe9Qb3LaWGEQA2EGDXoqx5FmZ93Y2KGSfQniL",
        tenant: str = "fd1cb388-55f9-432c-9fc3-b12811c67ee0", 
        database: str = "test-global-cs",
        collection_name: str = "test-global-cs"
    ):
        self.api_key = api_key
        self.tenant = tenant
        self.database = database
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        # 初始化ChromaDB客户端
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化ChromaDB客户端"""
        try:
            self.client = chromadb.CloudClient(
                api_key=self.api_key,
                tenant=self.tenant,
                database=self.database
            )
            self.collection = self.client.get_collection(self.collection_name)
            self.logger.info(f"成功连接到ChromaDB集合: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"ChromaDB连接失败: {e}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """获取数据库基本信息"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_programs": count,
                "database": self.database,
                "tenant": self.tenant
            }
        except Exception as e:
            self.logger.error(f"获取信息失败: {e}")
            return {}
    
    def search_programs(
        self,
        query: str,
        top_k: int = 5,
        region_filter: Optional[str] = None,
        tier_filter: Optional[str] = None,
        university_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索留学项目"""
        try:
            start_time = time.time()
            
            # 构建搜索参数
            search_kwargs = {
                "query_texts": [query],
                "n_results": min(top_k, 10),
                "include": ["documents", "metadatas", "distances"]
            }
            
            # 添加过滤条件（ChromaDB只支持单个过滤条件）
            if region_filter:
                search_kwargs["where"] = {"region": region_filter}
            elif tier_filter:
                search_kwargs["where"] = {"tier": tier_filter}
            elif university_filter:
                search_kwargs["where"] = {"university": university_filter}
            
            # 执行搜索
            results = self.collection.query(**search_kwargs)
            
            # 格式化结果
            formatted_results = []
            if results.get("documents") and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    distance = results["distances"][0][i]
                    score = max(0, 1 - distance)
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    
                    result = {
                        "program_id": results["ids"][0][i] if results.get("ids") else f"program_{i}",
                        "program_name": metadata.get("program_name", "未知项目"),
                        "university": metadata.get("university", "未知大学"),
                        "region": metadata.get("region", "未知地区"),
                        "tier": metadata.get("tier", "未知等级"),
                        "degree_type": metadata.get("degree_type", ""),
                        "language": metadata.get("language", ""),
                        "duration": metadata.get("duration", ""),
                        "score": round(score, 3),
                        "content": content,
                        "metadata": metadata
                    }
                    formatted_results.append(result)
            
            search_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "query": query,
                "results": formatted_results,
                "total_found": len(formatted_results),
                "search_time_ms": search_time
            }
            
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "search_time_ms": 0,
                "error": str(e)
            }
    
    def get_program_by_id(self, program_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取项目详情"""
        try:
            results = self.collection.get(
                ids=[program_id],
                include=["documents", "metadatas"]
            )
            
            if results.get("documents") and results["documents"]:
                metadata = results["metadatas"][0] if results.get("metadatas") else {}
                content = results["documents"][0]
                
                return {
                    "program_id": program_id,
                    "program_name": metadata.get("program_name", "未知项目"),
                    "university": metadata.get("university", "未知大学"),
                    "region": metadata.get("region", "未知地区"),
                    "tier": metadata.get("tier", "未知等级"),
                    "degree_type": metadata.get("degree_type", ""),
                    "language": metadata.get("language", ""),
                    "duration": metadata.get("duration", ""),
                    "thesis_required": metadata.get("thesis_required", False),
                    "internship_required": metadata.get("internship_required", False),
                    "content": content,
                    "metadata": metadata
                }
            return None
            
        except Exception as e:
            self.logger.error(f"获取项目详情失败: {e}")
            return None
    
    def get_programs_by_filter(
        self,
        region: Optional[str] = None,
        tier: Optional[str] = None,
        university: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """根据条件筛选项目"""
        try:
            query_kwargs = {
                "query_texts": [""],
                "n_results": min(limit, 50),
                "include": ["metadatas", "documents"]
            }
            
            # 添加过滤条件
            if region:
                query_kwargs["where"] = {"region": region}
            elif tier:
                query_kwargs["where"] = {"tier": tier}
            elif university:
                query_kwargs["where"] = {"university": university}
            
            results = self.collection.query(**query_kwargs)
            
            programs = []
            if results.get("metadatas") and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    program = {
                        "program_id": results["ids"][0][i] if results.get("ids") else f"program_{i}",
                        "program_name": metadata.get("program_name", "未知项目"),
                        "university": metadata.get("university", "未知大学"),
                        "region": metadata.get("region", "未知地区"),
                        "tier": metadata.get("tier", "未知等级"),
                        "degree_type": metadata.get("degree_type", ""),
                        "language": metadata.get("language", ""),
                        "duration": metadata.get("duration", "")
                    }
                    programs.append(program)
            
            return programs
            
        except Exception as e:
            self.logger.error(f"筛选项目失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            # 获取样本数据统计
            sample_data = self.collection.query(
                query_texts=[""],
                n_results=100,  # 限制数量避免配额问题
                include=["metadatas"]
            )
            
            stats = {
                "total_sampled": 0,
                "regions": {},
                "tiers": {},
                "universities": {}
            }
            
            if sample_data.get("metadatas") and sample_data["metadatas"][0]:
                metadatas = sample_data["metadatas"][0]
                stats["total_sampled"] = len(metadatas)
                
                for metadata in metadatas:
                    # 地区统计
                    region = metadata.get("region", "未知")
                    stats["regions"][region] = stats["regions"].get(region, 0) + 1
                    
                    # 等级统计
                    tier = metadata.get("tier", "未知")
                    stats["tiers"][tier] = stats["tiers"].get(tier, 0) + 1
                    
                    # 大学统计
                    university = metadata.get("university", "未知")
                    stats["universities"][university] = stats["universities"].get(university, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}


# 全局实例
_study_program_search = None


def get_study_program_search() -> StudyProgramSearch:
    """获取留学项目搜索实例（单例）"""
    global _study_program_search
    
    if _study_program_search is None:
        _study_program_search = StudyProgramSearch()
    
    return _study_program_search


"""
OpenAI 提供商实现
提供 OpenAI GPT 和嵌入模型的接口
"""
import time
import logging
from typing import AsyncGenerator, List, Dict, Any
import uuid

from .base_provider import BaseLLMProvider, BaseEmbeddingProvider, LLMResponse, StreamChunk

logger = logging.getLogger(__name__)


class BaseOpenAIClient:
    """OpenAI客户端基类，处理通用逻辑"""

    def __init__(self, api_key: str, base_url: str = None, extra_headers: Dict[str, str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.extra_headers = extra_headers or {}
        self.client = None
        self._http_client = None
        self._setup_client()

    def _setup_client(self):
        """设置 OpenAI 客户端"""
        try:
            from openai import AsyncOpenAI
            import httpx

            # 创建不使用代理的httpx客户端
            from httpx import AsyncHTTPTransport

            # 创建禁用代理的transport
            transport = AsyncHTTPTransport(
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )

            self._http_client = httpx.AsyncClient(
                transport=transport,
                timeout=120.0
            )

            client_kwargs = {
                "api_key": self.api_key,
                "http_client": self._http_client,  # 使用自定义客户端禁用代理
                "max_retries": 3,
            }
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            if self.extra_headers:
                client_kwargs["default_headers"] = self.extra_headers

            self.client = AsyncOpenAI(**client_kwargs)
            logger.info(f"OpenAI client initialized successfully with 120s timeout{' (using custom base_url)' if self.base_url else ''}")
        except ImportError:
            logger.warning("OpenAI package not installed, using mock responses")
            self.client = None

    async def close(self):
        """关闭客户端连接"""
        if self.client:
            try:
                await self.client.close()
                logger.info(f"OpenAI client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing OpenAI client: {e}")
            finally:
                self.client = None

        # 关闭自定义的httpx客户端（如果存在）
        if self._http_client:
            try:
                await self._http_client.aclose()
                logger.info("Custom httpx client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing custom httpx client: {e}")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM 提供商"""

    def __init__(self, api_key: str, base_url: str = None, extra_headers: Dict[str, str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self._client_helper = BaseOpenAIClient(api_key, base_url, extra_headers)

    @property
    def client(self):
        return self._client_helper.client

    async def close(self):
        """关闭客户端连接"""
        await self._client_helper.close()
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> LLMResponse:
        """OpenAI 聊天接口"""
        start_time = time.time()
        
        if not self.client:
            # 模拟响应
            return LLMResponse(
                content="这是一个模拟的OpenAI响应。请安装openai包以使用真实的API。",
                model=model,
                usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                finish_reason="stop",
                response_time=time.time() - start_time
            )
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else {},
                finish_reason=response.choices[0].finish_reason,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            # 返回错误响应
            return LLMResponse(
                content=f"OpenAI API 调用失败: {str(e)}",
                model=model,
                usage={},
                finish_reason="error",
                response_time=time.time() - start_time
            )
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """OpenAI 流式聊天接口"""
        if not self.client:
            # 模拟流式响应
            mock_content = "这是一个模拟的流式响应。请安装openai包以使用真实的API。"
            for i, char in enumerate(mock_content):
                yield StreamChunk(
                    content=char,
                    is_complete=i == len(mock_content) - 1,
                    model=model,
                    chunk_id=str(uuid.uuid4())
                )
            return
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        is_complete=chunk.choices[0].finish_reason is not None,
                        model=chunk.model,
                        chunk_id=chunk.id
                    )
                    
        except Exception as e:
            logger.error(f"OpenAI stream chat error: {e}")
            yield StreamChunk(
                content=f"流式响应错误: {str(e)}",
                is_complete=True,
                model=model,
                chunk_id=str(uuid.uuid4())
            )
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "gpt-4o-mini",
            "gpt-3.5-turbo", 
            "gpt-4",
            "gpt-4-turbo"
        ]
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.client:
                return False
            
            # 简单的API调用测试
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI 嵌入提供商"""

    def __init__(self, api_key: str, base_url: str = None, extra_headers: Dict[str, str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self._client_helper = BaseOpenAIClient(api_key, base_url, extra_headers)

    @property
    def client(self):
        return self._client_helper.client

    async def close(self):
        """关闭客户端连接"""
        await self._client_helper.close()

    async def embed_texts(
        self,
        texts: List[str],
        model: str,
        **kwargs
    ) -> List[List[float]]:
        """OpenAI 文本嵌入接口"""
        if not self.client:
            # 模拟嵌入向量 (1536维)
            return [[0.1] * 1536 for _ in texts]
        
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts,
                **kwargs
            )

            # OpenRouter的响应格式可能与OpenAI不同
            logger.info(f"Embeddings response type: {type(response)}, data type: {type(response.data) if hasattr(response, 'data') else 'no data attr'}")

            if hasattr(response, 'data') and response.data:
                # 标准OpenAI格式
                if isinstance(response.data, list):
                    return [data.embedding for data in response.data]
                else:
                    logger.warning(f"Unexpected response.data type: {type(response.data)}")
                    # 如果是字符串或其他格式，返回模拟数据
                    return [[0.1] * 1536 for _ in texts]
            else:
                logger.warning("Response has no data attribute, using mock embeddings")
                return [[0.1] * 1536 for _ in texts]
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            # 返回模拟嵌入
            return [[0.0] * 1536 for _ in texts]
    
    async def embed_query(
        self,
        query: str,
        model: str,
        **kwargs
    ) -> List[float]:
        """OpenAI 查询嵌入接口"""
        embeddings = await self.embed_texts([query], model, **kwargs)
        return embeddings[0] if embeddings else [0.0] * 1536
    
    async def get_available_models(self) -> List[str]:
        """获取可用嵌入模型列表"""
        return [
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large"
        ]
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.client:
                return False
            
            # 简单的嵌入测试
            await self.embed_query("test", "text-embedding-ada-002")
            return True
        except Exception as e:
            logger.error(f"OpenAI embedding health check failed: {e}")
            return False 
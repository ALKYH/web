"""
AI智能体系统相关的 API 路由
包括留学规划和咨询的智能体服务
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from libs.agents.v2 import (
    create_study_planner,
    create_study_consultant,
    get_architecture_info,
    AgentException,
    PlatformException
)
from libs.agents.v2.config import config_manager
from libs.agents.v2.ai_foundation.llm.manager import llm_manager
from libs.config.settings import settings
from apps.api.v1.deps import get_current_user_optional, get_database, AuthenticatedUser
from apps.api.v1.services import user_credit_logs as credit_service
from apps.schemas.user_credit_logs import CreditTransaction
from libs.database.adapters import DatabaseAdapter

logger = logging.getLogger(__name__)

router = APIRouter()

# 请求和响应模型
class ChatRequest(BaseModel):
    """智能体对话请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="会话ID（可选，会自动生成）")
    enable_rag: bool = Field(False, description="是否启用RAG检索功能（默认为False）")
    model: Optional[str] = Field(None, description="使用的模型名称（可选，使用默认模型）")

class AutoChatRequest(BaseModel):
    """智能体自动选择对话请求"""
    request: ChatRequest
    agent_type: str = Field("study_planner", description="智能体类型 study_planner 或 study_consultant")

class ChatResponse(BaseModel):
    """智能体对话响应"""
    response: str = Field(..., description="智能体回复")
    agent_type: str = Field(..., description="智能体类型")
    version: str = Field("1.0", description="API版本")
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")

class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    is_initialized: bool = Field(..., description="系统是否初始化")
    version: str = Field(..., description="系统版本")
    available_agents: List[str] = Field(..., description="可用的智能体类型")
    external_services: Dict[str, bool] = Field(..., description="外部服务状态")

class ArchitectureInfoResponse(BaseModel):
    """架构信息响应"""
    name: str
    version: str
    author: str
    agent_types: List[str]
    modules: List[str]
    features: List[str]
    tools: List[str]

# 依赖注入：检查系统状�?
async def verify_system_ready():
    """验证系统是否就绪"""
    if not config_manager.is_initialized:
        raise HTTPException(
            status_code=503,
            detail="AI智能体系统尚未初始化，请稍后重试"
        )


# AI会话管理
async def get_or_create_session(db: DatabaseAdapter, user_id: int, session_id: Optional[str] = None) -> str:
    """
    获取或创建AI会话
    简化实现：暂时使用内存中的session_id管理，未来可以扩展为数据库存储
    """
    if session_id:
        return session_id

    # 生成新的会话ID
    return str(uuid.uuid4())


async def log_agent_interaction(db: DatabaseAdapter, user_id: int, agent_type: str, message: str, response: str, session_id: str):
    """
    记录AI智能体交互日志
    """
    try:
        # 这里可以记录到数据库中，暂时记录到日志
        logger.info(f"AI交互: user={user_id}, agent={agent_type}, session={session_id}, message_length={len(message)}")

        # 扣除积分（如果需要的话）
        # await credit_service.award_credits(db, CreditTransaction(
        #     user_id=user_id,
        #     credit_type="learning_points",
        #     amount=-1,  # 每次对话消耗1积分
        #     description=f"AI{agent_type}对话",
        #     reference_type="ai_interaction"
        # ))

    except Exception as e:
        logger.error(f"记录AI交互失败: {e}")


async def check_user_credits(db: DatabaseAdapter, user_id: int) -> bool:
    """
    检查用户是否有足够的积分使用AI服务
    """
    try:
        balance = await credit_service.get_user_credit_balance(db, user_id)
        # 检查是否有足够的积分（这里可以设置最低要求）
        return balance.total_points >= 0  # 暂时允许所有用户使用
    except Exception as e:
        logger.error(f"检查用户积分失败: {e}")
        return True  # 出错时允许使用

# API路由
@router.get("/status", response_model=SystemStatusResponse, summary="获取系统状态")
async def get_system_status():
    """
    获取智能体系统的运行状态

    返回系统初始化状态、可用服务等信息
    """
    try:
        status = config_manager.get_config_status()
        info = get_architecture_info()
        
        return SystemStatusResponse(
            is_initialized=status['is_initialized'],
            version=info['version'],
            available_agents=info['agent_types'],
            external_services=status['external_services']
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统状态失败")

@router.get("/info", response_model=ArchitectureInfoResponse, summary="获取架构信息")
async def get_system_info():
    """
    获取智能体系统的架构信息

    返回系统版本、支持的智能体类型、功能模块等详细信息
    """
    try:
        info = get_architecture_info()
        return ArchitectureInfoResponse(**info)
    except Exception as e:
        logger.error(f"获取架构信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取架构信息失败")

@router.post("/planner/chat", response_model=ChatResponse, summary="留学规划师对话")
async def chat_with_planner(
    request: ChatRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
    db: DatabaseAdapter = Depends(get_database),
    _: None = Depends(verify_system_ready)
):
    """
    与留学规划师智能体对话

    留学规划师专注于
    - 个性化留学申请策略制定
    - 选校建议和专业推荐
    - 申请时间规划
    - 引路人和服务推荐
    """
    try:
        # 处理用户身份：支持匿名用户和认证用户
        if current_user:
            user_id = int(current_user.id)
            # 认证用户检查积分
            if not await check_user_credits(db, user_id):
                raise HTTPException(status_code=402, detail="积分不足，请充值后继续使用")
        else:
            # 匿名用户使用临时UUID
            user_id = str(uuid.uuid4())  # 匿名用户ID

        # 获取或创建会话
        session_id = await get_or_create_session(db, user_id, request.session_id)

        # 创建留学规划师智能体
        model_name = request.model or settings.DEFAULT_MODEL
        planner = create_study_planner(str(user_id), model_name=model_name, enable_rag=request.enable_rag)

        # 执行对话
        response = await planner.execute(request.message)

        # 记录交互日志
        await log_agent_interaction(db, user_id, "study_planner", request.message, response, session_id)

        return ChatResponse(
            response=response,
            agent_type="study_planner",
            user_id=str(user_id),
            session_id=session_id
        )

    except HTTPException:
        raise
    except AgentException as e:
        logger.error(f"留学规划师执行失败: {e}")
        raise HTTPException(status_code=400, detail=f"智能体错误: {e.message}")
    except PlatformException as e:
        logger.error(f"平台错误: {e}")
        raise HTTPException(status_code=500, detail=f"系统错误: {e.message}")
    except Exception as e:
        logger.error(f"留学规划师对话异常: {e}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

@router.post("/consultant/chat", response_model=ChatResponse, summary="留学咨询师对话")
async def chat_with_consultant(
    request: ChatRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
    db: DatabaseAdapter = Depends(get_database),
    _: None = Depends(verify_system_ready)
):
    """
    与留学咨询师智能体对话

    留学咨询师专注于
    - 留学政策和流程解释
    - 院校和专业信息咨询
    - 签证和生活问题解答
    - 留学经验分享
    """
    try:
        # 处理用户身份：支持匿名用户和认证用户
        if current_user:
            user_id = int(current_user.id)
            # 认证用户检查积分
            if not await check_user_credits(db, user_id):
                raise HTTPException(status_code=402, detail="积分不足，请充值后继续使用")
        else:
            # 匿名用户使用临时UUID
            user_id = str(uuid.uuid4())  # 匿名用户ID

        # 获取或创建会话
        session_id = await get_or_create_session(db, user_id, request.session_id)

        # 创建留学咨询师智能体
        model_name = request.model or settings.DEFAULT_MODEL
        consultant = create_study_consultant(str(user_id), model_name=model_name, enable_rag=request.enable_rag)

        # 执行对话
        response = await consultant.execute(request.message)

        # 记录交互日志
        await log_agent_interaction(db, user_id, "study_consultant", request.message, response, session_id)

        return ChatResponse(
            response=response,
            agent_type="study_consultant",
            user_id=str(user_id),
            session_id=session_id
        )

    except HTTPException:
        raise
    except AgentException as e:
        logger.error(f"留学咨询师执行失败: {e}")
        raise HTTPException(status_code=400, detail=f"智能体错误: {e.message}")
    except PlatformException as e:
        logger.error(f"平台错误: {e}")
        raise HTTPException(status_code=500, detail=f"系统错误: {e.message}")
    except Exception as e:
        logger.error(f"留学咨询师对话异常: {e}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="智能体自动选择对话",
    description="""
    通用对话接口，后端根据 `agent_type` 自动路由到对应智能体。

    - 默认返回一次性完整响应（JSON）。
    - 传入 `stream=true` 时，返回 SSE 流式响应（`text/event-stream`）。
    - 为了最小改动，流式模式当前以增量分块的方式推送已生成文本，后续可无缝替换为底层LLM的真实流式（`llm_manager.stream_chat`）。
    """
)
async def chat_with_auto_agent(
    auto_request: AutoChatRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
    db: DatabaseAdapter = Depends(get_database),
    _: None = Depends(verify_system_ready),
    stream: bool = Query(False, description="是否启用SSE流式响应")
):
    """
    智能选择智能体进行对话

    根据指定的智能体类型自动路由到相应的智能体：
    - study_planner: 留学规划师
    - study_consultant: 留学咨询师
    """
    try:
        # 处理用户身份：支持匿名用户和认证用户
        if current_user:
            user_id = int(current_user.id)
            # 认证用户检查积分
            if not await check_user_credits(db, user_id):
                raise HTTPException(status_code=402, detail="积分不足，请充值后继续使用")
        else:
            # 匿名用户使用临时UUID
            user_id = str(uuid.uuid4())  # 匿名用户ID

        # 获取或创建会话
        session_id = await get_or_create_session(db, user_id, auto_request.request.session_id)

        # 使用用户指定的模型或默认模型
        model_name = auto_request.request.model or settings.DEFAULT_MODEL

        if auto_request.agent_type == "study_planner":
            agent = create_study_planner(str(user_id), model_name=model_name, enable_rag=auto_request.request.enable_rag)
        elif auto_request.agent_type == "study_consultant":
            agent = create_study_consultant(str(user_id), model_name=model_name, enable_rag=auto_request.request.enable_rag)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的智能体类型 {auto_request.agent_type}。支持的类型: study_planner, study_consultant"
            )

        # 执行对话
        response_text = await agent.execute(auto_request.request.message)

        # 记录交互日志
        await log_agent_interaction(db, user_id, auto_request.agent_type, auto_request.request.message, response_text, session_id)

        if not stream:
            return ChatResponse(
                response=response_text,
                agent_type=auto_request.agent_type,
                user_id=str(user_id),
                session_id=session_id
            )

        # 流式响应（SSE）：对接底层 LLM 真流式输出
        import asyncio

        async def sse_emitter():
            try:
                # 握手事件
                yield (f"event: meta\n"
                       f"data: {{\"agent_type\": \"{auto_request.agent_type}\", \"session_id\": \"{session_id}\"}}\n\n")

                # 根据智能体类型设置系统提示
                system_prompt = "你是一个有用的AI助手。"
                if auto_request.agent_type == "study_planner":
                    system_prompt = "你是专业的留学规划师，回答要结构化、可执行。"
                elif auto_request.agent_type == "study_consultant":
                    system_prompt = "你是专业的留学咨询师，回答要准确、清晰、友好。"

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": auto_request.request.message}
                ]

                # 使用用户指定的模型或默认模型
                model_name = auto_request.request.model or settings.DEFAULT_MODEL

                async for chunk in llm_manager.stream_chat(
                    tenant_id=str(user_id),
                    model_name=model_name,
                    messages=messages,
                    temperature=0.7,
                    stream=True
                ):
                    if getattr(chunk, 'delta', None):
                        yield f"data: {chunk.delta}\n\n"
                    elif getattr(chunk, 'content', None):
                        yield f"data: {chunk.content}\n\n"

                # 结束事件
                yield "event: done\ndata: [DONE]\n\n"
            except Exception as e:
                yield f"event: error\ndata: {str(e)}\n\n"

        return StreamingResponse(sse_emitter(), media_type="text/event-stream")

    except HTTPException:
        raise
    except AgentException as e:
        logger.error(f"智能体执行失败: {e}")
        raise HTTPException(status_code=400, detail=f"智能体错误: {e.message}")
    except PlatformException as e:
        logger.error(f"平台错误: {e}")
        raise HTTPException(status_code=500, detail=f"系统错误: {e.message}")
    except Exception as e:
        logger.error(f"智能体对话异常: {e}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

# 健康检查路由
@router.get("/health", summary="智能体系统健康检查")
async def health_check():
    """智能体系统健康检查"""
    try:
        status = config_manager.get_config_status()
        return {
            "status": "healthy" if status['is_initialized'] else "initializing",
            "system": "PeerPortal AI智能体系统",
            "focus": "留学规划与咨询",
            "agents": ["study_planner", "study_consultant"],
            "timestamp": "2024-07-26"
        }
    except Exception as e:
        logger.error(f"健康检查失�? {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-07-26"
        }
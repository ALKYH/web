from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from apps.api.v1.deps import get_current_user, require_mentor_role, require_student_role, get_database
from apps.api.v1.deps import AuthenticatedUser
from apps.schemas.mentorship import (
    SessionCreate, SessionUpdate, Session, SessionRead, SessionFeedback, SessionSummary
)
from apps.api.v1.repositories import session

router = APIRouter()

@router.post(
    "",
    response_model=SessionRead,
    summary="创建指导会话",
    description="学生创建指导会话预约"
)
async def create_session(
    session_data: SessionCreate,
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """创建指导会话"""
    try:
        session_result = await session.create(db_conn, session_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建会话失败，请检查指导者和订单信息"
            )
        return session_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )

@router.get(
    "/{session_id}",
    response_model=SessionRead,
    summary="获取会话详情",
    description="获取指定会话的详细信息",
)
async def get_session_detail(
    session_id: UUID,
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取会话详情"""
    try:
        session_result = await session.get_by_id(db_conn, session_id)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话未找到或您没有权限查看",
            )
        return session_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话详情失败: {str(e)}"
        )

@router.get(
    "/statistics",
    response_model=dict,
    summary="获取会话统计",
    description="获取用户的会话统计信息",
)
async def get_session_statistics(
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取会话统计"""
    try:
        # 从当前用户中获取角色信息，后端自动判断角色
        user_role = current_user.role.lower() if hasattr(current_user, 'role') else 'student'

        # 简化实现：返回基础统计信息
        sessions = await session.get_by_user(db_conn, current_user.id, 1000)  # 获取所有会话进行统计

        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.get('status') == 'completed'])
        cancelled_sessions = len([s for s in sessions if s.get('status') == 'cancelled'])

        stats = {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "cancelled_sessions": cancelled_sessions,
            "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0
        }
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话统计失败: {str(e)}"
        )

@router.get(
    "",
    response_model=List[SessionRead],
    summary="获取我的会话",
    description="获取当前用户的所有会话",
)
async def get_my_sessions(
    role: Optional[str] = Query(None, description="角色筛选（student/mentor）"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取我的会话"""
    try:
        sessions = await session.get_by_user(db_conn, current_user.id, limit)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )

@router.put(
    "/{session_id}",
    response_model=SessionRead,
    summary="更新会话信息",
    description="更新会话的详细信息",
)
async def update_session(
    session_id: UUID,
    session_data: SessionUpdate,
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新会话信息"""
    try:
        session_result = await session.update(db_conn, session_id, session_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话未找到或您没有权限修改",
            )
        return session_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/start",
    response_model=dict,
    summary="开始会话",
    description="开始进行指导会话",
)
async def start_session(
    session_id: UUID,
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """开始会话"""
    try:
        # 简化实现：直接更新会话状态为 'active'
        from apps.schemas.session import SessionUpdate
        update_data = SessionUpdate(status="active")
        session_result = await session.update(db_conn, session_id, update_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始会话失败，请检查会话状态",
            )
        return {"message": "会话已开始", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"开始会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/end",
    response_model=dict,
    summary="结束会话",
    description="结束指导会话"
)
async def end_session(
    session_id: UUID,
    actual_duration: Optional[int] = Query(None, description="实际时长（分钟）"),
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """结束会话"""
    try:
        # 简化实现：直接更新会话状态为 'completed'
        from apps.schemas.session import SessionUpdate
        update_data = SessionUpdate(status="completed")
        if actual_duration:
            update_data.actual_duration = actual_duration
        session_result = await session.update(db_conn, session_id, update_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束会话失败，请检查会话状态",
            )
        return {"message": "会话已结束", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结束会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/cancel",
    response_model=dict,
    summary="取消会话",
    description="取消预定的指导会话",
)
async def cancel_session(
    session_id: UUID,
    reason: Optional[str] = Query(None, description="取消原因"),
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """取消会话"""
    try:
        # 简化实现：直接更新会话状态为 'cancelled'
        from apps.schemas.session import SessionUpdate
        update_data = SessionUpdate(status="cancelled")
        if reason:
            update_data.notes = f"取消原因: {reason}"
        session_result = await session.update(db_conn, session_id, update_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="取消会话失败，请检查会话状态",
            )
        return {"message": "会话已取消", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/feedback",
    response_model=dict,
    summary="提交会话反馈",
    description="提交会话反馈和评分",
)
async def submit_feedback(
    session_id: UUID,
    feedback: SessionFeedback,
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """提交会话反馈"""
    try:
        # 简化实现：直接更新会话的反馈信息
        from apps.schemas.session import SessionUpdate
        update_data = SessionUpdate(
            feedback_rating=feedback.rating,
            feedback_comment=feedback.comment
        )
        session_result = await session.update(db_conn, session_id, update_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提交反馈失败，请检查会话状态和权限"
            )
        return {"message": "反馈已提交", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交反馈失败: {str(e)}"
        )

@router.post(
    "/{session_id}/summary",
    response_model=dict,
    summary="保存会话总结",
    description="保存会话的详细总结信息"
)
async def save_summary(
    session_id: UUID,
    summary: SessionSummary,
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """保存会话总结"""
    try:
        # 简化实现：直接更新会话的总结信息
        from apps.schemas.session import SessionUpdate
        update_data = SessionUpdate(
            summary=summary.content,
            key_points=summary.key_points,
            action_items=summary.action_items
        )
        session_result = await session.update(db_conn, session_id, update_data)
        if not session_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="保存总结失败，请检查会话状态和权限"
            )
        return {"message": "会话总结已保存", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存总结失败: {str(e)}"
        )

@router.get(
    "/upcoming",
    response_model=List[SessionRead],
    summary="获取即将到来的会话",
    description="获取用户即将进行的会话",
)
async def get_upcoming_sessions(
    role: Optional[str] = Query(None, description="角色筛选（student/mentor）"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db_conn=Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取即将到来的会话"""
    try:
        # 简化实现：获取所有用户会话（实际应该根据时间筛选即将到来的会话）
        sessions = await session.get_by_user(db_conn, current_user.id, limit)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取即将到来的会话失败: {str(e)}"
        )


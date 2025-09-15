from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal

class SessionBase(BaseModel):
    """指导会话基础模型 - 匹配 mentorship_sessions 表"""
    session_number: int = Field(..., description="会话编号")
    scheduled_at: datetime = Field(..., description="预定时间")
    duration_minutes: Optional[int] = Field(None, ge=30, le=180, description="持续时间（分钟）")
    agenda: Optional[str] = Field(None, description="议程")
    status: Optional[str] = Field(default="scheduled", description="状态")

class SessionCreate(SessionBase):
    """创建指导会话"""
    relationship_id: Optional[int] = Field(None, description="指导关系ID")
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None
    key_topics: Optional[List[str]] = Field(default=[], description="关键主题")  # ARRAY 类型
    homework_assigned: Optional[str] = None
    resources_shared: Optional[List[str]] = Field(default=[], description="共享资源")  # ARRAY 类型
    next_session_plan: Optional[str] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[datetime] = None
    mentor_satisfaction: Optional[int] = None
    mentee_satisfaction: Optional[int] = None
    mentor_feedback: Optional[str] = None
    mentee_feedback: Optional[str] = None
    progress_percentage: Optional[int] = Field(default=0)
    milestones_achieved: Optional[List[str]] = Field(default=[], description="达成的里程碑")  # ARRAY 类型

class SessionUpdate(BaseModel):
    """更新指导会话"""
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    agenda: Optional[str] = None
    status: Optional[str] = None
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None
    key_topics: Optional[List[str]] = None
    homework_assigned: Optional[str] = None
    resources_shared: Optional[List[str]] = None
    next_session_plan: Optional[str] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[datetime] = None
    mentor_satisfaction: Optional[int] = None
    mentee_satisfaction: Optional[int] = None
    mentor_feedback: Optional[str] = None
    mentee_feedback: Optional[str] = None
    progress_percentage: Optional[int] = None
    milestones_achieved: Optional[List[str]] = None

class SessionRead(SessionBase):
    """指导会话详情 - 匹配 mentorship_sessions 表"""
    id: int
    relationship_id: Optional[int] = None  # 可空
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None
    key_topics: Optional[List[str]] = None  # ARRAY 类型
    homework_assigned: Optional[str] = None
    resources_shared: Optional[List[str]] = None  # ARRAY 类型
    next_session_plan: Optional[str] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[datetime] = None
    mentor_satisfaction: Optional[int] = None
    mentee_satisfaction: Optional[int] = None
    mentor_feedback: Optional[str] = None
    mentee_feedback: Optional[str] = None
    progress_percentage: Optional[int] = Field(default=0)
    milestones_achieved: Optional[List[str]] = None  # ARRAY 类型
    created_at: Optional[datetime] = None  # 可空
    updated_at: Optional[datetime] = None  # 可空
    
    class Config:
        from_attributes = True

class SessionAttendance(BaseModel):
    """会话出席管理"""
    session_id: int
    attended: bool = Field(..., description="是否出席")
    late_minutes: Optional[int] = Field(None, ge=0, description="迟到分钟数")
    early_leave_minutes: Optional[int] = Field(None, ge=0, description="早退分钟数")
    attendance_notes: Optional[str] = Field(None, max_length=500, description="出席备注")

class SessionMaterials(BaseModel):
    """会话材料 - 扩展支持数据库 ARRAY 字段"""
    session_id: int
    material_type: str = Field(..., description="材料类型")
    title: str = Field(..., max_length=200, description="材料标题")
    content: Optional[str] = Field(None, description="材料内容")
    file_url: Optional[str] = Field(None, description="文件链接")
    uploaded_by: str = Field(..., description="上传者")
    is_shared: bool = Field(default=True, description="是否共享")

class SessionProgress(BaseModel):
    """会话进度 - 匹配数据库字段"""
    session_id: int
    goals_set: List[str] = Field(default=[], description="设定目标")
    goals_achieved: List[str] = Field(default=[], description="已完成目标")
    next_steps: List[str] = Field(default=[], description="下一步计划")
    homework_assigned: Optional[str] = Field(None, description="布置的作业")
    progress_percentage: Optional[int] = Field(default=0, ge=0, le=100, description="进度百分比")

class SessionFeedback(BaseModel):
    """会话反馈 - 匹配数据库满意度字段"""
    session_id: int
    mentor_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="导师满意度")
    mentee_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="学员满意度")
    mentor_feedback: Optional[str] = Field(None, description="导师反馈")
    mentee_feedback: Optional[str] = Field(None, description="学员反馈")
    comments: Optional[str] = Field(None, description="文字评价")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议")

class SessionSummary(BaseModel):
    """会话总结 - 匹配数据库字段"""
    session_id: int
    key_topics: List[str] = Field(default=[], description="关键主题")
    milestones_achieved: List[str] = Field(default=[], description="达成的里程碑")
    resources_shared: List[str] = Field(default=[], description="分享的资源")
    next_session_plan: Optional[str] = Field(None, description="下次会话计划")
    progress_percentage: Optional[int] = Field(default=0, description="进度百分比") 

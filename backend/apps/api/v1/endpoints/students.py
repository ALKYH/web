"""
学生档案相关的 API 路由
包括学生档案的创建、查询、更新等功能
"""
from fastapi import APIRouter, Depends, status

from apps.schemas.student import StudentProfile, StudentCreate, StudentUpdate
from apps.api.v1.services import student
from apps.api.v1.deps import get_current_user, require_student_role, AuthenticatedUser, get_database
from libs.database.adapters import DatabaseAdapter

router = APIRouter()


@router.post(
    "/", 
    response_model=StudentProfile, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_student_role)],
    summary="创建学生档案",
    description="为当前登录的学生用户创建个人档案"
)
async def create_student_profile(
    profile_in: StudentCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """为当前登录的学生用户创建一份个人档案"""
    return await student.create_student_profile(db, int(current_user.id), profile_in)


@router.get(
    "/me", 
    response_model=StudentProfile,
    dependencies=[Depends(require_student_role)],
    summary="获取当前学生用户的档案",
    description="获取当前登录学生用户的个人档案"
)
async def get_my_student_profile(
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """获取当前登录学生用户的个人档案"""
    return await student.get_student_profile_by_user_id(db, int(current_user.id))


@router.put(
    "/me", 
    response_model=StudentProfile,
    dependencies=[Depends(require_student_role)],
    summary="更新当前学生用户的档案",
    description="更新当前登录学生用户的个人档案"
)
async def update_my_student_profile(
    profile_in: StudentUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """更新当前登录学生用户的个人档案"""
    return await student.update_student_profile(db, int(current_user.id), profile_in)


@router.get(
    "/{profile_id}", 
    response_model=StudentProfile,
    summary="根据ID获取学生档案",
    description="根据学生档案ID获取详细信息"
)
async def get_student_profile_by_id(
    profile_id: int,
    db: DatabaseAdapter = Depends(get_database),
):
    """根据学生档案ID获取详细信息"""
    return await student.get_student_profile_by_id(db, profile_id)
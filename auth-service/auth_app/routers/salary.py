"""Module with salary routes."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase.dal.salary import SalaryDAL
from auth_app.dbase.dal.user import UserDAL
from auth_app.dependencies import get_active_user, get_session

__all__ = [
    'router',
]

router = APIRouter(
    prefix='/salary',
    tags=['salary']
)


@router.get('/', response_model=models.SalaryInfo)
async def get_salary(
        user: models.ActiveUser = Depends(get_active_user),
        session: AsyncSession = Depends(get_session)) -> models.SalaryInfo:
    """Return salary info for current user.

    Args:
        user: pydantic ActiveUser model
        session: AsyncSession

    Returns: pydantic Salary model

    """
    user_dal = UserDAL(session=session)
    user_name = await user_dal.get_by_id(id_=user.id_)
    if not user_name:
        raise HTTPException(
            status_code=400,
            detail='User not found'
        )

    salary_dal = SalaryDAL(session=session)
    salary_info = await salary_dal.get_by_user_id(id_=user.id_)
    if not salary_info:
        raise HTTPException(
            status_code=400,
            detail='Salary info not found'
        )
    return salary_info

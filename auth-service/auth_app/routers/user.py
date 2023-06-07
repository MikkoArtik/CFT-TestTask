"""Module with user routes."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase.dal.salary import SalaryDAL
from auth_app.dbase.dal.user import UserDAL
from auth_app.dependencies import get_session

__all__ = [
    'router',
]

router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.post('/add', response_model=models.Response)
async def sign_up(
        user: models.User, salary: models.UserSalary,
        session: AsyncSession = Depends(get_session)
) -> models.Response:
    """Create new user.

    Args:
        user: pydantic User model
        salary: pydantic UserSalary model
        session: AsyncSession

    Returns: Response pydantic model

    """
    user_dal = UserDAL(session=session)
    if await user_dal.is_exist(login=user.login):
        raise HTTPException(
            status_code=401,
            detail=f'User with login {user.login} is exist'
        )
    await user_dal.add(user=user)
    user_id = await user_dal.get_id_by_login(login=user.login)

    salary_dal = SalaryDAL(session=session)
    await salary_dal.add(
        salary_info=models.SalaryInfo(
            user_id=user_id,
            name=user.name,
            value=salary.value,
            target_date=salary.target_date
        )
    )
    return models.Response(message='User and salary info is was added.')

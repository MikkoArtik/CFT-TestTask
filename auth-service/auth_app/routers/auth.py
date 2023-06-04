"""Module with auth routes."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase.dal.token_ import TokenDAL
from auth_app.dbase.dal.user import UserDAL
from auth_app.dependencies import get_session

__all__ = [
    'router',
]


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/', response_model=models.Token)
async def auth(user: models.User,
               session: AsyncSession = Depends(get_session)) -> models.Token:
    """Return token after auth.

    Args:
        user: pydantic User model
        session: AsyncSession

    Returns: pydantic Token model

    """
    user_dal = UserDAL(session=session)
    if not await user_dal.is_exist(login=user.login):
        raise HTTPException(
            status_code=400,
            detail='Login not found'
        )
    if not await user_dal.is_valid_login_password_pair(user=user):
        raise HTTPException(
            status_code=400,
            detail='Incorrect login or password'
        )
    token_dal = TokenDAL(session=session)

    user_id = await user_dal.get_id_by_login(login=user.login)
    await token_dal.add(user_id=user_id)

    return await token_dal.get_by_user_id(id_=user_id)

"""Module with FastAPI dependencies."""

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase.connection import CustomConnection
from auth_app.dbase.dal.token_ import TokenDAL
from auth_app.dbase.dal.user import UserDAL

__all__ = [
    'get_session',
    'get_active_user'
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth')


async def get_session() -> AsyncSession:
    """Return async session context.

    Returns: AsyncSession

    """
    conn = CustomConnection()
    async with conn.async_session as session:
        yield session


async def get_active_user(
        token_value: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
) -> models.ActiveUser:
    """Return active user information after authorization.

    Args:
        token_value: pydantic model Token
        session: AsyncSession

    Returns: pydantic ActiveUser model

    """
    token_dal = TokenDAL(session=session)
    user_id = await token_dal.get_user_id(token_value=token_value)
    if user_id < 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials'
        )

    token = await token_dal.get_by_user_id(id_=user_id)
    if not token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is expired'
        )

    user_dal = UserDAL(session=session)
    user = await user_dal.get_by_id(id_=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User info not found'
        )

    return models.ActiveUser(
        id_=user_id,
        name=user.name
    )

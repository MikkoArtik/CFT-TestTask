"""Module with Token database table operations."""

from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.base import BaseDAL

__all__ = [
    'TokenDAL',
]

EXPIRES_SIZE = timedelta(minutes=5)


class TokenDAL(BaseDAL):
    """Class with token table methods."""

    def __init__(self, session: AsyncSession):
        """Initialize class method.

        Args:
            session: AsyncSession
        """
        super().__init__(session=session)

    async def delete(self, token_value: str) -> bool:
        """Remove token from database by token value.

        Args:
            token_value: str

        Returns: bool

        """
        query = delete(orm.Token).where(orm.Token.value == token_value)
        await self.session.execute(query)
        return await self.is_success_changing_query()

    async def get_by_user_id(self, id_: int) -> models.Token:
        """Return token by user id.

        Args:
            id_: int

        Returns: str

        """
        query = select(orm.Token).where(orm.Token.user_id == id_)
        record = await self.session.execute(query)
        token_orm = record.scalar()
        if not token_orm:
            return models.Token()
        return models.Token(token=token_orm.token, expires=token_orm.expires)

    async def get_user_id(self, token: str) -> int:
        """Return user id by token value.

        Args:
            token: str

        Returns: int

        """
        query = select(orm.Token).where(orm.Token.token == token)
        record = await self.session.execute(query)
        token_orm = record.scalar()
        if not token_orm:
            return -1
        return token_orm.user_id

    async def add(self, user_id: int) -> bool:
        """Add token to database by user id.

        Args:
            user_id: int

        Returns: bool

        """
        current_token = await self.get_by_user_id(id_=user_id)
        is_create = False
        if not current_token:
            is_create = True
        else:
            if not current_token.is_valid:
                await self.delete(token=current_token.token)
                is_create = True

        if is_create:
            token = orm.Token(
                expires=datetime.now() + EXPIRES_SIZE,
                user_id=user_id
            )
            self.session.add(token)
            return await self.is_success_changing_query()
        else:
            return True

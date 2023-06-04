"""Module with base table api class."""

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = [
    'BaseDAL',
]


class BaseDAL:
    """Class which save changing query."""

    def __init__(self, session: AsyncSession):
        """Initialize base table API.

        Args:
            session: AsyncSession
        """
        self.__session = session

    @property
    def session(self) -> AsyncSession:
        """Return session object.

        Returns: AsyncSession

        """
        return self.__session

    async def is_success_changing_query(self) -> bool:
        """Return changing query status.

        Returns: True - if success, else - False
        """
        try:
            await self.session.commit()
            return True
        except DBAPIError:
            await self.session.rollback()
            return False

    async def get_by_id(self, id_: int):
        """Return object by id value.

        Args:
            id_: int

        Returns: Pydantic model

        """
        pass

    async def add(self, **kwargs):
        """Add object to database.

        Args:
            **kwargs: named arguments

        Returns: None

        """
        pass

    async def update(self, **kwargs):
        """Update record in database table.

        Args:
            **kwargs: named arguments

        Returns: None

        """
        pass

    async def delete(self, **kwargs):
        """Delete record in database table.

        Args:
            **kwargs: named arguments

        Returns: None

        """
        pass

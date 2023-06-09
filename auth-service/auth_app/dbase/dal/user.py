"""Module with User database table operations."""

import hashlib
import random
import string
from typing import Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.base import BaseDAL

__all__ = [
    'UserDAL',
]

HASH_SALT_DELIMITER = '^'


def generate_random_string(length: int = 10) -> str:
    """Return random string.

    Args:
        length: string length

    Returns: str

    """
    if not length:
        return ''
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def get_hashed_password(password: str, salt: str) -> str:
    """Return hashed password.

    Args:
        password: str
        salt: str

    Returns: str

    """
    return hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode(),
        salt=salt.encode(),
        iterations=20000
    ).hex()


def is_valid_password(password: str, hashed_password: str) -> bool:
    """Check password validation.

    Args:
        password: input password
        hashed_password: hashed password

    Returns: bool

    """
    hashed_password, salt = hashed_password.split(HASH_SALT_DELIMITER)
    return get_hashed_password(password, salt) == hashed_password


class UserDAL(BaseDAL):
    """Class with user table methods."""

    def __init__(self, session: AsyncSession):
        """Initialize class method.

        Args:
            session: AsyncSession
        """
        super().__init__(session=session)

    async def get_by_id(self, id_: int) -> Union[models.ActiveUser, None]:
        """Return User info by id.

        Args:
            id_: int

        Returns: pydantic ActiveUser model

        """
        query = select(orm.User).where(orm.User.id_ == id_)
        user_orm = (await self.session.execute(query)).scalar()
        if not user_orm:
            return
        return models.ActiveUser(
            id_=user_orm.id_,
            name=user_orm.name
        )

    async def get_id_by_login(self, login: str) -> int:
        """Return record id by login.

        Args:
            login: str

        Returns: bool

        """
        query = select(orm.User).where(
            func.lower(orm.User.login) == login.lower()
        )
        user_orm = (await self.session.execute(query)).scalar()
        if not user_orm:
            return -1
        return user_orm.id_

    async def is_exist(self, login: str) -> bool:
        """Return user existing by login.

        Args:
            login: str

        Returns: bool

        """
        id_value = await self.get_id_by_login(login=login)
        return id_value != -1

    async def is_valid_login_password_pair(self,
                                           user: models.UserAuth) -> bool:
        """Return validation by login and password.

        Args:
            user: pydantic UserAuth model

        Returns: bool

        """
        query = select(orm.User).where(
            func.lower(orm.User.login) == user.login.lower()
        )
        user_orm = (await self.session.execute(query)).scalar()
        if not user_orm:
            return False
        return is_valid_password(
            password=user.password,
            hashed_password=user_orm.hashed_password
        )

    async def add(self, user: models.User) -> bool:
        """Add user to database.

        Args:
            user: pydantic User model

        Returns: bool

        """
        is_exist = await self.is_exist(login=user.login)
        if is_exist:
            return False

        salt = generate_random_string()
        hashed_password = get_hashed_password(
            password=user.password,
            salt=salt
        )
        user_orm = orm.User(
            name=user.name,
            login=user.login,
            hashed_password=f'{hashed_password}{HASH_SALT_DELIMITER}{salt}'
        )
        self.session.add(user_orm)
        return await self.is_success_changing_query()

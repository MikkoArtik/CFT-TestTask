import asyncio
import random
from datetime import datetime

import dotenv
import pytest
import pytest_asyncio
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.dbase import orm
from auth_app.dbase.connection import CustomConnection
from auth_app.dbase.dal.user import (HASH_SALT_DELIMITER,
                                     generate_random_string,
                                     get_hashed_password)

dotenv.load_dotenv()


@pytest.fixture
def get_dbase_session():
    return AsyncSession(
        CustomConnection().engine,
        expire_on_commit=False
    )


@pytest.fixture(scope='session')
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def fill_user_table():
    session = AsyncSession(
        CustomConnection().engine,
        expire_on_commit=False
    )

    for i in range(10):
        salt = generate_random_string(length=5)
        hashed_password = get_hashed_password(
            password=f'qwerty={i}', salt=salt
        )
        full_hashed_password = HASH_SALT_DELIMITER.join(
            (hashed_password, salt)
        )
        project = orm.User(
            name=f'test-user-{i}',
            login=f'test-login={i}',
            hashed_password=full_hashed_password
        )
        session.add(project)
    await session.commit()

    yield


@pytest_asyncio.fixture(scope='session', autouse=True)
async def clear_user_table():
    yield
    session = AsyncSession(
        CustomConnection().engine,
        expire_on_commit=False
    )

    query = delete(orm.User).where(orm.User.login.contains('test'))
    await session.execute(query)
    await session.commit()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def fill_salary_table(fill_user_table):
    session = AsyncSession(
        CustomConnection().engine,
        expire_on_commit=False
    )

    query = select(orm.User.id_).where(
        orm.User.login.contains('test')
    )
    records = await session.execute(query)
    for user_id in records.scalars():
        salary = orm.Salary(
            value=random.randint(10, 10000),
            target_date=datetime(
                year=2023,
                month=random.randint(1, 12),
                day=random.randint(1, 28)
            ),
            user_id=user_id
        )
        session.add(salary)
    await session.commit()

    yield

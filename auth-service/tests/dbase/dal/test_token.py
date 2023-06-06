import random
from typing import List
from uuid import uuid4

import pytest
from hamcrest import assert_that, equal_to, is_
from sqlalchemy import func, select

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.token_ import TokenDAL


class TestTokenDAL:
    @pytest.mark.asyncio
    async def test_delete(self, get_dbase_session):
        query = select(orm.User.id_)
        record = await get_dbase_session.execute(query)
        user_ids: List[int] = record.scalars().all()
        user_id: int = random.choice(user_ids)

        table_dal = TokenDAL(session=get_dbase_session)
        await table_dal.add(user_id=user_id)

        query = select(orm.Token.value).where(orm.Token.user_id == user_id)
        record = await get_dbase_session.execute(query)
        token_value: str = record.scalar()

        await table_dal.delete(token_value=token_value)
        query = select(func.count(orm.Token.value)).where(
            orm.Token.user_id == user_id
        )
        record = await get_dbase_session.execute(query)
        is_exist = True if record.scalar() else False

        assert_that(
            actual_or_assertion=is_exist,
            matcher=is_(False)
        )

    @pytest.mark.asyncio
    async def test_add(self, get_dbase_session):
        query = select(orm.User.id_)
        record = await get_dbase_session.execute(query)
        user_ids: List[int] = record.scalars().all()
        user_id: int = random.choice(user_ids)

        table_dal = TokenDAL(session=get_dbase_session)
        is_success = await table_dal.add(user_id=user_id)

        assert_that(
            actual_or_assertion=is_success,
            matcher=is_(True)
        )

        query = select(orm.Token).where(
            orm.Token.user_id == user_id
        )
        record = await get_dbase_session.execute(query)
        token_orm = record.scalar()
        is_exist = True if token_orm else False

        assert_that(
            actual_or_assertion=is_exist,
            matcher=is_(True)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_user_id(self, get_dbase_session, is_exist: bool):
        table_dal = TokenDAL(session=get_dbase_session)
        if is_exist:
            query = select(orm.User.id_)
            record = await get_dbase_session.execute(query)
            user_ids: List[int] = record.scalars().all()
            expected_user_id: int = random.choice(user_ids)
            await table_dal.add(user_id=expected_user_id)

            query = select(orm.Token.value).where(
                orm.Token.user_id == expected_user_id
            )
            record = await get_dbase_session.execute(query)
            token_value = record.scalar()
        else:
            token_value = uuid4().hex
            expected_user_id = -1

        actual_user_id = await table_dal.get_user_id(
            token_value=token_value
        )
        assert_that(
            actual_or_assertion=actual_user_id,
            matcher=equal_to(expected_user_id)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_by_user_id(self, get_dbase_session, is_exist: bool):
        table_dal = TokenDAL(session=get_dbase_session)
        if is_exist:
            query = select(orm.User.id_)
            record = await get_dbase_session.execute(query)
            user_ids: List[int] = record.scalars().all()
            user_id: int = random.choice(user_ids)
            await table_dal.add(user_id=user_id)

            query = select(orm.Token).where(
                orm.Token.user_id == user_id
            )
            record = await get_dbase_session.execute(query)
            token_orm = record.scalar()
            expected_token = models.Token(
                value=token_orm.value,
                expires=token_orm.expires
            )
        else:
            user_id = -1
            expected_token = None

        actual_token = await table_dal.get_by_user_id(id_=user_id)
        assert_that(
            actual_or_assertion=actual_token,
            matcher=equal_to(expected_token)
        )

import random
from uuid import uuid4

import pytest
from hamcrest import assert_that, equal_to, is_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.token_ import TokenDAL


class TestTokenDAL:

    @staticmethod
    async def get_random_existing_user_id(session: AsyncSession) -> int:
        query = select(orm.User.id_)
        records = await session.execute(query)
        user_ids = records.scalars().all()
        if not user_ids:
            return -1
        return random.choice(user_ids)

    @pytest.mark.asyncio
    async def test_add(self, get_dbase_session):
        user_id = await self.get_random_existing_user_id(
            session=get_dbase_session
        )

        token_dal = TokenDAL(session=get_dbase_session)
        is_success = await token_dal.add(user_id=user_id)

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
    async def test_get_by_user_id(self, get_dbase_session, is_exist: bool):
        token_dal = TokenDAL(session=get_dbase_session)
        if is_exist:
            user_id: int = await self.get_random_existing_user_id(
                session=get_dbase_session
            )
            await token_dal.add(user_id=user_id)

            query = select(orm.Token).where(orm.Token.user_id == user_id)
            record = await get_dbase_session.execute(query)
            token_orm = record.scalar()
            expected_token = models.Token(
                value=token_orm.value,
                expires=token_orm.expires
            )
        else:
            user_id = -1
            expected_token = None

        actual_token = await token_dal.get_by_user_id(id_=user_id)
        assert_that(
            actual_or_assertion=actual_token,
            matcher=equal_to(expected_token)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_user_id(self, get_dbase_session, is_exist: bool):
        token_dal = TokenDAL(session=get_dbase_session)
        if is_exist:
            user_id = await self.get_random_existing_user_id(
                session=get_dbase_session
            )
            await token_dal.add(user_id=user_id)

            token_value = (await token_dal.get_by_user_id(id_=user_id)).value
        else:
            user_id = -1
            token_value = uuid4().hex

        actual_user_id = await token_dal.get_user_id(
            token_value=token_value
        )
        assert_that(
            actual_or_assertion=actual_user_id,
            matcher=equal_to(user_id)
        )

    @pytest.mark.asyncio
    async def test_delete(self, get_dbase_session):
        user_id = await self.get_random_existing_user_id(
            session=get_dbase_session
        )

        token_dal = TokenDAL(session=get_dbase_session)
        await token_dal.add(user_id=user_id)

        token_value = (await token_dal.get_by_user_id(id_=user_id)).value
        await token_dal.delete(token_value=token_value)

        token = await token_dal.get_by_user_id(id_=user_id)
        assert_that(
            actual_or_assertion=token,
            matcher=is_(None)
        )

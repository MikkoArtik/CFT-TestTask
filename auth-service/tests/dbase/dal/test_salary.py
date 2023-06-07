import random
from datetime import datetime
from typing import Union

import pytest
from hamcrest import assert_that, equal_to, is_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.salary import SalaryDAL


class TestSalaryDAL:

    @staticmethod
    async def get_random_existing_user(
            session: AsyncSession) -> Union[orm.User, None]:
        query = select(orm.User)
        records = await session.execute(query)
        users = records.scalars().all()
        if not users:
            return
        return random.choice(users)

    @pytest.mark.asyncio
    async def test_add(self, get_dbase_session):
        user = await self.get_random_existing_user(session=get_dbase_session)
        salary_info = models.SalaryInfo(
            user_id=user.id_,
            name=user.name,
            value=123456,
            target_date=datetime.now().date()
        )

        salary_dal = SalaryDAL(get_dbase_session)
        is_success = await salary_dal.add(salary_info=salary_info)

        assert_that(
            actual_or_assertion=is_success,
            matcher=is_(True)
        )

        query = select(orm.Salary).where(orm.Salary.user_id == user.id_)
        salary_orm: orm.Salary = (
            await get_dbase_session.execute(query)
        ).scalar()

        assert_that(
            actual_or_assertion=salary_orm.value,
            matcher=equal_to(salary_info.value)
        )
        assert_that(
            actual_or_assertion=salary_orm.target_date,
            matcher=equal_to(salary_info.target_date)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_by_user_id(self, get_dbase_session, is_exist: bool):
        if is_exist:
            query = select(orm.Salary)
            records = (await get_dbase_session.execute(query)).scalars().all()
            salary_orm = random.choice(records)

            user_id: int = salary_orm.user_id
            query = select(orm.User.name).where(orm.User.id_ == user_id)
            name = (await get_dbase_session.execute(query)).scalar()

            expected_salary = models.SalaryInfo(
                user_id=user_id,
                name=name,
                value=salary_orm.value,
                target_date=salary_orm.target_date
            )
        else:
            user_id = -1
            expected_salary = None

        table_dal = SalaryDAL(get_dbase_session)
        salary_info = await table_dal.get_by_user_id(id_=user_id)

        assert_that(
            actual_or_assertion=salary_info,
            matcher=equal_to(expected_salary)
        )

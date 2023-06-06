from datetime import datetime

import pytest
from hamcrest import assert_that, equal_to
from sqlalchemy import select

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.salary import SalaryDAL


class TestSalaryDAL:

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_by_user_id(self, get_dbase_session, is_exist: bool):
        if is_exist:
            query = select(orm.Salary).limit(1)
            record = await get_dbase_session.execute(query)
            salary_orm = record.scalar()
            user_id: int = salary_orm.user_id

            query = select(orm.User.name).where(
                orm.User.id_ == user_id
            )
            record = await get_dbase_session.execute(query)
            name = record.scalar()

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

    @pytest.mark.asyncio
    async def test_add(self, get_dbase_session):
        query = select(orm.User).limit(1)
        record = await get_dbase_session.execute(query)
        user_orm = record.scalar()

        salary_info = models.SalaryInfo(
            user_id=user_orm.id_,
            name=user_orm.name,
            value=123456,
            target_date=datetime.now().date()
        )
        table_dal = SalaryDAL(get_dbase_session)
        await table_dal.add(salary_info=salary_info)

        actual_salary_info = await table_dal.get_by_user_id(id_=user_orm.id_)
        assert_that(
            actual_or_assertion=actual_salary_info,
            matcher=equal_to(salary_info)
        )

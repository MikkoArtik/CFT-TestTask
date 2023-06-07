import ast
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from hamcrest import assert_that, equal_to

from auth_app import models
from auth_app.app import app
from auth_app.dbase.dal.salary import SalaryDAL
from auth_app.dbase.dal.token_ import EXPIRES_SIZE, TokenDAL
from auth_app.dbase.dal.user import UserDAL
from auth_app.models import DATETIME_FORMAT
from tests.dbase.dal.helpers import create_test_user


class TestSalaryRoute:
    @pytest.mark.asyncio
    async def test_without_token(self, get_dbase_session):
        with TestClient(app) as client:
            response = client.get(url='/salary')

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(401)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to({'detail': 'Not authenticated'})
        )

    @pytest.mark.freeze_time('2023-01-01')
    @pytest.mark.asyncio
    async def test_expired_token(self, get_dbase_session, freezer):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        user_id = await user_dal.get_id_by_login(login=user.login)

        token_dal = TokenDAL(session=get_dbase_session)
        await token_dal.add(user_id=user_id)

        token_value = await token_dal.get_by_user_id(id_=user_id)

        freezer.move_to('2023-02-01')

        with TestClient(app) as client:
            response = client.get(
                url='/salary',
                headers={
                    'Authorization': f'Bearer {token_value.value}'
                }
            )

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(401)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to({'detail': 'Token is expired'})
        )

    @pytest.mark.freeze_time('2023-01-01')
    @pytest.mark.asyncio
    async def test_good_token_without_salary(self, get_dbase_session, freezer):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        user_id = await user_dal.get_id_by_login(login=user.login)

        token_dal = TokenDAL(session=get_dbase_session)
        await token_dal.add(user_id=user_id)

        token_value = await token_dal.get_by_user_id(id_=user_id)

        next_time = datetime(2023, 1, 1) + EXPIRES_SIZE + timedelta(
            seconds=-30
        )

        freezer.move_to(next_time.strftime(DATETIME_FORMAT))

        with TestClient(app) as client:
            response = client.get(
                url='/salary',
                headers={
                    'Authorization': f'Bearer {token_value.value}'
                }
            )

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(400)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to({'detail': 'Salary info not found'})
        )

    @pytest.mark.freeze_time('2023-01-01')
    @pytest.mark.asyncio
    async def test_good_token_with_salary(self, get_dbase_session, freezer):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        user_id = await user_dal.get_id_by_login(login=user.login)

        salary_dal = SalaryDAL(session=get_dbase_session)
        expected_salary_info = models.SalaryInfo(
            user_id=user_id,
            name=user.name,
            value=123456,
            target_date=datetime.now().date()
        )
        await salary_dal.add(salary_info=expected_salary_info)

        request_data = {
            'username': user.login,
            'password': user.password
        }
        with TestClient(app) as client:
            response = client.post(url='/auth', data=request_data)

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(200)
        )

        token_dal = TokenDAL(session=get_dbase_session)
        await token_dal.add(user_id=user_id)

        token_value = await token_dal.get_by_user_id(id_=user_id)

        next_time = datetime(2023, 1, 1) + EXPIRES_SIZE + timedelta(
            seconds=-30
        )
        freezer.move_to(next_time.strftime(DATETIME_FORMAT))

        with TestClient(app) as client:
            response = client.get(
                url='/salary',
                headers={'Authorization': f'Bearer {token_value.value}'}
            )

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(200)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=ast.literal_eval(expected_salary_info.json(by_alias=True))
        )

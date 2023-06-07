import ast

import pytest
from fastapi.testclient import TestClient
from hamcrest import assert_that, equal_to

from auth_app import models
from auth_app.app import app
from auth_app.dbase.dal.user import UserDAL
from auth_app.models import DATE_FORMAT
from tests.dbase.dal.helpers import create_test_user

from .helpers import create_user_salary


class TestUserRoute:

    @pytest.mark.asyncio
    async def test_add_existing_login(self, get_dbase_session):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        request_data = {
            'user': user.dict(by_alias=True),
            'salary': ast.literal_eval(
                create_user_salary().json(by_alias=True)
            )
        }

        with TestClient(app) as client:
            response = client.post(
                url='/user/add',
                json=request_data
            )

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(401)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to(
                {
                    'detail': f'User with login {user.login} is exist'
                }
            )
        )

    @pytest.mark.asyncio
    async def test_add_new_user_info(self, get_dbase_session):
        user = create_test_user()
        salary_info = create_user_salary()
        request_data = {
            'user': {
                'Name': user.name,
                'Login': user.login,
                'Password': user.password
            },
            'salary': {
                'Value': salary_info.value,
                'TargetDate': salary_info.target_date.strftime(DATE_FORMAT)
            }
        }

        with TestClient(app) as client:
            response = client.post(
                url='/user/add',
                json=request_data
            )

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(200)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to(models.Response(
                message='User and salary info is was added.'
            ).dict(by_alias=True))
        )

import ast

import pytest
from fastapi.testclient import TestClient
from hamcrest import assert_that, equal_to

from auth_app import models
from auth_app.app import app
from auth_app.dbase.dal.token_ import TokenDAL
from auth_app.dbase.dal.user import UserDAL, generate_random_string


class TestAuth:
    @pytest.mark.asyncio
    async def test_invalid_username(self, get_dbase_session):
        request_data = {
            'username': generate_random_string(10),
            'password': generate_random_string(5)
        }
        with TestClient(app) as client:
            response = client.post(url='/auth', data=request_data)

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(400)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to({'detail': 'Login not found'})
        )

    @pytest.mark.asyncio
    async def test_invalid_password(self, get_dbase_session):
        table = UserDAL(session=get_dbase_session)
        user = models.User(
            name=generate_random_string(10),
            login='test-' + generate_random_string(5),
            password=generate_random_string(5)
        )
        await table.add(user=user)

        request_data = {
            'username': user.login,
            'password': generate_random_string(5)
        }
        with TestClient(app) as client:
            response = client.post(url='/auth', data=request_data)

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(400)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to({'detail': 'Incorrect login or password'})
        )

    @pytest.mark.asyncio
    async def test_valid_login_and_password(self, get_dbase_session):
        table = UserDAL(session=get_dbase_session)
        user = models.User(
            name=generate_random_string(10),
            login='test-' + generate_random_string(5),
            password=generate_random_string(5)
        )
        await table.add(user=user)
        user_id = await table.get_id_by_login(login=user.login)

        request_data = {
            'username': user.login,
            'password': user.password
        }
        with TestClient(app) as client:
            response = client.post(url='/auth', data=request_data)

        table = TokenDAL(session=get_dbase_session)
        token = await table.get_by_user_id(id_=user_id)

        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(200)
        )

        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to(ast.literal_eval(token.json(by_alias=True)))
        )

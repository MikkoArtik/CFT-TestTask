from unittest.mock import Mock, patch

import pytest
from hamcrest import assert_that, equal_to, is_
from helpers import generate_invalid_passwords, generate_valid_passwords
from sqlalchemy import select

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.user import (UserDAL, generate_random_string,
                                     get_hashed_password, is_valid_password)


@pytest.mark.parametrize('length', [0, 1, 10, 20])
def test_generate_random_string(length: int):
    line = generate_random_string(length=length)
    assert_that(
        actual_or_assertion=len(line),
        matcher=equal_to(length)
    )


@pytest.mark.parametrize(
    'password, salt', [('', 'salt'), ('pass', ''), ('pass', 'salt')])
@patch('hashlib.pbkdf2_hmac')
def test_get_hashed_password(pbkdf2_hmac_mock: Mock, password: str, salt: str):
    get_hashed_password(password=password, salt=salt)

    pbkdf2_hmac_mock.assert_called_once_with(
        hash_name='sha256',
        password=password.encode(),
        salt=salt.encode(),
        iterations=20000
    )
    pbkdf2_hmac_mock.hex.aasert_called_ones()


def test_is_valid_password():
    valid_passwords = generate_valid_passwords(count=20)
    for password, salt, encoded_password in valid_passwords:
        assert_that(
            actual_or_assertion=is_valid_password(
                password=password, hashed_password=encoded_password
            ),
            matcher=is_(True)
        )

    invalid_passwords = generate_invalid_passwords(count=20)
    for password, salt, encoded_password in invalid_passwords:
        assert_that(
            actual_or_assertion=is_valid_password(
                password=password, hashed_password=encoded_password
            ),
            matcher=is_(False)
        )


class TestUser:
    user = models.User(
        name='test-user',
        login='test-name',
        password='some-pass'
    )

    @pytest.mark.asyncio
    async def test_add(self, get_dbase_session):
        dal = UserDAL(session=get_dbase_session)
        is_success = await dal.add(user=self.user)

        assert_that(
            actual_or_assertion=is_success,
            matcher=is_(True)
        )

        query = select(orm.User.login).where(orm.User.name == self.user.name)
        record = await get_dbase_session.execute(query)
        assert_that(
            actual_or_assertion=record.scalar(),
            matcher=equal_to(self.user.login)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_valid', [True, False])
    async def test_is_valid_login_password_pair(self, get_dbase_session,
                                                is_valid: bool):
        if is_valid:
            auth_info = models.UserAuth(
                login=self.user.login,
                password=self.user.password
            )
        else:
            auth_info = models.UserAuth(
                login=self.user.login,
                password=self.user.password + 'q'
            )

        dal = UserDAL(session=get_dbase_session)
        actual_is_valid = await dal.is_valid_login_password_pair(
            user=auth_info
        )

        assert_that(actual_or_assertion=actual_is_valid,
                    matcher=is_(is_valid))

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_is_exist(self, get_dbase_session, is_exist: bool):
        if is_exist:
            login = self.user.login
        else:
            login = self.user.login + 'q'

        dal = UserDAL(session=get_dbase_session)
        actual_is_exist = await dal.is_exist(login=login)
        assert_that(
            actual_or_assertion=actual_is_exist,
            matcher=is_(is_exist)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_id_by_login(self, get_dbase_session, is_exist: bool):
        if is_exist:
            login = self.user.login
        else:
            login = self.user.login + 'q'

        dal = UserDAL(session=get_dbase_session)
        id_value = await dal.get_id_by_login(login=login)

        if not is_exist:
            assert_that(
                actual_or_assertion=id_value,
                matcher=equal_to(-1)
            )
        else:
            query = select(orm.User.id_).where(orm.User.login == login)
            record = await get_dbase_session.execute(query)
            assert_that(
                actual_or_assertion=id_value,
                matcher=equal_to(record.scalar())
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_by_id(self, get_dbase_session, is_exist: bool):
        dal = UserDAL(session=get_dbase_session)
        if is_exist:
            id_value = await dal.get_id_by_login(login=self.user.login)
        else:
            id_value = -1

        active_user = await dal.get_by_id(id_=id_value)
        if is_exist:
            assert_that(
                actual_or_assertion=active_user.name,
                matcher=equal_to(self.user.name)
            )
        else:
            assert_that(
                actual_or_assertion=active_user,
                matcher=is_(None)
            )

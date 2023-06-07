from unittest.mock import Mock, patch

import pytest
from hamcrest import assert_that, equal_to, is_
from sqlalchemy import select

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.user import (UserDAL, generate_random_string,
                                     get_hashed_password, is_valid_password)

from .helpers import (create_test_user, generate_invalid_passwords,
                      generate_valid_passwords)


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
    pbkdf2_hmac_mock.return_value.hex.assert_called_once_with()


def test_is_valid_password():
    passwords = []
    passwords += [x + [True] for x in generate_valid_passwords()]
    passwords += [x + [False] for x in generate_invalid_passwords()]

    for password, salt, encoded_password, is_valid in passwords:
        assert_that(
            actual_or_assertion=is_valid_password(
                password=password, hashed_password=encoded_password
            ),
            matcher=is_(is_valid)
        )


class TestUserDAL:

    @pytest.mark.asyncio
    async def test_add(self, get_dbase_session):
        user = create_test_user()

        dal = UserDAL(session=get_dbase_session)
        is_success = await dal.add(user=user)

        assert_that(
            actual_or_assertion=is_success,
            matcher=is_(True)
        )

        query = select(orm.User.login).where(orm.User.name == user.name)
        record = await get_dbase_session.execute(query)
        assert_that(
            actual_or_assertion=record.scalar(),
            matcher=equal_to(user.login)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'is_good_login, is_good_password',
        [[True, True], [True, False], [False, False]]
    )
    async def test_is_valid_login_password_pair(
            self, get_dbase_session, is_good_login: bool,
            is_good_password: bool
    ):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        if not is_good_login:
            auth_info = models.UserAuth(
                login=create_test_user().login,
                password=user.password
            )
        elif not is_good_password:
            auth_info = models.UserAuth(
                login=user.login,
                password=create_test_user().password
            )
        else:
            auth_info = models.UserAuth(
                login=user.login,
                password=user.password
            )

        actual_is_valid = await user_dal.is_valid_login_password_pair(
            user=auth_info
        )

        assert_that(actual_or_assertion=actual_is_valid,
                    matcher=is_(is_good_login and is_good_password))

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_is_exist(self, get_dbase_session, is_exist: bool):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        if is_exist:
            login = user.login
        else:
            login = create_test_user().login

        dal = UserDAL(session=get_dbase_session)
        actual_is_exist = await dal.is_exist(login=login)
        assert_that(
            actual_or_assertion=actual_is_exist,
            matcher=is_(is_exist)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_exist', [True, False])
    async def test_get_id_by_login(self, get_dbase_session, is_exist: bool):
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        if is_exist:
            login = user.login
        else:
            login = create_test_user().login

        id_value = await user_dal.get_id_by_login(login=login)

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
        user = create_test_user()
        user_dal = UserDAL(session=get_dbase_session)
        await user_dal.add(user=user)

        if is_exist:
            id_value = await user_dal.get_id_by_login(login=user.login)
        else:
            id_value = -1

        active_user = await user_dal.get_by_id(id_=id_value)
        if is_exist:
            assert_that(
                actual_or_assertion=active_user.name,
                matcher=equal_to(user.name)
            )
        else:
            assert_that(
                actual_or_assertion=active_user,
                matcher=is_(None)
            )

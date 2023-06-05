from unittest.mock import AsyncMock, patch

import pytest
from hamcrest import assert_that, equal_to
from sqlalchemy.exc import DBAPIError

from auth_app.dbase.dal.base import BaseDAL


class TestBaseDAL:
    @patch('sqlalchemy.ext.asyncio.AsyncSession', autospec=True)
    def test_session(self, session_mock: AsyncMock):
        session_instance = session_mock.return_value
        obj = BaseDAL(session=session_instance)
        assert_that(
            actual_or_assertion=obj.session,
            matcher=equal_to(session_instance)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_success', [True, False])
    @patch('sqlalchemy.ext.asyncio.AsyncSession', autospec=True)
    async def test_is_success_changing_query(self, session_mock: AsyncMock,
                                             is_success: bool):
        session_instance = AsyncMock()
        if not is_success:
            session_instance.commit.side_effect = DBAPIError(
                statement='some-statement',
                params=[],
                orig=BaseException
            )

        session_mock.return_value = session_instance
        obj = BaseDAL(session=session_instance)

        await obj.is_success_changing_query()

        session_instance.commit.assert_called_once()
        if is_success:
            session_instance.rollback.assert_not_called()
        else:
            session_instance.rollback.assert_called_once()

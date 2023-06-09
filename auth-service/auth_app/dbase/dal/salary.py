"""Module with Token database table operations."""

from typing import Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app import models
from auth_app.dbase import orm
from auth_app.dbase.dal.base import BaseDAL

__all__ = [
    'SalaryDAL',
]


class SalaryDAL(BaseDAL):
    """Class with token table methods."""

    def __init__(self, session: AsyncSession):
        """Initialize class method.

        Args:
            session: AsyncSession
        """
        super().__init__(session=session)

    async def add(self, salary_info: models.SalaryInfo) -> bool:
        """Add salary info to database.

        Args:
            salary_info: pydantic SalaryInfo model

        Returns: bool

        """
        query = select(orm.Salary).where(
            orm.Salary.user_id == salary_info.user_id
        )
        salary_orm = (await self.session.execute(query)).scalar()
        if not salary_orm:
            self.session.add(
                orm.Salary(
                    user_id=salary_info.user_id,
                    value=salary_info.value,
                    target_date=salary_info.target_date,
                )
            )
        else:
            query = update(orm.Salary).where(
                orm.Salary.user_id == salary_info.user_id
            ).values(
                {
                    'value': salary_info.value,
                    'target_date': salary_info.target_date
                }
            )
            await self.session.execute(query)
        return await self.is_success_changing_query()

    async def get_by_user_id(self, id_: int) -> Union[models.SalaryInfo, None]:
        """Return salary info by user id.

        Args:
            id_: int

        Returns: pydantic SalaryInfo model

        """
        query = select(orm.Salary).where(orm.Salary.user_id == id_)
        salary_orm = (await self.session.execute(query)).scalar()
        if not salary_orm:
            return

        query = select(orm.User).where(orm.User.id_ == id_)
        user_orm = (await self.session.execute(query)).scalar()

        return models.SalaryInfo(
            user_id=id_,
            name=user_orm.name,
            value=salary_orm.value,
            target_date=salary_orm.target_date
        )

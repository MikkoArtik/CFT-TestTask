"""Module with class-models.

This module contains models with database fields.

"""

from datetime import MINYEAR, date, datetime
from typing import List

from pydantic import BaseModel, Field

__all__ = [
    'Response',
    'User',
]

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


def format_datetime(value: datetime) -> str:
    return value.strftime(DATETIME_FORMAT)


def format_date(value: date) -> str:
    return value.strftime(DATE_FORMAT)


class CustomBaseModel(BaseModel):
    class Config:
        """Model configuration."""

        allow_population_by_field_name = True
        json_encoders = {
            date: format_date,
            datetime: format_datetime
        }


class Response(CustomBaseModel):
    """Model with API response params.

    Args:
        status: response status
        message: description with response action
        data: info about deposit area name

    """
    status: bool = Field(alias='Status', default=True)
    message: str = Field(alias='Message', default='All good.')
    data: List = Field(alias='Data', default=[])


class User(CustomBaseModel):
    """Model with user information.

    Args:
        login: user login
        password: user password

    """
    name: str = Field(alias='Name', min_length=5, max_length=50)
    login: str = Field(alias='Login', min_length=5, max_length=20)
    password: str = Field(alias='Password', min_length=1, max_length=10)


class Token(CustomBaseModel):
    """Model with token information.

    Args:
        token: user login
        expires: user password

    """
    token: str = Field(alias='AccessToken', default='')
    expires: datetime = Field(
        alias='Expires',
        default=datetime(year=MINYEAR, month=1, day=1)
    )

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires


class ActiveUser(CustomBaseModel):
    id_: int = Field(alias='UserID')
    name: str = Field(alias='Name')


class SalaryInfo(CustomBaseModel):
    user_id: int = Field(alias='UserID')
    name: str = Field(alias='Name')
    salary: int = Field(alias='Salary')
    target_date: date = Field(alias='TargetDate')

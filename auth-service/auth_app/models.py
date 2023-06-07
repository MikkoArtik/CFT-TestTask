"""Module with class-models.

This module contains models with database fields.

"""

from datetime import date, datetime
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
    """Base model."""

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
        data: array with something

    """
    status: bool = Field(alias='Status', default=True)
    message: str = Field(alias='Message', default='All good.')
    data: List = Field(alias='Data', default=[])


class UserAuth(CustomBaseModel):
    """Model with user auth parameters.

    Args:
        login: user login
        password: user password

    """
    login: str = Field(alias='username', min_length=1, max_length=20)
    password: str = Field(alias='password', min_length=1, max_length=10)


class User(CustomBaseModel):
    """Model with user information.

    Args:
        name: name of user
        login: user login
        password: user password

    """
    name: str = Field(alias='Name', max_length=50)
    login: str = Field(alias='Login', min_length=1, max_length=20)
    password: str = Field(alias='Password', min_length=1, max_length=10)


class Token(CustomBaseModel):
    """Model with token information.

    Args:
        value: user login
        expires: user password
        token_type: default Bearer

    """
    value: str = Field(alias='access_token')
    expires: datetime = Field(alias='expires')
    token_type: str = Field(alias='token_type', default='Bearer')

    @property
    def is_valid(self) -> bool:
        """Return token validation.

        Returns: bool

        """
        return datetime.now() < self.expires


class ActiveUser(CustomBaseModel):
    """Model with active user information.

    Args:
        id_: user id
        name: name of user

    """
    id_: int = Field(alias='UserID')
    name: str = Field(alias='Name')


class SalaryInfo(CustomBaseModel):
    """Model with salary information for current user.

    Args:
        user_id: user id
        name: name of user
        value: salary value
        target_date: salary increase date

    """
    user_id: int = Field(alias='UserID')
    name: str = Field(alias='Name')
    value: int = Field(alias='Salary')
    target_date: date = Field(alias='TargetDate')


class UserSalary(CustomBaseModel):
    """Model with salary information for current user.

    Args:
        value: salary value
        target_date: salary increase date

    """
    value: int = Field(alias='Value')
    target_date: date = Field(alias='TargetDate')

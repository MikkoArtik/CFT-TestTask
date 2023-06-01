"""Module with class-models.

This module contains models with database fields.

"""

from typing import List

from pydantic import BaseModel, Field

__all__ = [
    'Response',
    'User',
]


class Response(BaseModel):
    """Model with API response params.

    Args:
        status: response status
        message: description with response action
        data: info about deposit area name

    """
    status: bool = Field(alias='Status', default=True)
    message: str = Field(alias='Message', default='All good.')
    data: List = Field(alias='Data', default=[])

    class Config:
        """Model configuration."""

        allow_population_by_field_name = True


class User(BaseModel):
    """Model with user information.

    Args:
        login: user login
        password: user password

    """
    login: str = Field(alias='Login', min_length=5, max_length=20)
    password: str = Field(alias='Password', min_length=1, max_length=10)

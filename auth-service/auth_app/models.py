"""Module with class-models.

This module contains models with database fields.

"""

from typing import List

from pydantic import BaseModel, Field

__all__ = [
    'Response',
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

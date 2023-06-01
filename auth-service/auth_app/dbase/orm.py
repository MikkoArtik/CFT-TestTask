"""Module with SQLAlchemy models."""

import sqlalchemy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

__all__ = [
    'UserTable',
    'Token',
    'Staff',
    'Salary',
]

base = declarative_base()


class UserTable(base):
    """User information table."""

    id_ = Column(
        name='id',
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    login = Column(
        name='login',
        type_=String(length=20),
        nullable=False,
        unique=True
    )
    hashed_password = Column(
        name='hashed_password',
        type_=String(length=100),
        nullable=False,
        unique=True
    )

    __tablename__ = 'users'


class Token(base):
    """Tokens list table."""

    id_ = Column(
        name='id',
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    token = Column(
        name='token',
        type_=UUID(as_uuid=False),
        nullable=False,
        unique=True,
        server_default=sqlalchemy.text('uuid_generate_v4()')
    )
    expires = Column(
        name='expires',
        type_=DateTime,
        nullable=False
    )
    user_id = Column(
        ForeignKey('users.id'),
        name='user_id',
        type_=Integer,
        nullable=False
    )
    user = relationship(argument='User', back_populates='parent')

    __tablename__ = 'tokens'


class Staff(base):
    """Staff information table."""

    id_ = Column(
        name='id',
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    name = Column(
        name='name',
        type_=String(length=50),
        nullable=False,
    )
    user_id = Column(
        ForeignKey('users.id'),
        name='user_id',
        type_=Integer,
        nullable=False
    )
    user = relationship(argument='User', back_populates='parent')

    __tablename__ = 'staff'


class Salary(base):
    """Salary information table."""

    id_ = Column(
        name='id',
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    value = Column(
        name='value',
        type_=Integer,
        nullable=False,
        default=0
    )
    increase_datetime = Column(
        name='increase_datetime',
        type_=DateTime,
        nullable=False
    )
    staff_id = Column(
        ForeignKey('staff.id'),
        name='staff_id',
        type_=Integer,
        nullable=False
    )
    staff = relationship(argument='Staff', back_populates='parent')

    __tablename__ = 'salary'

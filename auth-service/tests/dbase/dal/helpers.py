from typing import List

from auth_app import models
from auth_app.dbase.dal.user import (HASH_SALT_DELIMITER,
                                     generate_random_string,
                                     get_hashed_password)


def generate_valid_passwords(count: int = 10) -> List[List[str]]:
    passwords = []
    for _ in range(count):
        password = generate_random_string(length=10)
        salt = generate_random_string(length=5)
        hashed_password = get_hashed_password(password=password, salt=salt)
        passwords.append(
            [password, salt, HASH_SALT_DELIMITER.join([hashed_password, salt])]
        )
    return passwords


def generate_invalid_passwords(count: int = 10) -> List[List[str]]:
    passwords = []
    for _ in range(count):
        password = generate_random_string(length=10)
        salt = generate_random_string(length=5)
        hashed_password = get_hashed_password(
            password=password,
            salt=salt + 'q'
        )
        passwords.append(
            [password, salt, HASH_SALT_DELIMITER.join([hashed_password, salt])]
        )
    return passwords


def create_test_user() -> models.User:
    return models.User(
        name=generate_random_string(length=10),
        login='test-' + generate_random_string(length=5),
        password=generate_random_string(length=7)
    )

import random
from datetime import datetime

from auth_app import models
from auth_app.dbase.dal.user import generate_random_string


def create_auth_data() -> models.UserAuth:
    return models.UserAuth(
        login=generate_random_string(),
        password=generate_random_string()
    )


def create_user_salary() -> models.UserSalary:
    return models.UserSalary(
        value=random.randint(1, 10000000),
        target_date=datetime.now()
    )

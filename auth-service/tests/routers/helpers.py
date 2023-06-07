from auth_app import models
from auth_app.dbase.dal.user import generate_random_string


def create_auth_data() -> models.UserAuth:
    return models.UserAuth(
        login=generate_random_string(),
        password=generate_random_string()
    )

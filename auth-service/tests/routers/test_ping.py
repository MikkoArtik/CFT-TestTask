from fastapi.testclient import TestClient
from hamcrest import assert_that, equal_to

from auth_app.app import app
from auth_app.models import Response


def test_ping():
    with TestClient(app) as client:
        response = client.get('/ping')
        assert_that(
            actual_or_assertion=response.status_code,
            matcher=equal_to(200)
        )
        assert_that(
            actual_or_assertion=response.json(),
            matcher=equal_to(
                Response(message='Service is alive').dict(by_alias=True)
            )
        )

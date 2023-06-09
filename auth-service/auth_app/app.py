"""App main module."""

from fastapi import FastAPI

from auth_app.models import Response
from auth_app.routers import auth, salary, user

__all__ = [
    'app',
]

app = FastAPI()
app.include_router(auth.router)
app.include_router(salary.router)
app.include_router(user.router)


@app.get('/ping', response_model=Response)
async def check_service_alive() -> Response:
    """Return ping-pong response.

    Returns: dict object with status and message

    """
    return Response(
        message='Service is alive'
    )

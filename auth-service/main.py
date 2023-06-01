"""App main module."""

import os

import dotenv
import uvicorn
from fastapi import FastAPI

from auth_app.models import Response

__all__ = []

dotenv.load_dotenv()

app = FastAPI()


@app.get('/ping')
async def check_service_alive() -> Response:
    """Return ping-pong response.

    Returns: dict object with status and message

    """
    return Response(
        message='Service is alive'
    )


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host=os.getenv('APP_HOST'),
        port=int(os.getenv('APP_PORT'))
    )

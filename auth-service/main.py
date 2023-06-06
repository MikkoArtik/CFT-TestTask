"""App main module."""

import os

import dotenv
import uvicorn

from auth_app.app import app

__all__ = []

dotenv.load_dotenv()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host=os.getenv('APP_HOST'),
        port=int(os.getenv('APP_PORT'))
    )

import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from short_url import api, constants
from short_url.app import init_application
from short_url.containers import Application
from short_url.error_handlers import register_error_handler


def create_fastapi() -> FastAPI:
    app: Application = init_application()

    fastapi_app = FastAPI(
        title=constants.PROJECT_NAME,
        version=app.config.version(),
        docs_url=f"{constants.API_PREFIX}{constants.SWAGGER_DOC_URL}",
        description=constants.DESCRIPTION,
        openapi_url=f"{constants.API_PREFIX}/openapi.json",
    )
    fastapi_app.include_router(api.router, prefix="")
    fastapi_app.app = app
    fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")

    register_error_handler(fastapi_app)

    return fastapi_app


def run_api():
    options = {
        "host": "0.0.0.0",  # noqa: S104
        "port": 8000,
        "log_level": "debug",
        "reload": os.getenv("ENV", "prod") == "development",
    }

    uvicorn.run("short_url.fastapi_app:create_fastapi", **options)

"""GitHub Bootstrap web application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from github_bootstrap.web.routes import router

WEB_DIRECTORY = Path(__file__).parent


def create_app() -> FastAPI:
    """Create and configure the web application."""

    application = FastAPI(
        title="GitHub Bootstrap",
    )

    application.mount(
        "/static",
        StaticFiles(directory=WEB_DIRECTORY / "static"),
        name="static",
    )

    application.include_router(router)

    return application


app = create_app()

"""GitHub Bootstrap web application."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from github_bootstrap.web.routes import router

WEB_DIRECTORY = Path(__file__).parent


def create_app() -> FastAPI:
    """Create and configure the web application."""

    session_secret = os.environ.get("SESSION_SECRET")

    if not session_secret:
        raise RuntimeError("SESSION_SECRET environment variable is required.")

    application = FastAPI(
        title="GitHub Bootstrap",
    )

    application.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        same_site="lax",
        https_only=os.environ.get(
            "SESSION_COOKIE_SECURE",
            "true",
        ).lower()
        == "true",
    )

    application.mount(
        "/static",
        StaticFiles(directory=WEB_DIRECTORY / "static"),
        name="static",
    )

    application.include_router(router)

    return application


app = create_app()

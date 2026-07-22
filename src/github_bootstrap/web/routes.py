"""Web routes for GitHub Bootstrap."""

import hmac
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from github_bootstrap.application.synchronization_service import (
    SynchronizationService,
)
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.planner.plan import Plan
from github_bootstrap.specification.models import ProjectSpecification
from github_bootstrap.specification.parser import parse_specification
from github_bootstrap.specification.validator import (
    SpecificationValidationError,
    validate_specification,
)

WEB_DIRECTORY = Path(__file__).parent

DEFAULT_SPECIFICATION = """organization:
repository:

project:
  title:
"""

templates = Jinja2Templates(
    directory=WEB_DIRECTORY / "templates",
)

router = APIRouter()


@dataclass(frozen=True)
class WebResult:
    """Structured result rendered by the web interface."""

    title: str
    message: str
    result_type: str = "neutral"
    actions: list[str] = field(default_factory=list)
    drift: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _parse_specification(
    specification: str,
) -> ProjectSpecification:
    """Parse and validate a YAML project specification."""

    raw_specification: Any = yaml.safe_load(specification)

    if not isinstance(raw_specification, dict):
        raise SpecificationValidationError(
            "Specification root must be a mapping.",
        )

    validated_specification = validate_specification(
        raw_specification,
    )

    return parse_specification(
        validated_specification,
    )


def _build_plan_result(
    plan: Plan,
    *,
    title: str,
    message: str,
) -> WebResult:
    """Convert a synchronization plan into a web result."""

    actions = [action.description for action in plan.executable_actions()]

    drift = [action.description for action in plan.drift_actions()]

    if plan.is_empty():
        return WebResult(
            title=title,
            message="Everything is up to date.",
            result_type="success",
        )

    if actions and drift:
        result_type = "warning"
    elif drift:
        result_type = "warning"
    else:
        result_type = "success"

    return WebResult(
        title=title,
        message=message,
        result_type=result_type,
        actions=actions,
        drift=drift,
    )


def _render(
    request: Request,
    specification: str,
    result: WebResult,
) -> HTMLResponse:
    """Render the main web interface."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "specification": specification,
            "result": result,
        },
    )


@router.get(
    "/",
    response_class=HTMLResponse,
    response_model=None,
)
def index(
    request: Request,
) -> HTMLResponse | RedirectResponse:
    """Render the GitHub Bootstrap web interface."""

    redirect = _require_authentication(request)

    if redirect is not None:
        return redirect

    return _render(
        request=request,
        specification=DEFAULT_SPECIFICATION,
        result=WebResult(
            title="Ready",
            message=(
                "Validate the specification or run a dry run "
                "to inspect the synchronization plan."
            ),
        ),
    )


@router.post(
    "/validate",
    response_class=HTMLResponse,
    response_model=None,
)
def validate(
    request: Request,
    specification: str = Form(...),
) -> HTMLResponse | RedirectResponse:
    """Validate a YAML project specification."""

    redirect = _require_authentication(request)

    if redirect is not None:
        return redirect

    try:
        project_specification = _parse_specification(
            specification,
        )

        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="Valid specification",
                message=(
                    "The specification is valid for "
                    f"{project_specification.organization}/"
                    f"{project_specification.repository}."
                ),
                result_type="success",
            ),
        )

    except (
        yaml.YAMLError,
        SpecificationValidationError,
    ) as error:
        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="Invalid specification",
                message=("The YAML specification could not be validated."),
                result_type="error",
                errors=[str(error)],
            ),
        )


@router.post(
    "/dry-run",
    response_class=HTMLResponse,
    response_model=None,
)
def dry_run(
    request: Request,
    specification: str = Form(...),
) -> HTMLResponse | RedirectResponse:
    """Build and display a synchronization plan."""

    redirect = _require_authentication(request)

    if redirect is not None:
        return redirect

    try:
        project_specification = _parse_specification(
            specification,
        )

        client = GitHubClient()
        service = SynchronizationService(client)

        synchronization_result = service.dry_run(
            project_specification,
        )

        result = _build_plan_result(
            synchronization_result.plan,
            title="Dry run complete",
            message=("The following changes would be applied to GitHub."),
        )

        return _render(
            request=request,
            specification=specification,
            result=result,
        )

    except (
        yaml.YAMLError,
        SpecificationValidationError,
    ) as error:
        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="Invalid specification",
                message=(
                    "The dry run was not executed because the specification is invalid."
                ),
                result_type="error",
                errors=[str(error)],
            ),
        )

    except GitHubError as error:
        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="GitHub error",
                message=("The current GitHub state could not be loaded."),
                result_type="error",
                errors=[str(error)],
            ),
        )


@router.post(
    "/sync",
    response_class=HTMLResponse,
    response_model=None,
)
def synchronize(
    request: Request,
    specification: str = Form(...),
    confirm: str | None = Form(None),
) -> HTMLResponse | RedirectResponse:
    """Execute synchronization against GitHub."""

    redirect = _require_authentication(request)

    if redirect is not None:
        return redirect

    if confirm != "yes":
        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="Confirmation required",
                message=(
                    "Synchronization was not executed. Confirm that "
                    "the operation may modify GitHub resources."
                ),
                result_type="warning",
            ),
        )

    try:
        project_specification = _parse_specification(
            specification,
        )

        client = GitHubClient()
        service = SynchronizationService(client)

        synchronization_result = service.synchronize(
            project_specification,
        )

        result = _build_plan_result(
            synchronization_result.plan,
            title="Synchronization complete",
            message=("The supported synchronization actions were applied to GitHub."),
        )

        return _render(
            request=request,
            specification=specification,
            result=result,
        )

    except (
        yaml.YAMLError,
        SpecificationValidationError,
    ) as error:
        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="Invalid specification",
                message=(
                    "Synchronization was not executed because "
                    "the specification is invalid."
                ),
                result_type="error",
                errors=[str(error)],
            ),
        )

    except GitHubError as error:
        return _render(
            request=request,
            specification=specification,
            result=WebResult(
                title="GitHub synchronization error",
                message=("GitHub Bootstrap could not complete the synchronization."),
                result_type="error",
                errors=[str(error)],
            ),
        )


@router.get("/health")
def health() -> dict[str, str]:
    """Return the application health status."""

    return {
        "status": "ok",
    }


def _is_authenticated(request: Request) -> bool:
    """Return whether the current web session is authenticated."""

    return request.session.get("authenticated") is True


def _require_authentication(
    request: Request,
) -> RedirectResponse | None:
    """Redirect unauthenticated requests to the login page."""

    if _is_authenticated(request):
        return None

    return RedirectResponse(
        url="/login",
        status_code=303,
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
    response_model=None,
)
def login_page(
    request: Request,
) -> HTMLResponse | RedirectResponse:
    """Render the login page."""

    if _is_authenticated(request):
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
        },
    )


@router.post(
    "/login",
    response_class=HTMLResponse,
    response_model=None,
)
def login(
    request: Request,
    password: str = Form(...),
) -> HTMLResponse | RedirectResponse:
    """Authenticate access to the web interface."""

    expected_password = os.environ.get("WEB_ACCESS_PASSWORD")

    if not expected_password:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": (
                    "WEB_ACCESS_PASSWORD environment variable is not configured."
                ),
            },
            status_code=500,
        )

    if not hmac.compare_digest(
        password,
        expected_password,
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid password.",
            },
            status_code=401,
        )

    request.session["authenticated"] = True

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@router.post("/logout")
def logout(request: Request) -> RedirectResponse:
    """Clear the authenticated web session."""

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303,
    )

"""Web routes for GitHub Bootstrap."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
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


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Render the GitHub Bootstrap web interface."""

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


@router.post("/validate", response_class=HTMLResponse)
def validate(
    request: Request,
    specification: str = Form(...),
) -> HTMLResponse:
    """Validate a YAML project specification."""

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


@router.post("/dry-run", response_class=HTMLResponse)
def dry_run(
    request: Request,
    specification: str = Form(...),
) -> HTMLResponse:
    """Build and display a synchronization plan."""

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


@router.post("/sync", response_class=HTMLResponse)
def synchronize(
    request: Request,
    specification: str = Form(...),
    confirm: str | None = Form(None),
) -> HTMLResponse:
    """Execute synchronization against GitHub."""

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
                title="GitHub error",
                message="The current GitHub state could not be loaded.",
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

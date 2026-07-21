"""Web routes for GitHub Bootstrap."""

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
from github_bootstrap.specification.models import ProjectSpecification
from github_bootstrap.specification.parser import parse_specification
from github_bootstrap.specification.validator import (
    SpecificationValidationError,
    validate_specification,
)

WEB_DIRECTORY = Path(__file__).parent

templates = Jinja2Templates(
    directory=WEB_DIRECTORY / "templates",
)

router = APIRouter()


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


def _render(
    request: Request,
    specification: str,
    result: str,
    result_type: str,
) -> HTMLResponse:
    """Render the main web interface."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "specification": specification,
            "result": result,
            "result_type": result_type,
        },
    )


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Render the GitHub Bootstrap web interface."""

    specification = (
        "organization: example-org\n"
        "repository: example-repository\n\n"
        "project:\n"
        "  title: Example Development\n"
    )

    return _render(
        request=request,
        specification=specification,
        result="No operation executed yet.",
        result_type="neutral",
    )


@router.post("/validate", response_class=HTMLResponse)
def validate(
    request: Request,
    specification: str = Form(...),
) -> HTMLResponse:
    """Validate a YAML project specification."""

    try:
        _parse_specification(specification)

        return _render(
            request=request,
            specification=specification,
            result="Specification is valid.",
            result_type="success",
        )

    except (yaml.YAMLError, SpecificationValidationError) as error:
        return _render(
            request=request,
            specification=specification,
            result=f"Validation error: {error}",
            result_type="error",
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

        plan = synchronization_result.plan

        lines: list[str] = []

        executable_actions = plan.executable_actions()
        drift_actions = plan.drift_actions()

        if plan.is_empty():
            lines.append("Everything is up to date.")

        if executable_actions:
            lines.append("Synchronization plan:")

            for action in executable_actions:
                lines.append(
                    f"+ {action.description}",
                )

        if drift_actions:
            if lines:
                lines.append("")

            lines.append("Drift detected:")

            for action in drift_actions:
                lines.append(
                    f"! {action.description}",
                )

        return _render(
            request=request,
            specification=specification,
            result="\n".join(lines),
            result_type="success",
        )

    except (
        yaml.YAMLError,
        SpecificationValidationError,
    ) as error:
        return _render(
            request=request,
            specification=specification,
            result=f"Validation error: {error}",
            result_type="error",
        )

    except GitHubError as error:
        return _render(
            request=request,
            specification=specification,
            result=f"GitHub error: {error}",
            result_type="error",
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
            result=(
                "Synchronization was not executed.\n\n"
                "Confirm the operation before applying changes to GitHub."
            ),
            result_type="warning",
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

        plan = synchronization_result.plan

        executable_actions = plan.executable_actions()
        drift_actions = plan.drift_actions()

        lines: list[str] = []

        if executable_actions:
            lines.append("Synchronization complete.")
            lines.append("")
            lines.append("Applied synchronization plan:")

            for action in executable_actions:
                lines.append(
                    f"+ {action.description}",
                )
        else:
            lines.append("No executable actions to apply.")

        if drift_actions:
            lines.append("")
            lines.append("Drift detected:")

            for action in drift_actions:
                lines.append(
                    f"! {action.description}",
                )

        return _render(
            request=request,
            specification=specification,
            result="\n".join(lines),
            result_type="success",
        )

    except (
        yaml.YAMLError,
        SpecificationValidationError,
    ) as error:
        return _render(
            request=request,
            specification=specification,
            result=f"Validation error: {error}",
            result_type="error",
        )

    except GitHubError as error:
        return _render(
            request=request,
            specification=specification,
            result=f"GitHub error: {error}",
            result_type="error",
        )

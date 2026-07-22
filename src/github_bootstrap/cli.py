"""Command-line interface for GitHub Bootstrap."""

from pathlib import Path
from typing import Annotated, Any

import typer

from github_bootstrap import __version__
from github_bootstrap.application.synchronization_service import (
    SynchronizationService,
)
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.specification.loader import (
    SpecificationError,
    load_specification,
)
from github_bootstrap.specification.parser import parse_specification
from github_bootstrap.specification.validator import (
    SpecificationValidationError,
    validate_specification,
)

app = typer.Typer(
    name="github-bootstrap",
    help="Bootstrap GitHub Projects V2 from declarative YAML specifications.",
    no_args_is_help=True,
)


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output."),
    ] = False,
) -> None:
    _ = verbose


@app.command()
def version() -> None:
    """Show the application version."""
    typer.echo(f"github-bootstrap {__version__}")


@app.command()
def validate(
    file: Path = typer.Option(
        Path(".github-project.yaml"),
        "--file",
        "-f",
        help="Path to project specification.",
    ),
) -> None:
    """Validate a GitHub project specification."""
    try:
        specification: dict[str, Any] = load_specification(file)
    except SpecificationError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    try:
        validate_specification(specification)
    except SpecificationValidationError as error:
        typer.echo(f"Validation error: {error}")
        raise typer.Exit(code=1) from error

    typer.echo(f"Valid specification: {file}")


@app.command()
def github_check() -> None:
    """Check GitHub authentication."""
    try:
        client = GitHubClient()
        user = client.viewer()
    except GitHubError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    typer.echo("GitHub connection successful")
    typer.echo(f"Authenticated as: {user['login']}")


@app.command()
def sync(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show planned changes without applying them.",
    ),
) -> None:
    """Synchronize GitHub resources."""

    specification_file = Path(".github-project.yaml")

    client = GitHubClient()

    try:
        specification = load_specification(specification_file)
        validated_specification = validate_specification(specification)
        project_specification = parse_specification(validated_specification)

    except (
        SpecificationError,
        SpecificationValidationError,
    ) as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    service = SynchronizationService(client)

    try:
        if dry_run:
            result = service.dry_run(project_specification)
        else:
            result = service.synchronize(project_specification)

    except GitHubError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    plan = result.plan

    executable_actions = plan.executable_actions()
    drift_actions = plan.drift_actions()

    if plan.is_empty():
        typer.echo("Everything is up to date.")
        return

    if dry_run:
        if executable_actions:
            typer.echo("Synchronization plan:")

            for action in executable_actions:
                typer.echo(f"+ {action.description}")

        if drift_actions:
            typer.echo("Drift detected:")

            for action in drift_actions:
                typer.echo(f"! {action.description}")

        return

    if not executable_actions:
        if drift_actions:
            typer.echo("Drift detected:")

            for action in drift_actions:
                typer.echo(f"! {action.description}")

        typer.echo("No executable actions to apply.")
        return

    typer.echo("Synchronization complete.")


@app.command()
def web(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        help="Host interface for the web server.",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        help="Port for the web server.",
    ),
) -> None:
    """Run the GitHub Bootstrap web interface."""

    import uvicorn

    uvicorn.run(
        "github_bootstrap.web.app:app",
        host=host,
        port=port,
    )

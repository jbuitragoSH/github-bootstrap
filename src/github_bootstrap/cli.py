"""Command-line interface for GitHub Bootstrap."""

from pathlib import Path
from typing import Annotated, Any

import typer

from github_bootstrap import __version__
from github_bootstrap.github.client import (
    GitHubClient,
    GitHubError,
)
from github_bootstrap.planner.plan import create_plan
from github_bootstrap.specification.loader import (
    SpecificationError,
    load_specification,
)
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

    try:
        specification = load_specification(specification_file)
        project_specification = validate_specification(specification)
    except (
        SpecificationError,
        SpecificationValidationError,
    ) as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    try:
        client = GitHubClient()
        state = client.find_project(project_specification.project.title)
    except GitHubError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    plan = create_plan(
        project_specification,
        state,
    )
    if dry_run:
        typer.echo("Synchronization plan:")

        for action in plan.actions:
            typer.echo(f"+ {action}")

        return

    typer.echo("Execution is not implemented yet.")

"""Command-line interface for GitHub Bootstrap."""

from pathlib import Path
from typing import Annotated, Any

import typer

from github_bootstrap import __version__
from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.executor import Executor
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.planner.plan import create_plan
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

    try:
        project_state = client.projects.find(
            project_specification.project.title,
        )

        label_state = client.labels.find(
            owner=project_specification.organization,
            repository=project_specification.repository,
        )

        milestone_state = client.milestones.find(
            owner=project_specification.organization,
            repository=project_specification.repository,
        )

        field_state = client.fields.find(
            project_title=project_specification.project.title,
        )
        issue_state = client.issues.find(
            owner=project_specification.organization,
            repository=project_specification.repository,
        )

        github_state = GitHubState(
            project=project_state,
            labels=label_state,
            milestones=milestone_state,
            fields=field_state,
            issues=issue_state,
        )

    except GitHubError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    plan = create_plan(
        project_specification,
        github_state,
    )

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

    try:
        viewer = client.viewer()

        repository = client.repositories.find(
            owner=project_specification.organization,
            repository=project_specification.repository,
        )

    except GitHubError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    context = ExecutionContext(
        owner_id=viewer["id"],
        repository_id=repository.id,
        owner=project_specification.organization,
        repository=project_specification.repository,
        project_id=project_state.id,
        field_state=field_state,
    )

    executor = Executor(client)
    executor.execute(
        plan,
        context,
    )

    typer.echo("Synchronization complete.")

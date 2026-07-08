"""Command-line interface for GitHub Bootstrap."""

from pathlib import Path
from typing import Annotated, Any

import typer

from github_bootstrap import __version__
from github_bootstrap.specification.loader import (
    SpecificationError,
    load_specification,
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

    typer.echo(f"Valid specification: {file}")
    typer.echo(f"Keys: {list(specification.keys())}")

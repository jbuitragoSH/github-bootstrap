"""Command-line interface for GitHub Bootstrap."""

from typing import Annotated

import typer

from github_bootstrap import __version__

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
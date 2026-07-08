"""Tests for package metadata."""

from github_bootstrap import __version__


def test_version_is_defined() -> None:
    """The package exposes a version string."""
    assert __version__ == "0.1.0"

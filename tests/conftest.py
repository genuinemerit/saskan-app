# tests/conftest.py
import pytest
from typer.testing import CliRunner

from saskan.ui_cli.manage import app  # your Typer app


@pytest.fixture(scope="session")
def cli_app():
    """The Typer app under test."""
    return app


@pytest.fixture
def runner():
    """Fresh CliRunner per test (isolated filesystem by default if enabled)."""
    return CliRunner()

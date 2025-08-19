# tests/conftest.py

import pathlib
import sys

# Add project root so "saskan" can be imported when not installed
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from typer.testing import CliRunner  # noqa: E402

from saskan.ui_cli.manage import app  # noqa: E402


@pytest.fixture(scope="session")
def cli_app():
    """The Typer app under test."""
    return app


@pytest.fixture
def runner():
    """Fresh CliRunner per test (isolated filesystem by default if enabled)."""
    return CliRunner()

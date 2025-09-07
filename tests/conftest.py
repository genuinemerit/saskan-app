# tests/conftest.py

import pathlib
import socket
import sys

import pytest  # noqa: E402
from typer.testing import CliRunner

from saskan.ui_cli.manage import app

# Add project root so "saskan" can be imported when not installed
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def cli_app():
    """The Typer app under test."""
    return app


@pytest.fixture
def runner():
    """Fresh CliRunner per test (isolated filesystem by default if enabled)."""
    return CliRunner()


def free_port() -> int:
    """
    Find and return a free port on localhost.
    Usage: `port = free_port()`
    """
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    _, port = s.getsockname()
    s.close()
    return port

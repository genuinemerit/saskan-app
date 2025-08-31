# saskan/ui_cli/server/start.py

# from typing import Optional

import typer
from rich.console import Console

from saskan.infra.config.net import HOST, PORT
from saskan.infra.net.server import server

console = Console()


def start(
    host: str = typer.Option(HOST, "--host", "-h", help="Host to connect to"),
    port: int = typer.Option(PORT, "--port", "-p", help="Port to connect to"),
) -> None:
    """Start up the Saskan game server.
    Example usage:
    `saskan start`
    `saskan start --h wingchun --p 7777`
    """
    server.start_server(host, port)

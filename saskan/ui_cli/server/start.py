# saskan/ui_cli/server/start.py

from typing import Optional

import typer
from rich.console import Console

from saskan.infra.config.net import HOST, PORT
from saskan.infra.net.server import server

console = Console()


def start(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Host to connect to"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port to connect to"),
) -> None:
    """Start up the Saskan game server."""
    host = HOST if host is None else host
    port = PORT if port is None else int(port)
    server.start_server(host, port)

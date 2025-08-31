# saskan/ui_cli/client/connect.py

import secrets
from typing import Optional

import typer
from rich.console import Console

from saskan.infra.config.net import HOST, PORT
from saskan.infra.net.client import client

console = Console()


def connect(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Host to connect to"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port to connect to"),
    request: Optional[str] = typer.Option(
        None, "--request", "-r", help="Name of request to server"
    ),
    id: Optional[str] = typer.Option(None, "--id", "-i", help="Player ID"),
) -> None:
    """
    Connect to Saskan game server and send a valid request.
    1. If no host is provided, it defaults to the value in config.
    2. If no port is provided, it defaults to the value in config.
    3. If no request is provided, it defaults to "handshake".
    4. If no id is provided, a random id is generated.
    5. The function prints the status of the connection attempt.
    6. Example usage:
    `saskan connect --host localhost --port 8000 --request handshake --id my_player_id`
    """
    host = HOST if host is None else host
    port = PORT if port is None else port
    request = "system.handshake.request" if request == "handshake" else request
    request = "system.handshake.request" if request is None else request
    id = secrets.token_urlsafe(32) if id is None else id
    typer.echo(f"Attempting connection to {host}:{port}")
    status = client.send_msg_to_server(host, port, request, id)
    typer.echo(status)

# saskan/ui_cli/client/connect.py

import secrets

import typer
from rich.console import Console

import saskan.infra.config.services as svc
from saskan.infra.config.net import HOST, PORT
from saskan.infra.net.client import client
from saskan.tools.utils.match_semver import match_semver

console = Console()


def connect(
    host: str = typer.Option(HOST, "--host", "-h", help="Host to connect to"),
    port: int = typer.Option(PORT, "--port", "-p", help="Port to connect to"),
    protocol: str = typer.Option(
        svc.PROTOCOL_VERSION, "--protocol", "-s", help="Version of protocol"
    ),
    request: str = typer.Option("handshake", "--request", "-r", help="Name of request to server"),
    id: str = typer.Option(secrets.token_urlsafe(32), "--id", "-i", help="Player ID"),
    timeout: float = typer.Option(1.0, "--timeout", "-t", help="Timeout in seconds"),
) -> None:
    """
    Connect to Saskan game server and send a valid request. All parameters are optional.
    Example usages:
    `saskan connect`
    `saskan connect --host localhost --port 8000`
    `saskan connect --request handshake`
    `saskan connect -h 127.0.0.1 -p 7777 -s 0.1.0 -r handshake -i Player_1 -t 1.0`
    """
    request = "system.handshake.request" if request == "handshake" else request
    if not match_semver(protocol):
        protocol = svc.PROTOCOL_VERSION
    typer.echo(f"Attempting connection to {host}:{port}")
    reply = client.send_msg_to_server(host, port, protocol, request, id, timeout)
    typer.echo(reply)

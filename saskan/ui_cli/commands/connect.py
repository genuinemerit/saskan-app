# saskan/ui_cli/client/connect.py

import secrets

import typer

import saskan.infra.config.services as svc
from saskan.infra.config.net import HOST, PORT
from saskan.infra.i18n.localize import format_reply
from saskan.infra.net.client import client
from saskan.tools.utils.match_semver import match_semver


def connect(
    host: str = typer.Option(HOST, "--host", "-H", help="Host to connect to"),
    port: int = typer.Option(PORT, "--port", "-p", help="Port to connect to"),
    protocol: str = typer.Option(
        svc.PROTOCOL_VERSION, "--protocol", "-v", help="Version of protocol"
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
    `saskan connect -H 127.0.0.1 -p 7777 -v 0.1.0 -r handshake -i Player_1 -t 1.0`
    """
    request = "system.handshake.request" if request == "handshake" else request
    if not match_semver(protocol):
        protocol = svc.PROTOCOL_VERSION
    reply = client.send_msg_to_server(host, port, protocol, request, id, timeout)
    reply_code = reply["msg.reply.code"]
    del reply["msg.reply.code"]
    reply_msg = format_reply(reply)
    typer.echo(reply_msg)
    raise typer.Exit(reply_code)

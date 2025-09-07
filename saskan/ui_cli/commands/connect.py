# saskan/ui_cli/client/connect.py

import secrets

import typer

import saskan.infra.config.services as svc
from saskan.infra.config.net import HOST, PORT
from saskan.infra.i18n import lookup
from saskan.infra.net.client import client

# from saskan.infra.schema.dto import RejectDTO, WelcomeDTO
from saskan.tools.utils.match_semver import match_semver


def format_reply(reply: dict) -> str:
    """
    If an item in the reply is keyed as i18n_id, translate the message string.
    If a key appears in the i18n lookup table, translate the label.
    Drop the reply_code key; it is handled by Typer exit code.
    :return: str translated message
    """
    msg_string = ""
    for key, value in reply.items():
        if key == "reply_code":
            continue
        elif key == "i18n_id":
            if value is not None:
                msg_tag = lookup.get_text("client_tag", fallback="[CLIENT] ")
                msg_label = lookup.get_text("message", fallback="Message: ")
                msg_text = lookup.get_text(value, fallback="No message provided")
        else:
            if key in ("message"):
                msg_tag = lookup.get_text("client_tag", fallback="[CLIENT] ")
            else:
                msg_tag = ""
            if key in ("motd"):
                msg_label = ""
            else:
                msg_label = lookup.get_text(key, fallback=f"{key.capitalize()}: ")
            if isinstance(value, list):
                msg_text = "["
                for text in value:
                    msg_text += lookup.get_text(text, fallback=text) + ", "
                msg_text = msg_text.rstrip(", ") + "]"
            else:
                msg_text = lookup.get_text(value, fallback=value)
        msg_string += f"{msg_tag}{msg_label}{msg_text}\n"
    return msg_string


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
    reply_msg = format_reply(reply)
    typer.echo(reply_msg)
    raise typer.Exit(code=reply["reply_code"])

# saskan/ui_cli/client/version.py

import json

import typer
from rich.console import Console

import saskan.infra.config.services as svc
from saskan.tools.utils.platform import sys_info

console = Console()


def echo_dict(title: str, d: dict):
    typer.echo(f"\n{title}:")
    for k, v in d.items():
        typer.echo(f"  {k:20}: {v}")


def version() -> None:
    """
    Display platform info and Saskan configuration info.
    Example usage:
    `saskan version`
    """
    system_info = json.loads(sys_info())
    client_msgs = [item for item in svc.ALLOWED_MESSAGE_NAMES if "handshake" in item.lower()]
    saskan_info = {
        "protocol version": svc.PROTOCOL_VERSION,
        "allowed client messages": client_msgs,
        "default language": svc.DEFAULT_LANG,
        "supported languages": svc.SUPPORTED_LANGS,
    }
    echo_dict("System Info", system_info)
    echo_dict("Saskan Info", saskan_info)

# saskan/ui_cli/commands/greet.py
from typing import Optional

import typer
from rich.console import Console

console = Console()


def hello(name: Optional[str] = typer.Option(None, "--name", "-n", help="Name to greet")) -> None:
    """Print a friendly greeting.
    Example usage:
    `saskan greet --name Alice`
    `saskan greet`
    """
    who = name or "Saskan Lands"
    console.print(f"Hello {who}!")

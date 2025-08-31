# saskan/ui_cli/manage.py
import typer

from saskan.infra.log.logger import configure
from saskan.ui_cli.client.connect import connect
from saskan.ui_cli.commands.greet import hello
from saskan.ui_cli.server.start import start

configure()  # Setup logging for CLI itself using defaults in infra/log/logger.py

app = typer.Typer(help="Saskan CLI", no_args_is_help=True)  # show help if no subcommand


@app.callback()
def main():
    """Saskan CLI."""
    # No params here → no root options leak into help
    pass


# Register subcommands
app.command("hello")(hello)
app.command("connect")(connect)
app.command("start")(start)


def cli():
    app()


if __name__ == "__main__":
    app()

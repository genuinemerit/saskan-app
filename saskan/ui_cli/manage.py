# saskan/ui_cli/manage.py
import typer

from saskan.infra.log.logger import configure
from saskan.ui_cli.commands.connect import connect
from saskan.ui_cli.commands.greet import hello
from saskan.ui_cli.commands.start import start
from saskan.ui_cli.commands.version import version

configure()  # Setup logging for CLI using defaults in infra/log/logger.py

# show help if no subcommand
help_text = (
    "Saskantinon Command Line Interface\n\n" + "saskan [COMMAND] --help for more info on a command"
)
app = typer.Typer(help=help_text, no_args_is_help=True)


@app.callback()
def main():
    """Saskan CLI."""
    # No params here → no root options leak into help
    pass


# Register subcommands
app.command("hello")(hello)
app.command("version")(version)
app.command("start")(start)
app.command("connect")(connect)


def cli():
    app()


if __name__ == "__main__":
    app()

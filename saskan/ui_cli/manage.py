# saskan/ui_cli/manage.py
import typer

from saskan.ui_cli.commands.greet import hello

app = typer.Typer(help="Saskan CLI", no_args_is_help=True)  # show help if no subcommand


@app.callback()
def main():
    """Saskan CLI."""
    # No params here → no root options leak into help
    pass


# Register subcommand
app.command("hello")(hello)


def cli():
    app()


if __name__ == "__main__":
    app()

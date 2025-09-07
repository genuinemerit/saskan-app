# tests/test_cli_hello.py
"""
Tests for saskan.ui_cli.commands.hello
"""


def test_hello_default(runner, cli_app):
    result = runner.invoke(cli_app, ["hello"])
    assert result.exit_code == 0
    assert "Hello Saskan Lands!" in result.stdout


def test_hello_named(runner, cli_app):
    result = runner.invoke(cli_app, ["hello", "--name", "Phoenix"])
    assert result.exit_code == 0
    assert "Hello Phoenix!" in result.stdout

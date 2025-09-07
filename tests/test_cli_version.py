# tests/test_cli_version.py
"""
Tests for saskan.ui_cli.commands.version
"""


def test_version(runner, cli_app):
    result = runner.invoke(cli_app, ["version"])
    assert result.exit_code == 0
    assert "System Info:" in result.stdout
    assert "platform-version" in result.stdout
    assert "Saskan Info:" in result.stdout
    assert "protocol version" in result.stdout
    assert "supported languages" in result.stdout

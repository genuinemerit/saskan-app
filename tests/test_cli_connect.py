# tests/test_cli_connect.py
"""
Tests for saskan.ui_cli.commands.connect
"""

from pprint import pprint as pp  # noqa: F401


def test_connect_en(runner, cli_app, monkeypatch):
    # Server is not running, so test fail condidtion (English)
    monkeypatch.setenv("SASKAN_LANG", "en-US")
    result = runner.invoke(cli_app, ["connect"])
    assert result.exit_code == 1
    assert result.output.strip() == "[CLIENT] Message: Connection refused by the server."


def test_connect_es(runner, cli_app, monkeypatch):
    # Server is not running, so test fail condidtion (Spanish)
    monkeypatch.setenv("SASKAN_LANG", "es-ES")
    result = runner.invoke(cli_app, ["connect"])
    assert result.exit_code == 1
    assert result.output.strip() == "[CLIENTE] Mensaje: Conexión rechazada por el servidor."


def test_connect_happy_path(runner, cli_app, monkeypatch):
    # Simulate a successful server response to handshake request
    def fake_send(host, port, protocol, request, id, timeout):
        return {
            "message": "Welcome to Saskan server",
            "protocol": ["0.1.0"],
            "session_id": "abccdefg",
            "motd": "ui.message_of_the_day",
            "reply_code": 0,
        }

    monkeypatch.setenv("SASKAN_LANG", "en-US")
    monkeypatch.setattr("saskan.infra.net.client.client.send_msg_to_server", fake_send)
    result = runner.invoke(cli_app, ["connect"])
    assert "Welcome to the Saskan game server!" in result.stdout
    assert result.exit_code == 0


def test_connect_protocol_mismatch(runner, cli_app, monkeypatch):
    # Simulate an unsuccessful server response to handshake request
    def fake_send(host, port, protocol, request, id, timeout):
        return {
            "message": "Connection rejected",
            "protocol": ["9.9.9"],
            "session_id": "abccdefg",
            "Details": "protocol_version_unsupported",
            "reply_code": 2,
        }

    monkeypatch.setenv("SASKAN_LANG", "en-US")
    monkeypatch.setattr("saskan.infra.net.client.client.send_msg_to_server", fake_send)
    result = runner.invoke(cli_app, ["connect"])
    assert "Connection rejected" in result.stdout
    assert result.exit_code == 2

# tests/test_cli_connect.py
"""
Tests for saskan.ui_cli.commands.connect
"""

from pprint import pprint as pp  # noqa: F401

from saskan.infra.schema.dto import RejectDTO, WelcomeDTO

# --- Monkey patching functions ---------------------------------------


def fake_fail(host, port, protocol, request, id, timeout):
    reject = RejectDTO(
        reason="protocol_version_unsupported",
        i18n_id="system.reject.protocol_version_unsupported",
        details="Requested protocol version is not supported",
        supported=["0.1.0"],
    )
    return {
        **reject.__dict__,
        "msg.message.name": "system.reject",
        "msg.reply.code": 2,
    }


def fake_send(host, port, protocol, request, id, timeout):
    welcome = WelcomeDTO(
        server_version="0.1.0",
        session_id="abccdefg",
        motd="ui.message_of_the_day",
        i18n_id="ui.message.handshake_welcome",
        accepted_capabilities=["cap.chat", "cap.assets"],
    )
    return {
        **welcome.__dict__,
        "msg.message.name": "system.welcome",
        "msg.reply.code": 0,
    }


# --- Tests ---------------------------------------------------------------


def test_connect_en(runner, cli_app, monkeypatch):
    # Server is not running, so test fail condidtion (English)
    monkeypatch.setenv("SASKAN_LANG", "en-US")
    result = runner.invoke(cli_app, ["connect"])
    assert result.exit_code == 1
    assert result.output.strip() == "Message: Connection refused by the server."


def test_connect_es(runner, cli_app, monkeypatch):
    # Server is not running, so test fail condidtion (Spanish)
    monkeypatch.setenv("SASKAN_LANG", "es-ES")
    result = runner.invoke(cli_app, ["connect"])
    assert result.exit_code == 1
    assert result.output.strip() == "Mensaje: Conexión rechazada por el servidor."


def test_connect_happy_path_en(runner, cli_app, monkeypatch):
    """
    Simulate a successful server response to handshake request
    ui.message_of_the_day: "Welcome to the Saskan Lands game server!"  (en-US)
    """
    monkeypatch.setenv("SASKAN_LANG", "en-US")
    monkeypatch.setattr("saskan.infra.net.client.client.send_msg_to_server", fake_send)
    result = runner.invoke(cli_app, ["connect"])
    assert "Welcome to the Saskan Lands game server!" in result.stdout
    assert "Message name: system.welcome\n" in result.stdout
    assert "[CLIENT] Message: ui.message.handshake_welcome\n" in result.stdout
    assert result.exit_code == 0


def test_connect_happy_path_es(runner, cli_app, monkeypatch):
    """
    Simulate a successful server response to handshake request
    ui.message_of_the_day: "¡Bienvenido/a al servidor de juego de Saskan Lands!"
    (es-ES)
    """
    monkeypatch.setenv("SASKAN_LANG", "es-ES")
    monkeypatch.setattr("saskan.infra.net.client.client.send_msg_to_server", fake_send)
    result = runner.invoke(cli_app, ["connect"])
    assert "¡Bienvenido/a al servidor de juego de Saskan Lands!" in result.stdout
    assert "ombre del mensaje: system.welcome\n" in result.stdout
    assert "[CLIENTE] Mensaje: ui.message.handshake_welcome\n" in result.stdout
    assert result.exit_code == 0


def test_connect_protocol_mismatch(runner, cli_app, monkeypatch):
    # Simulate an unsuccessful server response to handshake request
    def fake_send(host, port, protocol, request, id, timeout):
        return {
            "message": "Connection rejected",
            "protocol": ["9.9.9"],
            "session_id": "abccdefg",
            "Details": "protocol_version_unsupported",
            "reply_code": 0,
        }

    monkeypatch.setenv("SASKAN_LANG", "en-US")
    monkeypatch.setattr("saskan.infra.net.client.client.send_msg_to_server", fake_fail)
    result = runner.invoke(cli_app, ["connect"])
    assert "Requested protocol version is not supported" in result.stdout
    assert "[CLIENT] Message: system.reject.protocol_version_unsupported\n" in result.stdout
    assert result.exit_code == 2

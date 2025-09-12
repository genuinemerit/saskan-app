# tests/test_client_unit.py
"""
Tests for saskan.infra.net.client.client
"""

import json
import socket
import threading
from pprint import pprint as pp  # noqa: F401

from saskan.infra.net.client import client

WELCOME = {
    "id": "id-123",
    "ver": 1,
    "name": "system.welcome",
    "ts": "2025-09-06T21:38:38.842+00:00",
    "meta": {"protocol": "0.1.0"},
    "payload": {"server_version": "0.1.0", "session_id": "abc", "motd": "ui.message_of_the_day"},
}


def test_format_request_msg_ndjson():
    # Verify good formatting of the handshake request message
    b = client.format_request_msg("0.1.0", "system.handshake.request", "id-123")
    assert b.endswith(b"\n")
    msg = json.loads(b.decode("utf-8").rstrip("\n"))
    assert msg["name"] == "system.handshake.request"
    assert msg["meta"]["protocol"] == "0.1.0"
    assert isinstance(msg["ver"], int)


def _server_sim(sock):
    # one-exchange: read once (ignored), reply once, close
    _ = sock.recv(8192)
    sock.sendall((json.dumps(WELCOME) + "\n").encode("utf-8"))
    sock.close()


def test_send_msg_to_server_reads_full_line(monkeypatch):
    # Intercept socket creation and connect to use a socketpair
    # This generates python warnings about unclosed sockets, ignore them
    # To not display the warnings, run pytest with `-p no:warnings`
    c, s = socket.socketpair()
    t = threading.Thread(target=_server_sim, args=(s,), daemon=True)
    t.start()

    def fake_socket(*args, **kwargs):
        return c

    monkeypatch.setattr("socket.socket", lambda *a, **k: fake_socket())

    out = client.send_msg_to_server(
        "ignored", 0, "0.1.0", "system.handshake.request", "id-123", timeout=1.0
    )
    assert "message" in out.keys()

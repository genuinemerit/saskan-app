# tests/test_server_integration.py
import json
import socket
import threading
import time
from pprint import pprint as pp  # noqa: F401

import saskan.infra.config.services as svc
from saskan.infra.net.server import server  # your server entrypoint
from saskan.tools.utils.stamps import create_iso_timestamp


def _run_server(host, port):
    server.start_server(host, port)


def _connect_and_send(host, port, msg: dict, timeout=1.0) -> dict:
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        s.settimeout(timeout)
        raw = s.makefile("rb", buffering=0).readline(8192).rstrip(b"\r\n").decode("utf-8")
    return json.loads(raw)


def test_ready_happy_path(monkeypatch):
    host, _ = "127.0.0.1", 0  # ephemeral port
    monkeypatch.setattr(svc, "SERVER_TIMEOUT", 5.0)  # plenty of time
    t = threading.Thread(target=_run_server, args=(host, 7777), daemon=True)
    t.start()
    time.sleep(0.2)

    req = {
        "id": "id1",
        "ver": 1,
        "name": "system.handshake.request",
        "ts": create_iso_timestamp(),
        "meta": {"protocol": svc.PROTOCOL_VERSION},
        "payload": {"client_version": "0.1.0"},
    }
    reply = _connect_and_send(host, 7777, req)

    pp((reply))

    assert reply["name"] == "system.welcome"


def test_draining_reject(monkeypatch):
    host, port = "127.0.0.1", 8888
    monkeypatch.setattr(svc, "SERVER_TIMEOUT", 0.5)  # go idle quickly
    monkeypatch.setattr(svc, "IDLE_POLL_INTERVAL", 0.1)
    monkeypatch.setattr(svc, "DRAIN_GRACE_PERIOD", 0.5)

    t = threading.Thread(target=_run_server, args=(host, port), daemon=True)
    t.start()
    time.sleep(1.0)  # let it flip to DRAINING

    req = {
        "id": "id2",
        "ver": 1,
        "name": "system.handshake.request",
        "ts": create_iso_timestamp(),
        "meta": {"protocol": svc.PROTOCOL_VERSION},
        "payload": {"client_version": "0.1.0"},
    }
    reply = _connect_and_send(host, port, req)
    assert reply["name"] == "system.reject"
    assert reply["payload"]["reason"] == "server_not_ready"

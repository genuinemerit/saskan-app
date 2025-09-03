# saskan/infra/net/server/greet.py
"""
:module:   server.py
:author:   PQ
:date:     2024-06-20
:copyright: Copyright (c) 2025 Genuine Merit Software

Simple TCP server for handling multiplayer game connections,
with one-exchange request-response protocol.

Mockup example using socketserver.
Clients can register, send a handshake message.
This is a skeleton; real game logic and error handling are omitted for brevity.

- Terminal 1: Run the server (server.py) using CLI: `saskan start`
- Terminal 2, 3, 4: Run client programs (client.py) with different player IDs:
    `saskan connect` (ID is assigned if one is not provided)

@TODO:
- Review logging syntax per ADR:
  * [x] Logging: `READY`, `CONN_OPEN/CLOSE`, `HELLO outcome=… reason? latency_ms=…`
"""

from __future__ import annotations

import json
import secrets
import socketserver
import threading
import time
from collections.abc import Iterable
from importlib.resources import files
from pprint import pprint as pp  # noqa F401
from typing import Any, Dict, List, Optional, Tuple, Type, TypedDict

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from saskan.infra import schema
from saskan.infra.config import services as svc
from saskan.infra.config.net import HOST, PORT
from saskan.infra.log.logger import get_logger
from saskan.infra.schema import convert, dto, validator
from saskan.tools.utils import stamps

# Type aliases

Address = Tuple[str, int]


class Diagnostics(TypedDict):
    errors: list[str]


class Response(TypedDict):
    ok: bool
    reason: Optional[str]
    supported: List[str]
    diagnostics: Diagnostics
    token: str


# Schema caching
ENVELOPE = json.loads(files(schema).joinpath("envelope.schema.json").read_text())
HREQ = json.loads(files(schema).joinpath("handshake.request.schema.json").read_text())
V_ENVELOPE = Draft202012Validator(ENVELOPE)
V_HREQ = Draft202012Validator(HREQ)


# Functional code


class IdleShutdownServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Shutdown server after idle timeout.
    """

    allow_reuse_address = True
    daemon_threads = True  # kill handler threads on shutdown

    def __init__(
        self,
        server_address: Address,
        RequestHandlerClass: Type[socketserver.BaseRequestHandler],
        bind_and_activate: bool = True,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.idle_timeout: float = float(svc.SERVER_TIMEOUT)
        self._last_activity = time.monotonic()
        self._lock = threading.Lock()
        self.clients: Dict[str, Dict[str, Any]] = {}

    def touch(self) -> None:
        # mark activity on any connection or message
        with self._lock:
            self._last_activity = time.monotonic()

    def seconds_since_activity(self) -> float:
        with self._lock:
            return time.monotonic() - self._last_activity

    def drain_and_close(self) -> None:
        elapsed = self.seconds_since_activity()
        # print(f"Idle elapsed: {elapsed:.1f}s (timeout={self.idle_timeout}s)")
        if elapsed >= self.idle_timeout:
            print(f"Draining and closing connections after {elapsed:.1f}s of inactivity.")
            # Unregister any active clients
            for token in list(self.clients.keys()):
                # mirror the unregister semantics
                del self.clients[token]
            # orderly server shutdown
            self.shutdown()  # stop serve_forever loop
            self.server_close()  # release the socket


def _idle_watchdog(server: IdleShutdownServer, poll=0.5):
    # runs in a background thread
    while True:
        time.sleep(poll)
        if server.seconds_since_activity() >= server.idle_timeout:
            server.drain_and_close()
            break


class GameRequestHandler(socketserver.BaseRequestHandler):
    """
    Handle incoming client requests.
    """

    server: IdleShutdownServer

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # self.server.game = Game()  # Future -- Initialize game state
        # self.client_queue: dict = {}  # Future -- message queue for client
        self.srv_log = get_logger("saskan.server")
        super().__init__(*args, **kwargs)

    def _read_one_line(self, max_bytes: int = 8192) -> str:
        """
        Implement a simple line-based protocol (NDJSON).
        Read until newline, up to max_bytes (default 8192).
        Raise ValueError if line too long.
        Raise ConnectionError if client closes connection.
        """
        buf = bytearray()
        while True:
            chunk = self.request.recv(1024)
            if not chunk:
                raise ConnectionError("client closed")
            buf += chunk
            if len(buf) > max_bytes:
                raise ValueError("line too long")
            if buf.endswith(b"\n"):
                break
        return buf.rstrip(b"\r\n").decode("utf-8")

    def log_message_received(self, token: str, msg: dict) -> None:
        log_msg = {
            "event": "log_message",
            "from": token,
            "message": msg,
            "ts": stamps.create_iso_timestamp(),
        }
        self.srv_log.info(log_msg)

    def handle(self) -> None:
        """
        Per ADR-009, read exactly one NDJSON message, reply once, then close connection.
        Future: keep connection open for multiple exchanges.
        """
        self.server.touch()
        self.request.settimeout(svc.SERVER_TIMEOUT)  # idle timeout on socket
        try:
            token = self.register_client()
            response: Response = {
                "ok": True,
                "reason": None,
                "supported": svc.SUPPORTED_PROTOCOLS,
                "diagnostics": Diagnostics(errors=[]),
                "token": token,
            }
            line = self._read_one_line(max_bytes=8192)
            msg_in = json.loads(line)

            self.log_message_received(token, msg_in)

            if response["ok"]:
                response = self.review_protocol(response, msg_in)
            if response["ok"]:
                response = self.review_message(response, msg_in)

            self.reply_message(response, msg_in)
        finally:
            self.unregister_client(response["token"])
            self.request.close()

    def register_client(self) -> str:
        """
        Future.
        Generate a session token (id) for the client.
        In a real game, this step would involve authentication and player state setup.
        For now, just store the client address.
        :return: (str) token for the client session
        """
        # id = self.server.game.register_player(self.client_address) -- Future
        token = secrets.token_urlsafe(32)
        self.server.clients[token] = {"sock": self.client_address}
        return token

    def unregister_client(self, token: str) -> None:
        """
        Future.
        Remove a client from the game's active list of players.
        """
        # self.server.game.unregister_player(response['id']) -- Future
        if token in self.server.clients:
            print(f"Unregistering client with token {token}")
            del self.server.clients[token]

    def review_protocol(self, response: Response, msg_in: Dict) -> Response:
        """
        Run validation using agreed-on protocols for PR-2.

        :param response: (dict) The current response dictionary.
        :param msg_in: (dict) The incoming message dictionary.
        :return: (dict) Updated response dictionary.
        """
        ok, reason, errs = validator.validate_message_name(msg_in["name"])
        response.update(
            {"ok": ok, "reason": reason, "diagnostics": {"errors": [str(e) for e in errs]}}
        )
        if response["ok"]:
            protocol = msg_in.get("meta", {}).get("protocol", "")
            ok, reason, supported, errs = validator.validate_protocol(protocol)
            response.update(
                {
                    "ok": ok,
                    "reason": reason,
                    "supported": supported,
                    "diagnostics": {"errors": [str(e) for e in errs]},
                }
            )
        return response

    def review_message(self, response: Response, msg_in: Dict) -> Response:
        """
        :param: (dict) response
        :param: (dict) msg_in
        Run validation on message content using agreed-on rules for PR-2.
        First validate the envelope, then the payload.
        :return: (dict) response
        """

        def fmt_diagnostics(response: Response, errors: Iterable[ValidationError]) -> Response:
            response["ok"] = False
            response["reason"] = "invalid_contract"
            response["diagnostics"] = {"errors": [str(e) for e in errors]}
            return response

        # Validate envelope
        env_errs: list[ValidationError] = list(V_ENVELOPE.iter_errors(msg_in))
        env_errs.sort(key=lambda e: e.path)
        if env_errs:
            response = fmt_diagnostics(response, env_errs)
        if response["ok"]:
            # Validate payload based on message name
            pay_errs: list[ValidationError] = list(V_HREQ.iter_errors(msg_in["payload"]))
            pay_errs.sort(key=lambda e: e.path)
            if pay_errs:
                response = fmt_diagnostics(response, pay_errs)
        return response

    def system_welcome(self, token: str, msg: Dict) -> Dict:
        """
        Fill in the payload for a welcome message.
        :param: (str) token = client address
        :param: (dict) msg = message envelope to fill in
        """
        msg["name"] = "system.welcome"
        payload = dto.WelcomeDTO(
            server_version=svc.SERVER_VERSION,
            session_id=token,
            motd=svc.MOTD,
            i18n_id=svc.I18N_WELCOME,
            accepted_capabilities=list(svc.ACCEPTED_CAPABILITIES),
        )
        msg["payload"] = convert.payload_from_welcome(payload)
        return msg

    def system_reject(self, response: Response, msg: Dict) -> Dict:
        """
        Fill in the payload for a reject message.
        :param: (str) response = information about the rejection
        :param: (dict) msg = message envelope to fill in
        """
        msg["name"] = "system.reject"
        reason = response["reason"] or "invalid_contract"
        i18n_id = (
            svc.I18N_REJECT_PROTOCOL
            if response["reason"] == "protocol_version_unsupported"
            else (
                svc.I18N_REJECT_NOT_READY
                if response["reason"] == "server_not_ready"
                else svc.I18N_REJECT_GENERIC
            )
        )
        payload = dto.RejectDTO(
            reason=reason,
            i18n_id=i18n_id,
            details="; ".join(response["diagnostics"].get("errors", [])),
            supported=response.get("supported") or None,
        )
        msg["payload"] = convert.payload_from_reject(payload)
        return msg

    def reply_message(self, response: Response, msg_in: Dict) -> None:
        """
        :param: (dict) response
        :param: (dict) msg_in
        Send message back to client based on the response to their request.
        Only send message if we have an active request.
        :return: None
        """
        envelope = dto.EnvelopeDTO(
            id=msg_in["id"],
            ver=1,
            name="",
            ts=stamps.create_iso_timestamp(),
            meta={"protocol": "0.1.0"},
            payload={},
        )
        msg = convert.envelope_from_dto(envelope)
        if response["ok"]:
            msg = self.system_welcome(response["token"], msg)
        else:
            msg = self.system_reject(response, msg)

        msg_ndjson = f"{json.dumps(msg)}\n".encode("utf-8")
        if msg_in:
            self.request.sendall(msg_ndjson)


def start_server(host: str = HOST, port: int = PORT) -> None:
    srv_log = get_logger("saskan.server")
    print(f"\nStarting server on {host}:{port}")

    server = IdleShutdownServer((host, port), GameRequestHandler)
    # start the idle watchdog
    threading.Thread(target=_idle_watchdog, args=(server,), daemon=True).start()

    def log_server_status(status: str, host: str, port: int) -> None:
        log_msg = {
            "event": status,
            "host": host,
            "port": port,
            "ts": stamps.create_iso_timestamp(),
        }
        srv_log.info(log_msg)

    try:
        print(f"\n{svc.MOTD}")
        log_server_status("server_starting", host, port)
        server.serve_forever()  # returns after shutdown()
        log_server_status("server_stopped", host, port)
    finally:
        # double-close safe; ensures socket is released
        server.server_close()

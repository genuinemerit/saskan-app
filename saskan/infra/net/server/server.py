# saskan/infra/net/server/greet.py
"""
:module:   server.py
:author:   PQ
:date:     2024-06-20
:copyright: Copyright (c) 2025 Genuine Merit Software

Simple TCP server for handling multiplayer game connections,
with one-exchange request-response protocol.

Mockup example using socketserver.
Clients can send a handshake message.
This is a skeleton; real game logic and error handling are omitted for brevity.

- Terminal 1: Run the server (server.py) using CLI: `saskan start`
- Terminal 2, 3, 4: Run client programs (client.py) with different player IDs:
    `saskan connect` (ID is assigned if one is not provided)

The server can be in one of three states:
- READY: acept connections, read one line, reply either welcome or reject, close connection
- DRAINING: accept but do not read connections, reply system.reject with reason server_not_ready,
            close connection
- STOPPED: do not accept connections, listener socket is closed
"""

from __future__ import annotations

import json
import secrets
import socket
import socketserver
import threading
import time
from collections.abc import Iterable
from enum import Enum
from importlib.resources import files
from pprint import pprint as pp  # noqa F401
from typing import Any, Optional, Tuple, Type, TypedDict

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from saskan.infra import schema
from saskan.infra.config import services as svc
from saskan.infra.config.net import HOST, PORT
from saskan.infra.i18n.localize import lookup
from saskan.infra.log import events as ev
from saskan.infra.schema import convert, dto, validator
from saskan.infra.schema.types import Diagnostics
from saskan.tools.utils import stamps

# --- Type aliases ---

Address = Tuple[str, int]


class Response(TypedDict):
    ok: bool
    reason: Optional[str]
    supported: list[str]
    diagnostics: Diagnostics
    protocol: Optional[str]
    token: str


class ServerState(Enum):
    READY = "READY"
    DRAINING = "DRAINING"
    STOPPED = "STOPPED"


# --- Diagnostics helpers ---
def diag_ok() -> Diagnostics:
    return {"errors": []}


def diag_join(diag: Diagnostics) -> str:
    """Turn {"errors": [...]} into details string."""
    errs = diag.get("errors") or []
    return "; ".join(errs)


def diag_from_validation(errs: Iterable[ValidationError]) -> Diagnostics:
    """Normalize jsonschema errors → list[str] with stable paths."""
    out: list[str] = []
    for e in sorted(errs, key=lambda x: (list(x.path), x.message)):
        path = "/".join(map(str, e.path))  # e.g., "payload/client_version"
        out.append(f"{path}: {e.message}" if path else e.message)
    return {"errors": out}


def fmt_diagnostics(response: Response, errors: Iterable[ValidationError]) -> Response:
    response["ok"] = False
    response["reason"] = "invalid_contract"
    response["diagnostics"] = diag_from_validation(errors)
    return response


# --- Schema caching ---
ENVELOPE = json.loads(files(schema).joinpath("envelope.schema.json").read_text())
HREQ = json.loads(files(schema).joinpath("handshake.request.schema.json").read_text())
V_ENVELOPE = Draft202012Validator(ENVELOPE)
V_HREQ = Draft202012Validator(HREQ)


# Functional code


class IdleShutdownServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Shutdown server. This server runs separately from the main TCP server.
    The instance defines the attributes of the shutdown server and provides tracking methods.
    More complex shutdown logic occurs in the _idle_watchdog() function,
      which runs in a background thread.
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
        self.clients: dict[str, dict[str, Any]] = {}
        self._active = 0  # number of active connections
        self.state = ServerState.READY

    def touch(self) -> None:
        """
        Mark time of activity on any connection or message.
        """
        with self._lock:
            self._last_activity = time.monotonic()

    def seconds_since_activity(self) -> float:
        """
        Compute time since last touch.
        """
        with self._lock:
            return time.monotonic() - self._last_activity

    def increment_active(self) -> None:
        """
        Increment counter of active connections.
        """
        with self._lock:
            self._active += 1

    def decrement_active(self) -> None:
        """
        Decrement counter of active connections.
        """
        with self._lock:
            if self._active > 0:
                self._active -= 1


def _register_session(client_address: str, server: IdleShutdownServer) -> str:
    """
    :param: (str) client_address
    :param: (IdleShutdownServer) server
    Future.
    Generate a session token (id) for the client and associate it with the client address.
    In a real game, this step would involve authentication and player state setup and allows
      for maintaining state between reconnects.
    For now, just store the client address.
    :return: (str) token for the client session
    """
    # id = self.server.game.register_player(self.client_address) -- Future
    token = secrets.token_urlsafe(32)
    server.clients[token] = {"sock": client_address}
    return token


def _unregister_session(token: str, server: IdleShutdownServer) -> None:
    """
    :param: (str) token
    :param: (IdleShutdownServer) server
    Future.
    Remove a client from the game's active list of sessions.
    For now, the queue gets cleaned out when the server stops.
    """
    # self.server.game.unregister_player(response['id']) -- Future
    if token in server.clients:
        print(f"Unregistering client with token {token}")
        del server.clients[token]


def _idle_watchdog(server: IdleShutdownServer) -> None:
    """
    Runs in a background thread, using the ShutdownServer instance.
    Handles server state transitions based on idle time and active connections.
    Initiate draining state after idle timeout interval.
    After draining, close the server socket.
    """
    while True:
        host = server.server_address[0]
        port = server.server_address[1]
        time.sleep(svc.IDLE_POLL_INTERVAL)
        idle = server.seconds_since_activity()
        with server._lock:
            state = server.state
            active = server._active
        if state == ServerState.READY and idle >= server.idle_timeout:
            server.state = ServerState.DRAINING
            drain_started = time.monotonic()
            ev.draining_start(host=str(host), port=int(port))
            print("\nServer started draining")
        elif state == ServerState.DRAINING:
            if active == 0 and (
                drain_started and time.monotonic() - drain_started >= svc.DRAIN_GRACE_PERIOD
            ):
                server.state = ServerState.STOPPED
                for token in list(server.clients.keys()):
                    _unregister_session(token, server)
                server.shutdown()  # stop serve_forever loop
                server.server_close()  # release the socket
                break


class GameRequestHandler(socketserver.BaseRequestHandler):
    """
    Handle incoming client requests. This is the base class for socketserver.
    This is a one-exchange protocol: read one message, reply once, close connection.
    In the future, this will be extended to a multi-message protocol and become the
      main game server.  It is passed in to the IdleShutdownServer instance as a TCP socket.
    The actual server instance is available in this class as `self.server`.
    """

    server: IdleShutdownServer

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # self.server.game = Game()  # Future -- Initialize game state
        super().__init__(*args, **kwargs)
        self.token: str = ""  # session token (future use)
        self.timer: float = 0.0

    def _read_one_line(self) -> str:
        """
        Helper method to read one line from the socket.
        Implement a simple line-based protocol (NDJSON).
        Read until newline, up to max_bytes; default set in services.py.
        Raise ValueError if line too long.
        Raise ConnectionError if client closes connection.
        """
        buf = bytearray()
        while True:
            chunk = self.request.recv(1024)
            if not chunk:
                raise ConnectionError("client closed")
            buf += chunk
            if len(buf) > svc.MAX_MESSAGE_SIZE:
                raise ValueError("line too long")
            if buf.endswith(b"\n"):
                break
        return buf.rstrip(b"\r\n").decode("utf-8")

    def handle(self) -> None:
        """
        If state is not READY:
            Reply once with system.reject (reason=server_not_ready), then close connection.
        Otherwise:
            Read exactly one NDJSON message, reply once, then close connection after timeout.
        Future: keep connection open for multiple exchanges.
        """

        def server_not_ready_response() -> Response:
            return {
                "ok": False,
                "reason": "server_not_ready",
                "supported": svc.SUPPORTED_PROTOCOLS,
                "diagnostics": diag_ok(),
                "token": "",
                "protocol": None,
            }

        def server_welcome_or_reject_response(msg_in: dict) -> Response:
            response: Response = {
                "ok": True,
                "reason": None,
                "supported": svc.SUPPORTED_PROTOCOLS,
                "diagnostics": diag_ok(),
                "token": self.token,
                "protocol": None,
            }
            if response["ok"]:
                response = self.review_protocol(response, msg_in)
            if response["ok"]:
                response = self.review_message(response, msg_in)
            return response

        # Main handler() logic

        self.server.touch()
        self.server.increment_active()
        try:
            if self.server.state != ServerState.READY:
                self.reply_message(server_not_ready_response(), None)
                return
            # else establish session
            self.timer = time.time()  # in milliseconds
            self.token = _register_session(self.client_address, self.server)
            # monitor idle timeout on socket -- not same as server idle timeout
            self.request.settimeout(svc.SOCKET_IDLE_TIMEOUT)
            # read one line, parse JSON
            line = self._read_one_line()
            msg_in = json.loads(line)
            ess = {"id": msg_in["id"]}
            ev.msg_recv(
                msg_name=msg_in["name"],
                essentials=ess,
                payload=msg_in["payload"],
                session_id=self.token,
            )
            # write response
            self.reply_message(server_welcome_or_reject_response(msg_in), msg_in)
        finally:
            try:
                # close socket for write, but not read
                self.request.shutdown(socket.SHUT_WR)
            except Exception:
                pass
            self.request.close()
            self.server.decrement_active()

    def review_protocol(self, response: Response, msg_in: dict) -> Response:
        """
        Run validation using agreed-on protocols for PR-2.

        :param response: (dict) The current response dictionary.
        :param msg_in: (dict) The incoming message dictionary.
        :return: (dict) Updated response dictionary.
        """
        ok, reason, errs = validator.validate_message_name(msg_in["name"])
        response.update({"ok": ok, "reason": reason, "diagnostics": errs})
        if response["ok"]:
            protocol = msg_in.get("meta", {}).get("protocol", "")
            ok, reason, supported, errs = validator.validate_protocol(protocol)
            response.update(
                {
                    "ok": ok,
                    "reason": reason,
                    "supported": supported,
                    "diagnostics": errs,
                    "protocol": protocol if ok else None,
                }
            )
        return response

    def review_message(self, response: Response, msg_in: dict) -> Response:
        """
        :param: (dict) response
        :param: (dict) msg_in
        Run validation on message content using agreed-on rules for PR-2.
        First validate the envelope, then the payload.
        :return: (dict) response
        """

        # Validate envelope
        env_errs = list(V_ENVELOPE.iter_errors(msg_in))
        if env_errs:
            response = fmt_diagnostics(response, env_errs)
        if response["ok"]:
            # Validate payload based on message name
            pay_errs = list(V_HREQ.iter_errors(msg_in["payload"]))
            if pay_errs:
                response = fmt_diagnostics(response, pay_errs)
        return response

    def system_welcome(self, token: str, msg: dict) -> dict:
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

    def system_reject(self, response: Response, msg: dict) -> dict:
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
            details=diag_join(response.get("diagnostics", diag_ok())),
            supported=response.get("supported") or None,
        )
        msg["payload"] = convert.payload_from_reject(payload)
        return msg

    def reply_message(self, response: Response, msg_in: dict[str, Any] | None) -> None:
        """
        :param: (dict) response
        :param: (dict) msg_in
        Send message back to client based on the response to their request.
        :return: None
        """
        envelope = dto.EnvelopeDTO(
            id=msg_in["id"] if msg_in else "",
            ver=1,
            name="",
            ts=stamps.create_iso_timestamp(),
            meta={"protocol": response.get("protocol") or svc.PROTOCOL_VERSION},
            payload={},
        )
        msg = convert.envelope_from_dto(envelope)
        msg = (
            self.system_welcome(response["token"], msg)
            if response["ok"]
            else self.system_reject(response, msg)
        )
        if msg["id"] != "":
            ev.msg_sent(msg_name=msg["name"], session_id=self.token, payload=msg["payload"])
            reason = ""
            if "reason" in msg["payload"]:
                reason = msg["payload"]["reason"]
                del msg["payload"]["reason"]
            ev.hello(
                outcome="success" if response["ok"] else "fail",
                latency_ms=(time.time() - self.timer),
                reason=reason,
                payload=msg["payload"],
                session_id=self.token,
            )
            msg_ndjson = (json.dumps(msg, separators=(",", ":")) + "\n").encode("utf-8")
            self.request.sendall(msg_ndjson)


def start_server(host: str = HOST, port: int = PORT) -> None:

    server = IdleShutdownServer((host, port), GameRequestHandler)

    # start the idle watchdog
    threading.Thread(target=_idle_watchdog, args=(server,), daemon=True).start()

    try:
        print(f"\n{lookup.get_text(svc.MOTD, fallback='Welcome to the Saskan Lands server!')}")
        ev.ready(host=host, port=port, protocol=svc.PROTOCOL_VERSION)
        server.serve_forever()  # returns after shutdown()
    finally:
        # double-close safe; ensures socket is released
        server.server_close()
        ev.conn_close(addr=f"{host}:{port}")

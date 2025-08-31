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
from importlib.resources import files
from pprint import pprint as pp  # noqa F401
from typing import Any, Dict, List, Optional, Tuple, Type, TypedDict

from jsonschema import Draft202012Validator

from saskan.infra import schema
from saskan.infra.config import services as svc
from saskan.infra.config.net import HOST, PORT
from saskan.infra.log.logger import get_logger
from saskan.infra.schema import validator
from saskan.tools.utils import stamps

# Type aliases

Address = Tuple[str, int]


class Response(TypedDict):
    ok: bool
    reason: Optional[str]
    supported: List[str]
    diagnostics: Dict[str, Any]
    token: str


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
        print(f"Idle elapsed: {elapsed:.1f}s (timeout={self.idle_timeout}s)")
        if elapsed >= self.idle_timeout:
            print(f"Draining and closing connections after {elapsed:.1f}s of inactivity.")
            # best-effort unregister
            for token in list(self.clients.keys()):
                # mirror your unregister semantics
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
        self.client_queue: dict = {}  # Future -- message queue for client
        schema_path = files(schema).joinpath("envelope.schema.json")
        with schema_path.open("r", encoding="utf-8") as f:
            self.envelope_schema = json.load(f)
        schema_path = files(schema).joinpath("handshake.request.schema.json")
        with schema_path.open("r", encoding="utf-8") as f:
            self.handshake_schema = json.load(f)
        self.srv_log = get_logger("saskan.server")
        super().__init__(*args, **kwargs)

    def handle(self) -> None:
        self.server.touch()  # mark activity

        response: Response = {
            "ok": True,
            "reason": None,
            "supported": svc.SUPPORTED_PROTOCOLS,
            "diagnostics": {},
            "token": self.register_client(),
        }
        try:
            while True:
                msg_in = self.request.recv(1024)
                if not msg_in:
                    continue

                self.server.touch()  # mark activity
                msg_str = msg_in.decode("utf-8").rstrip("\n")

                log_msg = json.dumps(
                    {
                        "event": "message_received",
                        "from": str(self.client_address),
                        "msg": msg_str,
                        "ts": stamps.create_iso_timestamp(),
                    }
                )
                self.srv_log.info(log_msg)

                msg_in = json.loads(msg_str)
                if response["ok"]:
                    response = self.review_protocol(response, msg_in)
                if response["ok"]:
                    response = self.review_message(response, msg_in)

                self.reply_message(response, msg_in)
        finally:
            self.unregister_client(response["token"])

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
        # This works but .clients is not really an attribute of TCPServer
        # See mypy issue. Make my own clients stack?
        self.client_queue[token] = {"sock": self.client_address}
        return token

    def unregister_client(self, token: str) -> None:
        """
        Future.
        Remove a client from the game's active list of players.
        """
        # self.server.game.unregister_player(response['id']) -- Future
        if token in self.client_queue:
            print(f"Unregistering client with token {token}")
            del self.client_queue[token]

    def review_protocol(self, response: Response, msg_in: Dict) -> Response:
        """
        Run validation using agreed-on protocols for PR-2.

        :param response: (dict) The current response dictionary.
        :param msg_in: (dict) The incoming message dictionary.
        :return: (dict) Updated response dictionary.
        """
        ok, reason, diagnostics = validator.validate_message_name(msg_in["name"])
        response.update({"ok": ok, "reason": reason, "diagnostics": diagnostics})
        if response["ok"]:
            protocol = msg_in.get("meta", {}).get("protocol", "")
            ok, reason, supported, diagnostics = validator.validate_protocol(protocol)
            response.update(
                {"ok": ok, "reason": reason, "supported": supported, "diagnostics": diagnostics}
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

        def validate_envelope():
            diagnostics = sorted(
                Draft202012Validator(self.envelope_schema).iter_errors(msg_in), key=lambda e: e.path
            )
            if diagnostics:
                response["ok"] = False
                response["reason"] = "invalid_contract"
                response["diagnostics"] = diagnostics
            return response

        def validate_payload():
            diagnostics = sorted(
                Draft202012Validator(self.handshake_schema).iter_errors(msg_in["payload"]),
                key=lambda e: e.path,
            )
            if diagnostics:
                response["ok"] = False
                response["reason"] = "invalid_contract"
                response["diagnostics"] = diagnostics
            return response

        # Main logic
        response = validate_envelope()
        if response["ok"]:
            response = validate_payload()
        return response

    def system_welcome(self, response: Response, msg: Dict) -> Dict:
        msg["name"] = "system.welcome"
        msg["payload"] = (
            {
                "server_version": svc.SERVER_VERSION,
                "session_id": response["token"],
                "motd": svc.MOTD,
                "i18n_id": svc.I18N_WELCOME,
                "accepted_capabilities": ["system.handshake.request"],
            },
        )
        return msg

    def system_reject(self, response: Response, msg: Dict) -> Dict:
        msg["name"] = "system.reject"
        msg["reason"] = response["reason"]
        msg["i18n_id"] = (
            svc.I18N_REJECT_PROTOCOL
            if response["reason"] == "protocol_version_unsupported"
            else (
                svc.I18N_REJECT_NOT_READY
                if response["reason"] == "server_not_ready"
                else svc.I18N_REJECT_GENERIC
            )
        )
        msg["details"] = str(response["diagnostics"])
        return msg

    def reply_message(self, response: Response, msg_in: Dict) -> None:
        """
        :param: (dict) response
        :param: (dict) msg_in
        Send message back to client based on the response to their request.
        Only send message if we have an active request.
        Only single-recipient messages are supported for PR-2.
        :return: None
        """
        msg = {
            "id": msg_in["id"],
            "ver": "1",
            "name": "",
            "ts": stamps.create_iso_timestamp(),
            "meta": {"protocol": "0.1.0"},
        }
        if response["ok"]:
            msg = self.system_welcome(response, msg)
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

    try:
        print(f"\n{svc.MOTD}")
        log_msg = json.dumps(
            {
                "event": "server_started",
                "host": host,
                "port": port,
                "ts": stamps.create_iso_timestamp(),
            }
        )
        srv_log.info(log_msg)
        server.serve_forever()  # returns after shutdown()
        print("\nServer has shut down.")
        log_msg = json.dumps(
            {
                "event": "server_shutdown",
                "host": host,
                "port": port,
                "ts": stamps.create_iso_timestamp(),
            }
        )
        srv_log.info(log_msg)
    finally:
        # double-close safe; ensures socket is released
        server.server_close()

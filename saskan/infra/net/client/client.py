import json
import socket
from pprint import pprint as pp  # noqa E402
from typing import Any, Dict, TypedDict

import saskan.infra.config.services as svc
from saskan.infra.schema.convert import to_reject_dto, to_welcome_dto
from saskan.tools.utils import stamps

# Typing for message structure


class Request(TypedDict):
    id: str
    ver: int
    name: str
    ts: str
    meta: Dict[str, str]
    payload: Dict[str, Any]


def format_request_msg(protocol: str, request_name: str, id: str) -> bytes:
    """
    Send a handshake message to initiate communication with the game server.
    """
    request: Request = {
        "id": id,
        "ver": 1,
        "name": request_name,
        "ts": stamps.create_iso_timestamp(),
        "meta": {"protocol": protocol},
        "payload": {"client_version": "0.1.0"},
    }
    request_ndjson = f"{json.dumps(request)}\n".encode("utf-8")
    return request_ndjson


def send_msg_to_server(
    host: str, port: int, protocol: str, request_name: str, id: str, timeout: float
) -> dict:
    """
    Connect to the server, send a request, and return the server's reply.
    This is called from CLI saskan/ui_cli/client/connect.py.
    Data returned to CLI is a dict with keys. Formatting and localization is done in the CLI.
    :param host: Server hostname or IP address.
    :param port: Server port number.
    :param protocol: Protocol version string.
    :param request_name: Name of the request to send.
    :param id: Player ID.
    :param timeout: Timeout in seconds for socket operations.
    :return: Server's reply as a dict.
    """

    def _read_reply() -> dict:
        """
        Read a single line reply from the server, parse it as JSON, and return it as a dict.
        Raise ConnectionError if no reply is received.
        Raise ValueError if the reply exceeds MAX_MESSAGE_SIZE.
        """
        f = sock.makefile("rb", buffering=0)
        line = f.readline(svc.MAX_MESSAGE_SIZE + 1)
        if not line:
            raise ConnectionError("no reply")
        if len(line) > svc.MAX_MESSAGE_SIZE:
            raise ValueError("oversize reply")
        raw = line.rstrip(b"\r\n").decode("utf-8")
        response_json = json.loads(raw)
        return response_json

    # --- main function body ---
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            # send request
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.sendall(format_request_msg(protocol, request_name, id))
            sock.shutdown(socket.SHUT_WR)
            # receive reply
            sock.settimeout(timeout)
            response_json = _read_reply()
            name = response_json.get("name")  # name of the reply message
            # parse reply based on name
            payload = response_json.get("payload", {})
            if name == "system.welcome":
                reply_dict = to_welcome_dto(payload).__dict__ | {
                    "message_name": name,
                    "reply_code": 0,
                }
            elif name == "system.reject":
                reply_dict = to_reject_dto(payload).__dict__ | {
                    "message_name": name,
                    "reply_code": 2,
                }
            else:
                reply_dict = {
                    "message": "error.unknown_reply",
                    "message_name": name,
                    "reply_code": 1,
                }
        except ConnectionRefusedError:
            reply_dict = {"message": "error.connection_refused", "reply_code": 1}
        except Exception as e:
            reply_dict = {"message": f"An error occurred: {e}", "reply_code": 1}
        return reply_dict

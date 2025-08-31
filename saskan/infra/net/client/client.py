import json
import socket
import time
from pprint import pprint as pp  # noqa E402
from typing import Any, Dict, Optional, TypedDict

from saskan.infra.i18n import lookup
from saskan.infra.schema.convert import to_reject_dto, to_welcome_dto
from saskan.infra.schema.dto import RejectDTO, WelcomeDTO
from saskan.tools.utils import stamps

# @TODO:
# Use DTOs to return structured data rather than a string.


# Typing for message structure


class Request(TypedDict):
    id: str
    ver: str
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
        "ver": "1",
        "name": request_name,
        "ts": stamps.create_iso_timestamp(),
        "meta": {"protocol": protocol},
        "payload": {"client_version": "0.1.0"},
    }
    request_ndjson = f"{json.dumps(request)}\n".encode("utf-8")
    print("[CLIENT] Sending:\n", request_ndjson)
    return request_ndjson


def localize_reply(reply: WelcomeDTO | RejectDTO) -> Optional[str]:
    """
    If the reply has i18n identifier, translate it to the actual message string.
    :param: (DTO object) reply from server
    :return: (Optional[str]) translated message
    """
    msg_string: Optional[str] = None
    if reply.i18n_id is not None:
        msg_string = lookup.get_text(reply.i18n_id, fallback="No message provided")
    return msg_string


def format_welcome_reply(reply: WelcomeDTO, msg_string: Optional[str]) -> str:
    """
    Format the welcome reply message for display.
    :param reply: (WelcomeDTO object) welcome reply from server
    :param msg_string: (str) translated message or None
    :return: (str) formatted welcome message
    """
    welcome: str = (
        f"[CLIENT] Welcome to Saskan server version {reply.server_version}!\n"
        f"Session ID: {reply.session_id}\n"
        f"MOTD: {reply.motd}\n"
    )
    if msg_string:
        welcome += f"Message: {msg_string}\n"
    if reply.accepted_capabilities:
        welcome += f"Accepted capabilities: {', '.join(reply.accepted_capabilities)}\n"
    return welcome


def format_reject_reply(reply: RejectDTO, msg_string: Optional[str]) -> str:
    """
    Format the reject reply message for display.
    :param reply: (RejectDTO object) reject reply from server
    :param msg_string: (str) translated message or None
    :return: (str) formatted reject message
    """
    reject: str = f"[CLIENT] Connection rejected: {reply.reason}\n"
    if msg_string:
        reject += f"Message: {msg_string}\n"
    if reply.details:
        reject += f"Details: {reply.details}\n"
    if reply.supported:
        reject += f"Supported protocols: {', '.join(reply.supported)}\n"
    return reject


# host, port, protocol, request, id, timeout
def send_msg_to_server(
    host: str, port: int, protocol: str, request_name: str, id: str, timeout: float
) -> str:
    """
    Connect to the server, send a request, and return the server's reply.
    This is called from CLI saskan/ui_cli/client/connect.py.
    :param host: Server hostname or IP address.
    :param port: Server port number.
    :param request_name: Name of the request to send.
    :param id: Player ID.
    :return: Server's reply as a string.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            start_time = time.time()
            sock.connect((host, port))
            sock.sendall(format_request_msg(protocol, request_name, id))
            elapsed = time.time() - start_time
            print(f"[CLIENT] Sent request in {elapsed:.2f}s, waiting for reply...")

            response_bytes = sock.recv(1024)
            raw = response_bytes.decode().strip()
            response_json: dict[str, Any] = json.loads(raw)
            name = response_json.get("name")
            payload = response_json.get("payload", {})

            if name == "system.welcome":
                welcome_dto = to_welcome_dto(payload)
                msg_string = localize_reply(welcome_dto)
                reply_msg = format_welcome_reply(welcome_dto, msg_string)
            elif name == "system.reject":
                reject_dto = to_reject_dto(payload)
                msg_string = localize_reply(reject_dto)
                reply_msg = format_reject_reply(reject_dto, msg_string)
            else:
                reply_msg = "[CLIENT] Received unknown reply format."
        except ConnectionRefusedError:
            reply_msg = "[CLIENT] Connection refused by the server."
        except Exception as e:
            reply_msg = f"[CLIENT] An error occurred: {e}"
        return reply_msg

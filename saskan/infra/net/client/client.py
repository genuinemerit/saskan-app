import json
import socket

from saskan.tools.utils import stamps

# @TODO: Implement as a CLI tool with argparse for host/port options.
# Enhance CLI per ADR:
# * [ ] Flags: `--host/--port/--protocol/--timeout`
# Add timeouts on the client side.
#  * [ ] Read one line with 1.0s deadline; return typed DTO or error
# Use DTOs to return structured data.
# Lookup i18n strings for messages.
#  * [ ] I18n lookup and fallback logic (or expose text to CLI)


def format_msg(request, id):
    """
    Send a handshake message to initiate communication with the game server.
    """
    msg = {
        "id": id,
        "ver": "1",
        "name": request,
        "ts": stamps.create_iso_timestamp(),
        "meta": {"protocol": "0.1.0"},
        "payload": {"client_version": "0.1.0"},
    }
    msg = f"{json.dumps(msg)}\n".encode("utf-8")
    print("[CLIENT] Sending:\n", msg)
    return msg


def send_msg_to_server(host, port, request, id):
    status = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            sock.sendall(format_msg(request, id))
            response = sock.recv(1024)
            status = f"[CLIENT] Received:\n{response.decode()}"
        except ConnectionRefusedError:
            status = "[CLIENT] Connection refused by the server."
        except Exception as e:
            status = f"[CLIENT] An error occurred: {e}"
        return status

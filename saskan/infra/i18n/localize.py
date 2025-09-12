# saskan/infra/i18n.localize.py

import json
from functools import lru_cache
from importlib.resources import files

from saskan.infra.i18n import lookup

# from pprint import pprint as pp


@lru_cache(maxsize=4)
def _load_keymap() -> dict:
    """
    Load i18n keymap to memory.
    :return: dict of i18n keymaps
    """
    try:
        path = files("saskan.data.locales").joinpath("i18n_keymap.json")
        with path.open("r") as fh:
            jh = fh.read()
            return json.loads(jh)
    except Exception:
        return {}


KEYMAP = _load_keymap()


def convert_tag(internal_tag: str) -> str:
    """
    Manage converting internal tags and keys into well-formed tags used to lookup i18n values.

    A well-formed i18n tag fits this pattern:

    | Namespace | Purpose                                     | Examples                       |
    |-----------|---------------------------------------------|--------------------------------|
    | `system.*`| Server lifecycle & handshake outcomes       | `system.welcome`, `system.reject` |
    | `msg.*`   | Protocol/session messages                   | `msg.handshake.welcome`        |
    | `ui.*`    | CLI / PySide UI strings                     | `ui.splash.title`, `ui.menu.quit` |
    | `err.*`   | Application errors not tied to handshake    | `err.invalid_input`            |
    | `log.*`   | Log templates (if user-visible)             | `log.server.ready`             |

    Because of standard schema structures or other reasons, sometimes the internal code
    uses a tag that does not fit this pattern.  This module handles converting them
    into a valid i18n tag so that the string value can be localized.
    """
    i18n_tag: str = internal_tag
    i18n_tag = KEYMAP[internal_tag] if internal_tag in list(KEYMAP.keys()) else internal_tag
    return i18n_tag


def format_reply(reply: dict) -> str:
    """
    This function handles reformatting of message replies in dict format into strings
    suitable for display via ui_pyside, ui_cli or ui_pygame modules.

    If item key in the reply is `i18n_id`, translate as a "Message" labeled value.
    If a key or value appears in the i18n keymap table, translate to a valid i18n tag
      before applying localization to it.

    :return: str localized message
    """
    msg_string = ""
    local_reply = {convert_tag(k): convert_tag(v) for k, v in reply.items()}

    for key, value in local_reply.items():
        msg_tag = ""
        msg_label = ""
        msg_text = ""

        if key == "i18n_id" and value is not None:
            msg_label = lookup.get_text("ui.message.label", fallback="Message: ")
            msg_tag = lookup.get_text("ui.client.tag", fallback="[CLIENT] ")

        if key not in ("motd", "i18n_id"):
            msg_label = lookup.get_text(key, fallback=f"{key.capitalize()}: ")

        if isinstance(value, list):
            local_value = [convert_tag(i) for i in value]
            local_value = [lookup.get_text(i, fallback=i) for i in local_value]
            msg_text = "[" + ", ".join(local_value) + "]"
        else:
            msg_text = lookup.get_text(value, fallback="")

        msg_string += f"{msg_tag}{msg_label}{msg_text}\n"

    return msg_string

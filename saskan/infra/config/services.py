"""
:module:   services.py
:author:   PQ

Authoritative constants for protocol and services metadata.
"""

from typing import Final, FrozenSet

# Protocol versions
PROTOCOL_VERSION: Final[str] = "0.1.0"
SERVER_VERSION: Final[str] = "0.1.0"
SUPPORTED_PROTOCOLS: Final[list[str]] = ["0.1.0"]  # ordered by preference

# Allowed message names (PR-2 scope)
ALLOWED_MESSAGE_NAMES: Final[FrozenSet[str]] = frozenset(
    {
        "system.handshake.request",
        "system.welcome",
        "system.reject",
    }
)
ACCEPTED_CAPABILITIES: Final[FrozenSet[str]] = frozenset({"welcome"})

# Rejection reasons
REJECTION_REASONS: Final[FrozenSet[str]] = frozenset(
    {
        "protocol_version_unsupported",
        "server_not_ready",
        "invalid_contract",
    }
)

# server timeouts (in seconds)
SERVER_TIMEOUT: Final[float] = 10.0
IDLE_POLL_INTERVAL: Final[float] = 0.5
DRAIN_GRACE_PERIOD: Final[float] = 5.0
SOCKET_IDLE_TIMEOUT: Final[float] = 1.0

# max message size (in bytes)
MAX_MESSAGE_SIZE: Final[int] = 8192

# motd
MOTD: Final[str] = "Welcome to the Saskan game server!"

# i18n defaults
DEFAULT_LANG: Final[str] = "en-US"
SUPPORTED_LANGS: Final[list[str]] = ["en-US", "es-ES"]

# i18n identifiers used in PR-2
I18N_WELCOME: Final[str] = "msg.handshake.welcome"
I18N_REJECT_GENERIC: Final[str] = "msg.handshake.reject.generic"
I18N_REJECT_PROTOCOL: Final[str] = "msg.handshake.reject.protocol"
I18N_REJECT_NOT_READY: Final[str] = "msg.handshake.reject.not_ready"
I18N_REJECT_INVALID: Final[str] = "msg.handshake.reject.invalid"

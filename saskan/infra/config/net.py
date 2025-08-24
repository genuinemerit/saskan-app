"""
:module:   net.py
:author:   PQ

Configuration defaults for network services.
Environment overrides via SASKAN_* vars.
"""

import os
from typing import Final

# Defaults
DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 8000
DEFAULT_CONNECT_DEADLINE: Final[float] = 2.0
DEFAULT_READ_DEADLINE: Final[float] = 1.0
DEFAULT_WRITE_DEADLINE: Final[float] = 1.0

# Recognized env overrides
ENV_OVERRIDES: Final[set[str]] = {
    "SASKAN_HOST",
    "SASKAN_PORT",
    "SASKAN_PROTOCOL",
    "SASKAN_LANG",
}

# Resolved values (used by CLI/server)
HOST: Final[str] = os.getenv("SASKAN_HOST", DEFAULT_HOST)
PORT: Final[int] = int(os.getenv("SASKAN_PORT", DEFAULT_PORT))
CONNECT_DEADLINE: Final[float] = float(
    os.getenv("SASKAN_CONNECT_DEADLINE", DEFAULT_CONNECT_DEADLINE)
)
READ_DEADLINE: Final[float] = float(os.getenv("SASKAN_READ_DEADLINE", DEFAULT_READ_DEADLINE))
WRITE_DEADLINE: Final[float] = float(os.getenv("SASKAN_WRITE_DEADLINE", DEFAULT_WRITE_DEADLINE))

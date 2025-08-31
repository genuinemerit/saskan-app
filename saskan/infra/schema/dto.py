# saskan/infra/schema/dto.py
"""
:module:   dto.py
:author:   PQ

Dataclasses for Data Transfer Objects.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class HandshakeRequestDTO:
    client_version: str
    capabilities: List[str]  # can be empty


@dataclass(frozen=True)
class WelcomeDTO:
    server_version: str
    session_id: str
    motd: str
    i18n_id: Optional[str] = None
    accepted_capabilities: Optional[List[str]] = None


@dataclass(frozen=True)
class RejectDTO:
    reason: str
    i18n_id: Optional[str] = None
    details: Optional[str] = None
    supported: Optional[List[str]] = None  # for protocol mismatch

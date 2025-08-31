# saskan/infra/schema/dto.py
"""
:module:   dto.py
:author:   PQ

Dataclasses for Data Transfer Objects.
"""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HandshakeRequestDTO:
    id: str
    ver: str
    name: str
    ts: str
    meta: Dict[str, Any]
    payload: Dict[str, Any]


@dataclass
class SystemRejectDTO:
    id: str
    ver: str
    name: str
    ts: str
    meta: Dict[str, Any]
    payload: Dict[str, Any]


@dataclass
class SystemWelcometDTO:
    id: str
    ver: str
    name: str
    ts: str
    meta: Dict[str, Any]
    payload: Dict[str, Any]

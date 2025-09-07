# saskan/infra/schema/convert.py
from dataclasses import asdict
from typing import Any, Dict

from saskan.infra.schema.dto import EnvelopeDTO, HandshakeRequestDTO, RejectDTO, WelcomeDTO

"""
Conversion functions between dict payloads and DTOs.
For internal representations of validated data, see saskan/infra/schema/dto.py
Assume envelope and payload already validated by jsonschema.
"""


def to_envelope_dto(envelope: Dict[str, Any]) -> EnvelopeDTO:
    return EnvelopeDTO(
        id=envelope["id"],
        ver=envelope["ver"],
        name=envelope["name"],
        ts=envelope["ts"],
        meta=envelope.get("meta", {}),
        payload=envelope.get("payload", {}),
    )


def to_handshake_dto(payload: Dict[str, Any]) -> HandshakeRequestDTO:
    return HandshakeRequestDTO(
        client_version=payload["client_version"],
        capabilities=payload.get("capabilities", []),
    )


def to_welcome_dto(payload: Dict[str, Any]) -> WelcomeDTO:
    return WelcomeDTO(
        server_version=payload["server_version"],
        session_id=payload["session_id"],
        motd=payload["motd"],
        i18n_id=payload.get("i18n_id"),
        accepted_capabilities=payload.get("accepted_capabilities"),
    )


def to_reject_dto(payload: Dict[str, Any]) -> RejectDTO:
    return RejectDTO(
        reason=payload["reason"],
        i18n_id=payload.get("i18n_id"),
        details=payload.get("details"),
        supported=payload.get("supported"),
    )


def envelope_from_dto(dto: EnvelopeDTO) -> Dict[str, Any]:
    return asdict(dto)


def payload_from_welcome(dto: WelcomeDTO) -> Dict[str, Any]:
    return asdict(dto)


def payload_from_reject(dto: RejectDTO) -> Dict[str, Any]:
    return asdict(dto)


def payload_from_handshake(dto: HandshakeRequestDTO) -> Dict[str, Any]:
    return asdict(dto)

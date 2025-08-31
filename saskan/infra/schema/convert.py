# saskan/infra/schema/convert.py
from dataclasses import asdict
from typing import Any, Dict

from saskan.infra.schema.dto import HandshakeRequestDTO, RejectDTO, WelcomeDTO


# dict (payload) -> DTO (after schema validation)\
def to_request_dto(payload: Dict[str, Any]) -> HandshakeRequestDTO:
    # Assume envelope/payload already validated by jsonschema
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


# DTO -> dict (payload) for serialization
def payload_from_welcome(dto: WelcomeDTO) -> Dict[str, Any]:
    return asdict(dto)


def payload_from_reject(dto: RejectDTO) -> Dict[str, Any]:
    return asdict(dto)

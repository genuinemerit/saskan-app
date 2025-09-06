"""
:module:   validator.py
:author:   PQ

Validation helpers for protocol negotiation and message allow-list checks.
These do NOT do JSON Schema validation; they implement ADR-0010/0011 glue.
"""

from typing import List, Optional, Tuple

from saskan.infra.config import services as svc
from saskan.infra.schema.types import Diagnostics

# Type aliases for clarity
NegotiationResult = Tuple[bool, Optional[str], List[str], Diagnostics]
AllowlistResult = Tuple[bool, Optional[str], Diagnostics]


def validate_protocol(requested_ver: str) -> NegotiationResult:
    """
    Check if the requested protocol version is supported.

    :param requested_ver: e.g., "0.1.0"
    :return: (ok, accepted_protocol_or_None, supported_versions, diagnostics)
             - ok=True  -> accepted_protocol=requested_ver
             - ok=False -> accepted_protocol=None, supported_versions=svc.SUPPORTED_PROTOCOLS
    """
    diagnostics: Diagnostics = {"errors": []}
    supported = list(svc.SUPPORTED_PROTOCOLS)

    if requested_ver in svc.SUPPORTED_PROTOCOLS:
        return True, requested_ver, supported, diagnostics

    diagnostics["errors"].append(f"protocol_version_unsupported: supported={', '.join(supported)}")
    return False, None, supported, diagnostics


def validate_message_name(msg_name: str) -> AllowlistResult:
    """
    Check that the envelope 'name' is explicitly allowed for PR-2.

    :param msg_name: e.g., "system.handshake.request"
    :return: (ok, mapped_reason_or_None, diagnostics)
             - ok=True  -> name allowed
             - ok=False -> reason = 'invalid_contract'
    """
    diagnostics: Diagnostics = {"errors": []}
    if msg_name in svc.ALLOWED_MESSAGE_NAMES:
        return True, None, diagnostics

    reason = "invalid_contract"
    diagnostics["errors"].append(
        f"{reason}: allowed={', '.join(sorted(svc.ALLOWED_MESSAGE_NAMES))}"
    )
    return False, reason, diagnostics

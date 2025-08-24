# tests/test_validator.py
import pytest

from saskan.infra.config import services as svc
from saskan.infra.schema.validator import (
    validate_message_name,
    validate_protocol,
)


def test_validate_protocol_ok():
    ok, accepted, supported, diag = validate_protocol(svc.PROTOCOL_VERSION)
    assert ok is True
    assert accepted == svc.PROTOCOL_VERSION
    assert supported == svc.SUPPORTED_PROTOCOLS
    assert diag["errors"] == []


@pytest.mark.parametrize("bad_version", ["9.9.9", "0.0.0", ""])
def test_validate_protocol_mismatch(bad_version):
    ok, accepted, supported, diag = validate_protocol(bad_version)
    assert ok is False
    assert accepted is None
    assert supported == svc.SUPPORTED_PROTOCOLS
    # Expect a machine-readable code embedded in the detail string
    assert any("protocol_version_unsupported" in e for e in diag["errors"])


def test_validate_message_name_ok():
    for name in svc.ALLOWED_MESSAGE_NAMES:
        ok, reason, diag = validate_message_name(name)
        assert ok is True
        assert reason is None
        assert diag["errors"] == []


@pytest.mark.parametrize("unknown", ["foo.bar", "system.unknown", "game.start"])
def test_validate_message_name_unknown(unknown):
    ok, reason, diag = validate_message_name(unknown)
    assert ok is False
    # Per ADR-0011 mapping (recommended): unknown name => invalid_contract
    assert reason == "invalid_contract"
    assert diag["errors"] and "allowed=" in diag["errors"][0]

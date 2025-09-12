# saskan/infra/log/events.py
from __future__ import annotations

import os
from typing import Any, Mapping, Optional

from .logger import get_logger

# ---- env controls (see ADR-0017) ---------------------------------------
# SASKAN_LOG_PAYLOAD = none | handshake | all
_PAYLOAD_MODE = os.getenv("SASKAN_LOG_PAYLOAD", "handshake").lower()


def _want_payload(kind: str) -> bool:
    if _PAYLOAD_MODE == "all":
        return True
    if _PAYLOAD_MODE == "none":
        return False
    # default: include payload only for handshake logs
    return kind in {"HELLO"}


log_srv = get_logger("saskan.server")
log_events = get_logger("saskan.events")
log_debug = get_logger("saskan.debug")


# ---- lifecycle / handshake ---------------------------------------------
# N.B. - when the argument list starts with an asterisk,
#  that means all arguments must be by name, not by position


def ready(*, host: str, port: int, protocol: str, corr: str | None = None) -> None:
    log_srv.info(
        "Server ready",
        extra={"evt": "READY", "host": host, "port": port, "protocol": protocol, "corr": corr},
    )


def conn_open(*, addr: str, corr: str | None = None) -> None:
    log_srv.info("Connection opened", extra={"evt": "CONN_OPEN", "addr": addr, "corr": corr})


def hello(
    *,
    outcome: str,
    latency_ms: float,
    reason: str | None = None,
    payload: Optional[Mapping[str, Any]] = None,
    session_id: str | None = None,
    corr: str | None = None,
) -> None:
    extra: dict[str, Any] = {
        "evt": "HELLO",
        "outcome": outcome,
        "latency_ms": latency_ms,
        "corr": corr,
    }
    if reason:
        extra["reason"] = reason
    if session_id:
        extra["session_id"] = session_id
    if payload and _want_payload("HELLO"):
        # keep essentials only
        keep = ("server_version", "session_id", "i18n_id", "accepted_capabilities", "motd")
        extra["payload"] = {k: payload.get(k) for k in keep if k in payload}
    log_srv.info("Handshake result", extra=extra)


def draining_start(*, host: str, port: int, corr: str | None = None) -> None:
    log_srv.info(
        "Server draining", extra={"evt": "DRAINING_START", "host": host, "port": port, "corr": corr}
    )


def conn_close(*, addr: str, corr: str | None = None) -> None:
    log_srv.info("Connection closed", extra={"evt": "CONN_CLOSE", "addr": addr, "corr": corr})


# ---- messaging ----------------------------------------------------------


def msg_recv(
    *,
    msg_name: str,
    essentials: Mapping[str, Any] | None = None,
    payload: Mapping[str, Any] | None = None,
    corr: str | None = None,
    session_id: str | None = None,
) -> None:
    extra: dict[str, Any] = {"evt": "MSG_RECV", "msg_name": msg_name, "corr": corr}
    if session_id:
        extra["session_id"] = session_id
    if essentials:
        extra.update(essentials)
    if payload and _want_payload("MSG_RECV"):
        extra["payload"] = payload
    log_events.info("Message received", extra=extra)


def msg_sent(
    *,
    msg_name: str,
    essentials: Mapping[str, Any] | None = None,
    payload: Mapping[str, Any] | None = None,
    corr: str | None = None,
    session_id: str | None = None,
) -> None:
    extra: dict[str, Any] = {"evt": "MSG_SENT", "msg_name": msg_name, "corr": corr}
    if session_id:
        extra["session_id"] = session_id
    if essentials:
        extra.update(essentials)
    if payload and _want_payload("MSG_SENT"):
        extra["payload"] = payload
    log_events.info("Message sent", extra=extra)


# ---- game loop / commands ----------------------------------------------


def cmd(
    *,
    msg_name: str,
    status: str = "accepted",
    essentials: Mapping[str, Any] | None = None,
    corr: str | None = None,
    session_id: str | None = None,
) -> None:
    extra: dict[str, Any] = {"evt": "CMD", "msg_name": msg_name, "status": status, "corr": corr}
    if session_id:
        extra["session_id"] = session_id
    if essentials:
        extra.update(essentials)
    log_events.info("Command", extra=extra)


def tick(*, turn: int, delta_ms: int, corr: str | None = None) -> None:
    log_events.info(
        "Turn advanced", extra={"evt": "TICK", "turn": turn, "delta_ms": delta_ms, "corr": corr}
    )


def state_snap(*, snap_id: str, size_bytes: int, corr: str | None = None) -> None:
    log_events.info(
        "State snapshot",
        extra={"evt": "STATE_SNAP", "id": snap_id, "size_bytes": size_bytes, "corr": corr},
    )


# ---- assets / AI --------------------------------------------------------


def asset_fetch(*, asset_id: str, variant_id: str, status: str, corr: str | None = None) -> None:
    log_events.info(
        "Asset fetch",
        extra={
            "evt": "ASSET_FETCH",
            "asset_id": asset_id,
            "variant_id": variant_id,
            "status": status,
            "corr": corr,
        },
    )


def ai_gen(*, job_id: str, status: str, millis: int | None = None, corr: str | None = None) -> None:
    extra: dict[str, Any] = {"evt": "AI_GEN", "job_id": job_id, "status": status, "corr": corr}
    if millis is not None:
        extra["elapsed_ms"] = millis
    log_events.info("AI generation", extra=extra)


# ---- io / warnings / errors --------------------------------------------


def io_warn(*, op: str, target: str, reason: str | None = None, corr: str | None = None) -> None:
    log_events.warning(
        "I/O warning",
        extra={"evt": "IO_WARN", "op": op, "target": target, "reason": reason, "corr": corr},
    )


def io_err(*, op: str, target: str, reason: str | None = None, corr: str | None = None) -> None:
    log_events.error(
        "I/O error",
        extra={"evt": "IO_ERR", "op": op, "target": target, "reason": reason, "corr": corr},
    )

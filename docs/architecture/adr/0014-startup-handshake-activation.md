# ADR-0014: Startup, Handshake, and Session Activation

**Date:** 2025-08-20
**Status:** Accepted

## Context

A minimal protocol is needed for server startup, client session initiation, and operational status confirmation. The MVP uses JSON over TCP with a thread-per-connection server.

## Decision

### Server Lifecycle

- **Phases:** `init` → `ready` → `draining` → `stopped`.
- **Readiness:** Achieved after configuration, RNG seeding, world state attachment, and controller registration.
- **Liveness:** Monitored by an internal watchdog; errors transition the server to `draining`.

### Discovery & Configuration

- **Discovery:** Static host:port setup via environment/config file.
- **Configuration:** Clients use `SASKAN_SERVER_HOST/PORT` or CLI flags.

### Handshake Process

- **Client Request:** Includes `client_name`, `client_ver`, `protocol_ver`, `desired_topics`, `resume_token`.
- **Server Reply:** Contains `server_name`, `server_ver`, `protocol_ver_accepted`, `capabilities`, `client_id`, `session_id`, `ready_state`, `heartbeat_interval_sec`.
- **Version Policy:** Incompatible versions result in an error reply and connection closure.

### Health & Control Verbs

- **Ping/Pong:** For liveness checks and time skew.
- **Server Status:** Provides `ready_state`, world id, turn number, and load metrics.
- **Client Goodbye:** Signals intentional disconnect.

### Presence & Heartbeats

- **Heartbeats:** Sent at intervals; inactivity leads to disconnection.
- **Client Registry:** Tracks connections using `client_id`.

### Session Semantics

- **Session Scope:** Connection-scoped for MVP; no persistence across restarts.
- **Resumption & Auth:** Placeholders for future implementation.

### Readiness vs Liveness

- **Readiness:** Server accepts handshakes only when ready.
- **Liveness:** Periodic self-checks; severe faults lead to `draining`.

### Event Delivery at Activation

- **Welcome Snapshot:** Sent post-handshake, includes world id, turn number, player slot, and subscriptions.

## Consequences

- Predictable server bring-up and clear client-server interaction.
- Simple presence model without external dependencies.
- Extensible framework for future features like authentication and session resumption.

## Alternatives Considered

- **HTTP Health Endpoints:** Deferred to avoid adding complexity.
- **Broker-Mediated Presence:** Overkill for MVP.
- **Implicit Activation:** Simpler but risky for version drift.

## Notes / Follow-Ups

- Document failure codes for handshake errors.
- Define default timeouts and operator hooks.
- Consider HTTP endpoints for readiness/liveness in future iterations.

---

## Notification Taxonomy

| Namespace | Kind   | Purpose                       | Audience | Severity |
|-----------|--------|-------------------------------|----------|----------|
| system    | welcome| Successful activation/handshake| user     | info     |
| system    | reject | Handshake rejected + reason   | user     | error    |

### Schema Envelope

```json
{
  "id": "uuid",
  "ver": "1",
  "name": "system.welcome", // or "system.reject"
  "ts": "2025-08-21T12:34:56Z",
  "audience": "user",
  "severity": "info",
  "meta": { "protocol": "0.1.0" },
  "payload": {}
}
```

---

## Internationalization

- **Key Format:** Lowercase, dotted path (e.g., `msg.handshake.welcome`).
- **Language Selection:** Default to en-US, configurable via `SASKAN_LANG`.
- **Acceptance Test:** Ensure localized messages are printed based on language settings.

---

## Acceptance Criteria

1. Server logs `READY` and listens.
2. Successful handshake results in `system.welcome`; motd printed.
3. Protocol mismatches result in `protocol_version_unsupported`.
4. Schema failures result in `invalid_contract`.
5. Draining state results in `server_not_ready`.
6. Logs show connection lifecycle and outcomes.
7. No retries or sessions beyond one exchange.

## Diagram

Refer to `saskan/docs/diagrams/"ADR-0014 Handshake Activation.png"` for the client-server handshake activation flow.
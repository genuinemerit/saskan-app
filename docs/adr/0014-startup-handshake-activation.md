# ADR-0014: Startup, Handshake, and Session Activation

* **Date:** 2025-08-20
* **Status:** Accepted

## Context

We need a clear, minimal protocol for bringing the server online, letting clients start sessions, and mutually confirming operational status. MVP uses JSON over TCP with a thread-per-connection server (ADR‑0009) and message envelope (ADR‑0011). Multiple clients may connect (ADR‑0012). No broker or HTTP yet.

## Decision

### 1) Server lifecycle

* **Phases:** `init` → `ready` → `draining` → `stopped`.
* **Readiness gate:** server enters `ready` only after config loaded, RNG seeded, world state attached (new or loaded), and controllers registered.
* **Liveness:** internal watchdog/timer ensures the turn loop isn’t wedged; errors move server to `draining` (reject new conns, finish in-flight).

### 2) Discovery & configuration

* **Discovery**: static host\:port for MVP (env/config file). No dynamic discovery.
* **Config**: clients read `SASKAN_SERVER_HOST/PORT` (or CLI flags). No service registry.

### 3) Handshake (capability & version sync)

On TCP accept, client sends `handshake.request`, server replies `handshake.reply`. Both use the envelope fields from ADR‑0011.

* **Request (client → server) essential fields in `payload`:**

  * `client_name`, `client_ver`
  * `protocol_ver` (envelope `ver` echoed)
  * `desired_topics` (optional initial subscriptions; ADR‑0008)
  * `resume_token` (optional; future session resumption)

* **Reply (server → client) essential fields in `payload`:**

  * `server_name`, `server_ver`
  * `protocol_ver_accepted`
  * `capabilities` (e.g., `["events","notifications","turn-control"]`)
  * `client_id` (UUID for connection lifetime)
  * `session_id` (logical; may equal `client_id` in MVP)
  * `ready_state` (`ready|draining`)
  * `heartbeat_interval_sec` (see §5)

* **Version policy:** if `protocol_ver` incompatible, server replies `type=error` `code="incompatible_protocol"` and closes.

### 4) Health & control verbs

* `ping` / `pong`: round‑trip liveness and time skew; includes `ts` echo.
* `server.status`: returns `ready_state`, world id, turn number, and basic load metrics.
* `client.hello` (alias of handshake.request for simple CLIs).
* `client.goodbye`: client signals intentional disconnect (cleanup subscriptions).

### 5) Presence & heartbeats

* **Heartbeats:** server sends `type=event name=heartbeat` every `heartbeat_interval_sec` (or clients send `ping` on interval).
* **Timeouts:** if no traffic for `N` seconds (configurable), server marks client **inactive** and closes the socket.
* **Client Registry:** in‑proc structure keyed by `client_id` tracking: socket, last\_seen, subscriptions, groups (ADR‑0012). Presence is derived (connected + fresh last\_seen).

### 6) Session semantics

* **Session scope:** connection‑scoped in MVP. No persistence across restarts.
* **Resumption (placeholder):** reserved `resume_token` in handshake; not implemented in MVP.
* **Auth (placeholder):** reserved `meta.auth` in envelope; not implemented in MVP.

### 7) Readiness vs liveness signaling (operator view)

* **Readiness:** server only accepts handshakes once ready.
* **Liveness:** periodic self‑checks; if severe fault, transition to `draining` and reject new handshakes, emit `system` event to existing clients, then shut down cleanly after a grace period.

### 8) Event delivery at activation

* After successful handshake, server may emit a **welcome snapshot** (`event: client.welcome`) including: world id, turn number, player slot (if assigned), current subscriptions. This avoids clients guessing the initial state.

## Consequences

* Predictable bring‑up: clients know when the server is ready and what it supports.
* Simple presence model without external infrastructure.
* Clear extension points for authentication, session resumption, and richer QoS.
* Fits the minimal transport and notification taxonomy already defined.

## Alternatives considered

* **HTTP health endpoints** (`/ready`, `/live`): standard, but adds an HTTP stack; defer for now.
* **Broker‑mediated presence**: overkill for MVP.
* **Implicit activation** (no handshake): simpler, but brittle for version/capability drift.

## Notes / Follow‑ups

* Document failure codes for handshake (`incompatible_protocol`, `server_draining`, `auth_required`).
* Define default timeouts: handshake deadline (e.g., 5s), idle timeout (e.g., 60s), heartbeat interval (e.g., 15s).
* Add minimal operator hooks: log state transitions; emit `system` notifications when entering `draining`.
* When/if HTTP is introduced, mirror readiness/liveness as endpoints; keep the handshake contract unchanged on the socket side.

---

## Notification Taxonomy for PR-2 (MVP handshake)

Namespace	Kind	Purpose	Audience	Severity
system	welcome	Successful activation/handshake	user	info
system	reject	Handshake rejected + reason	user	error

(Everything else—chat, world, HUD, etc.—comes later.)

### Schema envelope

```json
{
  "id": "uuid",
  "ver": "1",
  "name": "system.welcome",        // or "system.reject"
  "ts": "2025-08-21T12:34:56Z",
  "topic": "system",               // optional; redundant if you keep 'name'
  "audience": "user",
  "severity": "info",
  "meta": { "protocol": "0.1.0" },
  "payload": { /* per message */ }
}
```

Notes:

Keep either name or (topic,kind). Probably just name for simplicity. If we keep topic, ensure `topic == name.split('.')[0]`.

---

## Internationalization for PR2

Key format

Lowercase, dotted path: msg.handshake.welcome, msg.handshake.reject.protocol

Namespace prefixes:

msg. for user‑facing strings

Later you we add err., hud., etc., but keep PR‑2 to msg.*

See: saskan/data/locales for bundles of message.yaml files under en-US and es-ES

### Envelope & payload (no code, just spec)

Keep motd as a plain string and include an optional i18n_id. Client prints the localized string if available; otherwise falls back to motd.

WELCOME payload (PR‑2)

```text
server_version: str
session_id: str
motd: str                # fallback text; may be same as en-US value
i18n_id: "msg.handshake.welcome"   # optional; if present, client looks it up
accepted_capabilities: [str]
```

REJECT payload (PR‑2)

```text
reason: "protocol_version_unsupported|server_not_ready|invalid_contract"
i18n_id: one of:
  - msg.handshake.reject.protocol
  - msg.handshake.reject.not_ready
  - msg.handshake.reject.invalid
details: str (optional, diagnostic; not for end users)
```

### Language selection (config only)

Default language: en-US

Env var: SASKAN_LANG (e.g., es-ES)

CLI flag: not needed for PR‑2 (keep the CLI thin)

Server side doesn’t need to know the client language for PR‑2; the client performs the lookup.

Lookup behavior (client, spec only)

Load messages.yaml for the active locale at process start.

If i18n_id present:

Try active locale → if missing, try en-US → if missing, use motd (or a hardcoded fallback).

If i18n_id absent: just print motd.

## Language: Acceptance test for PR‑2 i18n

Bundles exist at saskan/data/locales/en-US/messages.yaml and es-ES/messages.yaml.

Client prints Spanish when SASKAN_LANG=es-ES:

On success: Bienvenido a las Tierras Saskan

On protocol reject: Conexión rechazada: versión de protocolo no admitida.

Fallback: With SASKAN_LANG=fr-FR (no bundle), client prints English (or motd).

No code changes to server logic required for PR‑2 (only add i18n_id constants in replies).

---

## Redline Review version for PR-2 (MVP for first handshake)

Alright — **ADR-0014 — Startup / Handshake / Activation** is where all the pieces snap together. This is the “story of the first breath” of your system: server comes alive, clients greet it, and you decide if they are welcomed or rejected.

---

## Intent

Define the startup lifecycle of the server and the activation handshake between client and server. Ensure predictable readiness, simple flows for PR-2, and a clear path to expand later.

---

1) Server lifecycle

States:

```text
init → ready → draining → stopped
```

* **init**: configuration loaded, schemas validated, loggers ready, but not accepting sockets.
* **ready**: listening socket open, new connections accepted, handshake processed.
* **draining**: graceful shutdown; accept but immediately `system.reject {reason:"server_not_ready"}` and close.
* **stopped**: sockets closed, no work.

Transition rules:

* `init → ready`: once all configs and services load.
* `ready → draining`: on shutdown signal.
* `draining → stopped`: once active connections drained and socket closed.

---

2) Handshake flow (PR-2)

**Happy path**

1. Client opens TCP connection.
2. Client sends one line JSON (`system.handshake.request`) with `{client_version, capabilities?, meta.protocol}`.
3. Server validates envelope + payload (ADR-0011).
4. Server negotiates protocol (ADR-0010).
5. If OK: reply `system.welcome` with `{server_version, session_id, motd, i18n_id, accepted_capabilities}`.
6. Close connection.
7. Client prints motd (localized if possible) and exits `0`.

**Reject paths**

* Invalid JSON / >8 KB: drop connection (no reply).
* Envelope parseable but bad: reject with `invalid_contract`.
* Unknown `name`: reject with `invalid_contract`.
* Protocol mismatch: reject with `protocol_version_unsupported` + `supported`.
* Server draining/not ready: reject with `server_not_ready`.
* All rejections echo the request `id` if parseable.

---

3) Message kinds (PR-2 allow-list)

* `system.handshake.request` (client → server)
* `system.welcome` (server → client)
* `system.reject` (server → client)

Tie to ADR-0010/-0011. No other kinds permitted in PR-2.

---

4) Envelope & payload summary (cross-ADR)

* Envelope keys: `id, ver, name, ts, meta.protocol, payload` (ADR-0011).
* Request payload: `client_version, capabilities?`.
* Welcome payload: `server_version, session_id, motd, i18n_id?, accepted_capabilities`.
* Reject payload: `reason, i18n_id?, details?, supported?`.

---

5) Readiness guarantees

* Server MUST not accept connections until in `ready`.
* `READY host=<h> port=<p> protocol=0.1.0` log line is the contract for ops.
* CLI connect must fail gracefully if server not ready.

---

6) Observability

* Logs:

  * `READY` (server start).
  * `CONN_OPEN` / `CONN_CLOSE` with addr + id.
  * `HELLO outcome=welcome|reject reason? latency_ms`.
* Metrics (optional in PR-2): attempts, successes, latency histogram.

---

7) i18n hook

* Welcome includes `motd` and optional `i18n_id="msg.handshake.welcome"`.
* Reject includes `reason` and matching `i18n_id` (e.g., `"msg.handshake.reject.protocol"`).
* Client prints localized string if available; fallback to motd/details.

---

8) Out of scope (defer)

* Auth, TLS, heartbeats, resumption, subscriptions, snapshots.
* Multi-message sessions.
* Retention / delivery QoS.
* Complex readiness probes (K8s style).

---

## Acceptance criteria (PR-2, end-to-end)

1. Server logs `READY` and listens.
2. `saskan connect` handshake succeeds with `system.welcome`; exit `0`, motd printed.
3. If protocol mismatch, reject with `protocol_version_unsupported` and `supported`.
4. If schema fail, reject with `invalid_contract`.
5. If draining, reject with `server_not_ready`.
6. Logs show open, outcome, close with latency.
7. No retries or sessions beyond one exchange.

## Diagram

See: saskan/docs/diagrams/"ADR-0014 Handshake Activation.png"

Explanation:

**Figure: Client–Server Handshake Activation Flow**

* **Client states**:

  * *INIT*: CLI started, not yet connected.
  * *CONNECTING*: TCP connect in progress.
  * *SENT\_HELLO*: handshake request sent, waiting for reply.
  * *ACTIVE*: handshake succeeded (`system.welcome`).
  * *FAILED*: handshake rejected (`system.reject`), timed out, or network error.

* **Server states**:

  * *INIT*: process starting, config not yet loaded.
  * *READY*: listening for connections, able to validate handshakes.
  * *VALIDATE*: envelope + payload checked, protocol negotiated.
  * *WELCOME*: valid request → `system.welcome` response.
  * *REJECT*: invalid or unsupported request → `system.reject` response.
  * *CLOSE*: connection always closed after a reply (PR-2 scope).
  * *DRAINING*: graceful shutdown mode; new connections immediately rejected as `server_not_ready`.
  * *STOPPED*: server shut down, no longer accepting.

* **Message arrows**:

  * `handshake.request` (client → server) triggers validation.
  * `system.welcome` or `system.reject` (server → client) determine the client’s end state.

* **Dashed transitions**:

  * *Timeout* (client waiting too long without reply).
  * *Shutdown* (server moving from READY to DRAINING, then STOPPED).

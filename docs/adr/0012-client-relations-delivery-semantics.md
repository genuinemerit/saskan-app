# ADR-0012: Client Relationships & Delivery Semantics

* **Date:** 2025-08-20
* **Status:** Accepted

## Context

Even with a minimal request–reply server (ADR‑0009), we will simulate more than one player and emit system/story events. We need a small set of concepts for: identifying clients, addressing messages (unicast/group/broadcast), opting into event streams, and clarifying basic delivery guarantees—without pulling in brokers or asyncio.

## Decision

### 1) Identity & Sessions (minimal)

* **client\_id**: server-assigned UUID on connect (persists for connection lifetime).
* **session\_id**: optional logical session (future multi-login support).
* Stored in a lightweight **Client Registry** (in‑proc).

### 2) Addressing & Audience

Add an **audience** envelope field (non-breaking with ADR‑0011):

```
"audience": {
  "mode": "unicast | group | broadcast",
  "targets": ["<client_id>|<group_id>"],   // empty for broadcast
  "topic_filter": ["story","world",...],    // optional, aligns with ADR‑0008
}
```

* **unicast**: direct reply/event to one client.
* **group**: logical group id (e.g., “party‑A”, “observers”), server-maintained.
* **broadcast**: all connected clients.

### 3) Subscriptions (opt‑in events)

* Control verbs: `subscribe(topics)`, `unsubscribe(topics)`.
* Server records **topic subscriptions** per client in the registry.
* Events carry `topic` (ADR‑0010/0008). Delivery = `audience` ∩ subscription.
* MVP: **ephemeral** subscriptions (lost on disconnect).

### 4) Delivery Guarantees (MVP)

* **Requests/Replies**: at‑most‑once, synchronous per TCP connection; caller correlates via `id`.
* **Events**: at‑most‑once, best effort. No durability/rewind yet.
* Envelope fields reserved for growth:

  * `"seq"` (monotonic per client/channel), `"ttl"` (seconds), `"priority"` (hint).

### 5) Transaction Semantics (state changes)

* Mutating requests (e.g., “move actor”):

  * Include `"idempotency_key"` in `meta` (client‑generated).
  * Optional optimistic concurrency: `"precondition": {"entity":"actor:123","version":17}`.
* Server **must** return `error` with `code="precondition_failed"` on version mismatch; otherwise a `reply` describing applied changes.

### 6) Polling vs Push

* MVP: **push** over the same TCP connection for replies and events.
* Fallback (later): **long‑poll** style control verb if needed for CLI tooling or tests.
* No external broker; an in‑proc **Event Fan‑Out** routes `(topic,audience)` to sockets.

### 7) Error & Flow Control (basics)

* Backpressure: if a client’s send buffer is congested, **drop non‑critical events** (keep critical per ADR‑0008 `level`).
* Error taxonomy aligns with ADR‑0011 (e.g., `invalid_message`, `unknown_verb`, `unauthorized`, `precondition_failed`, `overloaded`).

## Consequences

* Clear, small vocabulary for multi‑client behavior now: identity, audience, subscription.
* Works with thread‑per‑connection `socketserver`.
* Forward path to durability and QoS without schema churn (reserved fields).
* Simple mental model for simulated multi‑player and NPC observers.

## Alternatives considered

* **Always broadcast everything**: noisy, wastes bandwidth, no privacy.
* **Broker from day one**: adds infra/ops complexity with little MVP value.
* **Client‑side polling only**: simpler, but poor latency and wasteful.

## Notes / Follow‑ups

* Define initial **groups** (e.g., `all_players`, `spectators`) and who manages membership (server‑side controller).
* Document which events are **critical** (must not drop) vs **informational** (may drop under backpressure).
* When durability is needed, add per‑client **cursors** and ring buffers (sequence‑based catch‑up) under a new ADR.
* Security/auth is out of scope for MVP; reserve `meta.auth` field for future use.

---

## Tight redline review for PR-2

## Intent

Define connection/attempt semantics for activation handshake. Keep it predictable and simple for operators and clients.

## Decisions

### 1) Delivery semantics

* **At‑most‑once** for handshake: one request → one reply → close.
* **No automatic retries** in PR‑2 (client exits on failure).
* **No ordering guarantees** beyond the single exchange.

### 2) Correlation & idempotence

* Client generates a unique **`id`** per handshake attempt; server echoes it.
* Server does **not** deduplicate by `id` in PR‑2 (because there are no retries).
* Idempotence keys are out of scope for PR‑2; revisit when we add re‑connect.

### 3) Client state machine

```text
INIT → CONNECTING → SENT_HELLO → ACTIVE (WELCOME) | FAILED (REJECT|timeout|network)
```

* **Deadlines:** connect ≤ 2.0s; handshake reply ≤ 1.0s (see ADR‑0009).
* **On failure:** exit with non‑zero code (see ADR‑0004).

### 4) Failure mapping (client)

| Failure class     | What happened                                  | User message (stderr)                      | Exit |
| ----------------- | ---------------------------------------------- | ------------------------------------------ | ---- |
| Reject/contract   | `system.reject (invalid_contract)`             | `Handshake rejected: invalid request`      | 10   |
| Reject/protocol   | `system.reject (protocol_version_unsupported)` | `Handshake rejected: unsupported protocol` | 10   |
| Reject/not\_ready | `system.reject (server_not_ready)`             | `Handshake rejected: server not ready`     | 10   |
| Timeout           | no reply within deadline                       | `Handshake timed out after <s>`            | 11   |
| Network           | DNS/connect/reset                              | `Unable to connect to <host>:<port>`       | 11   |
| Bad CLI args      | invalid flags                                  | `Invalid value for --…`                    | 12   |

(Aligns with ADR‑0004.)

### 5) Server behavior

* **Ready:** process one request; reply; close.
* **Draining:** reply `server_not_ready`; close.
* **Backpressure:** if write blocks beyond deadline, close (no partials).

### 6) Observability (minimum)

* Log: `HELLO outcome=welcome|reject reason? latency_ms=<n> addr=<ip:port> id=<id>`
* Counters (optional): `handshake_attempts_total`, `handshake_success_total`.

### 7) Out‑of‑scope (PR‑2)

* Retry/backoff strategies, session resumption, heartbeats, presence tracking, multi‑message conversations, QoS tiers.

## Acceptance checks

* Client never retries automatically.
* Each failure maps to the documented exit code and message.
* Logs contain outcome + latency for every attempt.
* No server‑side deduplication or retention.

# ADR-0012: Client Relationships & Delivery Semantics

**Date:** 2025-08-20
**Status:** Accepted

## Context

To support multi-client interactions and event emissions without complex infrastructure, we need a framework for identifying clients, addressing messages, subscribing to events, and defining basic delivery guarantees.

## Decision

### Identity & Sessions

- **client_id**: Server-assigned UUID per connection.
- **session_id**: Optional for future multi-login support.
- Managed via a lightweight in-process **Client Registry**.

### Addressing & Audience

Introduce an **audience** field:

```json
"audience": {
  "mode": "unicast | group | broadcast",
  "targets": ["<client_id>|<group_id>"],
  "topic_filter": ["story","world"]
}
```

- **unicast**: Direct message to one client.
- **group**: Message to a logical group (e.g., "party-A").
- **broadcast**: Message to all clients.

### Subscriptions

- Control verbs: `subscribe(topics)`, `unsubscribe(topics)`.
- Server tracks topic subscriptions per client.
- Events delivered based on `audience` intersecting with subscriptions.
- MVP: Subscriptions are ephemeral (lost on disconnect).

### Delivery Guarantees

- **Requests/Replies**: At-most-once, synchronous per TCP connection.
- **Events**: At-most-once, best effort. No durability yet.
- Reserved fields for future use: `"seq"`, `"ttl"`, `"priority"`.

### Transaction Semantics

- Mutating requests include `"idempotency_key"` in `meta`.
- Optional optimistic concurrency with `"precondition"`.
- On version mismatch, server returns `error` with `code="precondition_failed"`.

### Push vs Polling

- MVP uses **push** for replies and events.
- Potential fallback: **long-poll** style if needed.
- In-process **Event Fan-Out** routes `(topic,audience)` to sockets.

### Error & Flow Control

- Backpressure: Drop non-critical events if send buffer is congested.
- Error taxonomy aligns with ADR‑0011.

## Consequences

- Provides a clear framework for multi-client behavior.
- Compatible with thread-per-connection models.
- Prepares for future enhancements like durability and QoS.

## Alternatives Considered

- **Always broadcast everything**: Inefficient and lacks privacy.
- **Broker from day one**: Adds complexity without immediate benefit.
- **Client-side polling only**: Poor latency and inefficient.

## Notes / Follow-Ups

- Define initial groups and manage membership server-side.
- Document critical vs. informational events.
- Plan for durability with per-client cursors and ring buffers.
- Reserve `meta.auth` for future security/authentication needs.

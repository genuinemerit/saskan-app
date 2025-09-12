# ADR-0013: Message Retention, Expiration, and "Queues"

**Date:** 2025-08-20
**Status:** Accepted

## Context

The MVP transport uses JSON over TCP with a thread-per-connection server. There are no external brokers or durable pub-sub systems. This decision addresses message expiration and queue management.

## Decision

### No Durable Message Queues in MVP

- Events and replies are **ephemeral**, existing only in per-connection output buffers.
- Introduce a **best-effort TTL** field for future compatibility:
  - If expired at send time, the server may drop the message.
  - If absent, treat as non-expiring within the current connection.
- Backpressure policy: Drop non-critical events when a client is slow, retaining critical ones. No background sweeper needed; buffer eviction suffices.

### Separation of Concerns

- **Transport** is ephemeral and drop-eligible.
- **Game history** (e.g., logs, analytics) is managed by the engine and persisted separately, governed by game save policies.

## Consequences

- Simplifies server architecture; no need for janitors/sweepers.
- Clear distinction between transport and game history.
- TTL allows for future QoS enhancements without immediate implementation.

## Alternatives Considered

- **In-proc durable queue with sweeper:** Adds unnecessary complexity for MVP.
- **External broker:** Not needed at current scale; reconsider if durability or replay becomes necessary.

## Notes / Follow-Ups

- Define **buffer limits** per connection and a **drop policy** (e.g., oldest informational first).
- Future event replay/catch-up should be handled via a separate event store with sequence IDs.
- Document TTL semantics in ADR‑0011 and keep it optional until a QoS upgrade is warranted.

---

## Retention Policy for Handshakes

### Key Decisions

1. **Retention Policy**
   - Handshake messages are not retained; processing is in-memory only during the TCP connection's lifetime.

2. **TTLs**
   - Wire TTL is effectively zero; nothing is queued or persisted post-response.

3. **Logs**
   - Logs serve as the authoritative record, capturing essential details like `ts`, `level`, `id`, `addr`, `outcome`, etc.

4. **Privacy & Minimization**
   - Avoid logging payload contents and sensitive details verbatim.

5. **Metrics (Optional)**
   - Track handshake attempts and successes; compute metrics in-process.

6. **Backpressure Buffers**
   - No buffering beyond one line in memory; drop connections exceeding an 8 KB line cap.

7. **Future Considerations**
   - For multi-message sessions, define retention TTLs, durability levels, and backpressure strategies.

## Acceptance Checks

- Ensure no code paths enqueue or persist handshake messages.
- Verify logs contain required keys for each attempt.
- Oversize lines are dropped without reply.
- Log summaries of reject details without full echo to clients.

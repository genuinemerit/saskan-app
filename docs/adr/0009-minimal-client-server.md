# ADR-0009: Minimal Client–Server

Date: 2025-08-20

Status: Accepted

## Context

We need a tiny, reliable request–response path to exercise the turn pipeline and tooling. Older notes considered richer service topologies (pub–sub, brokers). For MVP, we’ll keep transport simple and local, but leave room to evolve.

Lock a simple, reliable transport for PR‑2 (first MVP feature) handshakes:

- TCP sockets, thread‑per‑connection.
- NDJSON framing (one JSON object per line).
- One request → one reply → close

## Decision

Start with a single-process, thread-per-connection TCP server using the Python standard library. Exchange UTF‑8 JSON messages over TCP, newline-delimited (NDJSON) for framing.

1) Transport & concurrency

- Server: Python socketserver.ThreadingTCPServer (or equivalent).
- Per‑conn model: blocking I/O, one thread per connection.
- One‑exchange policy (PR‑2): accept → read one line → respond → close.

2) NDJSON framing (wire format)

- Encoding: UTF‑8.
- Framing: exactly one JSON object per line, terminated by \n.
- Max line length: 8192 bytes (8 KB). If exceeded → drop the connection.
- No embedded newlines in JSON strings (client/server must escape them as \n).
- Accept \r\n to make telnet/netcat friendlier; normalize internally.
- Strict JSON: no comments, no trailing commas.

3) Timeouts & deadlines

- Connect timeout: 2.0 s
- Read deadline (handshake): 1.0 s to receive the request, 1.0 s to receive the reply.
- Write deadline: 1.0 s
- On any deadline breach: close connection; if possible, send system.reject with reason="server_not_ready" or let client map to timeout.

4) Backpressure & load‑shedding

- Accept backlog: use OS default; do not tune in PR‑2.
- Slow reader/writer: if socket write blocks beyond deadline → close.
- Busy server: if not ready, immediately send system.reject with reason="server_not_ready" and close.

5) Envelope + message kinds (tie‑in)

- Only two replies in PR‑2: system.welcome or system.reject.
- Echo request id in the reply.
- Include meta.protocol and (optionally) i18n_id as agreed earlier.

6) Error taxonomy (transport level)

- Malformed JSON / oversize line: close; if parseable enough to know id, reply system.reject with reason="invalid_contract".
- Unknown name/kind: invalid_contract.
- Protocol mismatch: reason="protocol_version_unsupported" with supported:["0.1.0"].
- Distinguish hard cap (oversize before parse → drop, no reply) vs. soft validation (parseable but invalid → invalid_contract). This avoids reflection attacks on giant payloads.

7) Connection lifecycle (server)

- init → ready → draining → stopped
- Only ready accepts and processes handshakes.
- In draining, accept then immediately reject with server_not_ready.
- Always close after reply in PR‑2.

8) Observability

## Logs (server)

- `READY host=<h> port=<p> protocol=0.1.0`
- `CONN_OPEN addr=<ip:port>`
- `HELLO outcome=welcome|reject reason? latency_ms=<n>`
- `CONN_CLOSE addr=<ip:port>`

## Counters (optional now)

- handshake_attempts_total, handshake_success_total

9) Security posture (PR‑2)

- No TLS, no auth (explicit non‑goal).
- Inputs are schema‑validated; reject on violation.
- Hard caps (8 KB line, timeouts) mitigate trivial abuse.

## Hard cap vs. soft validation

This is about how to defend the server against hostile or buggy input.

### Hard cap (structural limits)

Things like max line length (8 KB), max nesting depth, or invalid UTF-8.

If violated, the data is not even safely parseable.

Action: drop connection immediately (no reply).

Reason: You can’t trust the payload enough to even extract an id. Also prevents denial-of-service (someone sending 10 MB lines to eat your RAM).

The term “hard cap” is used a lot in systems: it’s the circuit breaker, the tripped fuse, the guardrail that absolutely cannot be exceeded.

### Soft validation (semantic checks)

Payload is well-formed JSON and under size limits.

But it fails your schema (e.g. "weight": "heavy" instead of a number, or name:"foo.bar" unknown).

Action: you can still parse it, so you know the id.

Reply politely with a system.reject {reason:"invalid_contract"}.

Then close.

### Summary

- Hard cap = unsafe to parse → drop, no reply.
- Soft validation = safe to parse but invalid → reject with clear reason.

## Consequences

- Trivial to implement and debug (human-readable JSON, simple framing).
- Deterministic, testable client–server boundary.
- Leaves room to add streaming/events later (type=event) without breaking envelope.

## Basic Message envelope (all messages)

```json
{
  "id": "<uuid>",            // correlation
  "ver": "1.0",              // message version
  "type": "request|reply|error|event",
  "name": "<verb>",          // e.g., new_game, advance_turn
  "ts": "<ISO8601Z>",
  "payload": {...}           // schema-specific
}
```

## Request–reply contract

Server treats each request as idempotent unless otherwise documented.

Replies echo id. Errors use type=error with code, message, details.

## Initial API surface (minimum)

new_game, load_game, save_game

get_world_summary, inspect_tile|node|region

submit_intents, advance_turn

## Operator probes (manual)

- netcat (client → server):
- Connect: `nc 127.0.0.1 7777`

- Paste a single‑line JSON (with \n at end):

```json
{"id":"…","ver":"1","name":"system.handshake.request","ts":"…","meta":{"protocol":"0.1.0"},"payload":{"client_version":"0.1.0","capabilities":["welcome"]}}
```

-Expect a one‑line JSON reply, then socket closes.

- telnet works similarly; ensure you send exactly one line.

## Alternatives considered

asyncio or ZeroMQ/RabbitMQ: more scale/complexity than needed now.

Length-prefixed binary or Protobuf: efficient, but less debuggable upfront.

## Notes / Follow-ups

Define per-message JSON Schemas (docs only for now).

Set conservative limits: max payload size, server timeouts, concurrent connections.

Add auth field later if/when multi-user appears.

Upgrade path: length-prefixed frames → TLS → structured events channel → external broker.

## Acceptance tests

1) Framing: server rejects lines > 8 KB; accepts valid single‑line JSON; closes after one reply.

2) Timeouts: with no request, server drops after 1.0 s; with delayed reply, client times out after its deadline.

3) Protocol mismatch: request with meta.protocol="99.0" → system.reject (protocol_version_unsupported, with supported).

4) Unknown kind: any name not in {system.handshake.request} → invalid_contract.

5) Lifecycle gate: when server marked draining, every new connection receives server_not_ready.

6) Logging: all events above appear with expected fields.

## Examples

- Request (client → server)

```json
{"id":"2e4c...","ver":"1","name":"system.handshake.request","ts":"2025-08-22T14:05:00Z","meta":{"protocol":"0.1.0"},"payload":{"client_version":"0.1.0","capabilities":["welcome"]}}
```

- Welcome (server → client)

```json
{"id":"2e4c...","ver":"1","name":"system.welcome","ts":"2025-08-22T14:05:00Z","meta":{"protocol":"0.1.0"},"payload":{"server_version":"0.1.0","session_id":"urn:uuid:...","motd":"Welcome to the Saskan Lands","i18n_id":"msg.handshake.welcome","accepted_capabilities":["welcome"]}}
```

-Reject (protocol)

```json
{"id":"2e4c...","ver":"1","name":"system.reject","ts":"2025-08-22T14:05:00Z","meta":{"protocol":"0.1.0"},"payload":{"reason":"protocol_version_unsupported","i18n_id":"msg.handshake.reject.protocol","supported":["0.1.0"]}}
```

# ADR-0009: Minimal Client–Server

**Date:** 2025-08-20
**Status:** Accepted

## Context

For the MVP, establish a simple, reliable request-response path using TCP sockets and NDJSON framing to facilitate the turn pipeline and tooling. This approach is straightforward but allows for future evolution.

## Decision

Implement a single-process, thread-per-connection TCP server using Python's standard library. Exchange UTF-8 JSON messages over TCP, newline-delimited (NDJSON) for framing.

### Transport & Concurrency

- **Server:** Use `socketserver.ThreadingTCPServer`.
- **Model:** Blocking I/O, one thread per connection.
- **Policy:** Accept → read one line → respond → close.

### NDJSON Framing

- **Encoding:** UTF-8.
- **Framing:** One JSON object per line, terminated by `\n`.
- **Max Line Length:** 8192 bytes. Exceeding this results in connection drop.
- **Newlines:** No embedded newlines in JSON strings; escape as `\n`.

### Timeouts & Deadlines

- **Connect Timeout:** 2.0 seconds.
- **Read/Write Deadline:** 1.0 second each.
- **On Breach:** Close connection; optionally send `system.reject`.

### Backpressure & Load-Shedding

- **Backlog:** Use OS default.
- **Slow Reader/Writer:** Close if socket write blocks beyond deadline.
- **Busy Server:** Send `system.reject` with reason "server_not_ready".

### Envelope & Message Kinds

- **Replies:** `system.welcome` or `system.reject`.
- **Echo Request ID:** Include in reply.
- **Include Meta:** Protocol and optional `i18n_id`.

### Error Taxonomy

- **Malformed JSON/Oversize Line:** Close connection; reply with `system.reject` if ID is known.
- **Unknown Name/Kind:** `invalid_contract`.
- **Protocol Mismatch:** Reply with `protocol_version_unsupported`.

### Connection Lifecycle

- **States:** init → ready → draining → stopped.
- **Ready State:** Accepts and processes handshakes.
- **Draining State:** Immediately reject with `server_not_ready`.

### Observability

#### Logs

- `READY host=<h> port=<p> protocol=0.1.0`
- `CONN_OPEN addr=<ip:port>`
- `HELLO outcome=welcome|reject reason? latency_ms=<n>`
- `CONN_CLOSE addr=<ip:port>`

#### Counters

- Optional: `handshake_attempts_total`, `handshake_success_total`.

### Security Posture

- No TLS or auth initially.
- Inputs are schema-validated; reject on violation.
- Hard caps mitigate trivial abuse.

### Hard Cap vs. Soft Validation

- **Hard Cap:** Unsafe to parse → drop, no reply.
- **Soft Validation:** Safe to parse but invalid → reject with clear reason.

## Consequences

- Simple implementation and debugging.
- Deterministic client-server boundary.
- Allows future streaming/events without breaking the envelope.

## Basic Message Envelope

```json
{
  "id": "<uuid>",
  "ver": "1.0",
  "type": "request|reply|error|event",
  "name": "<verb>",
  "ts": "<ISO8601Z>",
  "payload": {...}
}
```

## Initial API Surface

- `new_game`, `load_game`, `save_game`
- `get_world_summary`, `inspect_tile|node|region`
- `submit_intents`, `advance_turn`

## Operator Probes

- **Netcat:** Connect with `nc 127.0.0.1 7777`.
- Paste a single-line JSON ending with `\n`.

## Alternatives Considered

- **Asyncio/ZeroMQ/RabbitMQ:** More complexity than needed.
- **Length-prefixed Binary/Protobuf:** Efficient but less debuggable.

## Notes / Follow-ups

- Define JSON Schemas for messages.
- Set conservative limits on payload size and timeouts.
- Plan upgrade path to include more features like TLS and structured events.

## Acceptance Tests

1. **Framing:** Reject lines > 8 KB; accept valid JSON; close after reply.
2. **Timeouts:** Drop connection after 1.0 s without request.
3. **Protocol Mismatch:** Respond with `system.reject` for unsupported protocols.
4. **Unknown Kind:** Respond with `invalid_contract`.
5. **Lifecycle Gate:** Reject new connections when draining.
6. **Logging:** Ensure all events are logged with expected fields.

## Examples

- **Request (client → server):**

  ```json
  {"id":"2e4c...","ver":"1","name":"system.handshake.request","ts":"2025-08-22T14:05:00Z","meta":{"protocol":"0.1.0"},"payload":{"client_version":"0.1.0","capabilities":["welcome"]}}
  ```

- **Welcome (server → client):**

  ```json
  {"id":"2e4c...","ver":"1","name":"system.welcome","ts":"2025-08-22T14:05:00Z","meta":{"protocol":"0.1.0"},"payload":{"server_version":"0.1.0","session_id":"urn:uuid:...","motd":"Welcome to the Saskan Lands","i18n_id":"msg.handshake.welcome","accepted_capabilities":["welcome"]}}
  ```

- **Reject (protocol):**

  ```json
  {"id":"2e4c...","ver":"1","name":"system.reject","ts":"2025-08-22T14:05:00Z","meta":{"protocol":"0.1.0"},"payload":{"reason":"protocol_version_unsupported","i18n_id":"system.reject.protocol","supported":["0.1.0"]}}
  ```

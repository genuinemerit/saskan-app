# ADR-0013: Message Retention, Expiration, and “Queues”

* **Date:** 2025-08-20
* **Status:** Accepted

## Context

MVP transport is JSON over TCP with a thread‑per‑connection server (ADR‑0009). We have no external broker and no durable pub‑sub. Questions arose about message expiration and sweepers for “queues.”

## Decision

**No durable message queues in MVP.**

* Events and replies are **ephemeral** transport artifacts. They live only in per‑connection output buffers and are not stored for replay.
* Introduce a **best‑effort TTL** (time‑to‑live) envelope field now for forward compatibility:

  * If present and expired at send time, the server may drop the message.
  * If absent, treat as non‑expiring within the current connection only.
* Backpressure policy (per ADR‑0012): when a client is slow, **drop non‑critical events**, keep critical (category/level from ADR‑0008). No background “sweeper” is required; buffer eviction handles cruft.

**Story/recap is not the transport.**

* Player‑facing history (“story so far”, logs, analytics) is produced by the **engine** and persisted via **infra/persistence** (DB/snapshots). That retention is governed by game save policies, not transport queues.

## Consequences

* Simpler server; no janitors/sweepers in MVP.
* Clear separation: **transport** (ephemeral, drop‑eligible) vs **game history** (persisted).
* TTL exists for future QoS without forcing it now.

## Alternatives considered

* **In‑proc durable queue with sweeper:** adds complexity (retention windows, compaction) with little MVP value.
* **External broker:** overkill for current scale; revisit when we add durability or replay.

## Notes / Follow‑ups

* Define concrete **buffer limits** per connection (bytes, count) and a **drop policy** (oldest informational first).
* If/when we add **event replay/catch‑up**, do it as a separate **event store** with sequence IDs and retention settings (new ADR).
* Document TTL semantics in ADR‑0011 (Message Contracts) and keep it optional until a QoS upgrade.

## Tight Redline review for PR-2

## Intent

Specify what is (and is not) retained for handshakes. Keep the wire ephemeral; keep only minimal operational traces.

## Decisions (ready to paste)

### 1) Retention policy

* **Handshake messages are not retained** (no message broker, no durable queue, no store‑and‑forward).
* Processing is **in‑memory only** for the lifetime of the TCP connection.

### 2) TTLs

* **Wire TTL:** effectively **0**; once response is sent/connection closed, nothing is queued or persisted.
* **Log retention:** logs are the sole record (see below). No PII beyond IP\:port and request `id`.

### 3) Logs (authoritative operational record)

* **Format (suggested keys):**
  `ts, level, name, id, addr, outcome, reason?, latency_ms, protocol, server_version`
* **Examples:**

  * `READY host=0.0.0.0 port=7777 protocol=0.1.0`
  * `HELLO outcome=welcome id=2e4c… addr=1.2.3.4:55555 latency_ms=243`
  * `HELLO outcome=reject reason=invalid_contract id=… addr=… latency_ms=120`
* **Sampling:** none for PR‑2 (low volume); all attempts are logged.

### 4) Privacy & minimization

* Do **not** log payload contents.
* Do **not** log `details` field from rejects verbatim; summarize validator keyword/path only.
* Log IP\:port strictly for operations; no user identifiers beyond network address and `id`.

### 5) Metrics (optional)

* Counters: `handshake_attempts_total`, `handshake_success_total`.
* Histograms: `handshake_latency_ms`.
* Storage for metrics is out of scope; acceptable to compute only in‑process for PR‑2 tests.

### 6) Backpressure buffers

* No buffering/queueing between read and write beyond one line in memory.
* If input exceeds **8 KB** line cap → **drop connection** with no reply (ADR‑0009 hard cap).

### 7) Future (non‑binding)

* When multi‑message sessions arrive, define explicit **retention TTLs** for transient topics (e.g., 30s replay), **per‑topic durability levels**, and **backpressure** strategy (drop oldest vs reject writers). Not part of PR‑2.

## Acceptance checks

* No code paths enqueue or persist handshake messages.
* Logs exist for each attempt with the documented keys.
* Oversize lines are dropped without reply (hard cap).
* Reject `details` are summarized in logs; not echoed to clients in full.

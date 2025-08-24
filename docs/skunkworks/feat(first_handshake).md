# Pull request #2 -- a bare bones but full handshake

Here’s a compact table mapping **CLI flows ↔ handshake sequence** (design-level, no code):

```html
| CLI Command (Typer)            | Underlying Flow                                                                                                                             | Notes                                                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `saskan new`                   |
1. `handshake.request` → `handshake.reply`  <br>
2. `game.new_game` request → reply  <br>
3. `client.welcome` event from server               | Handshake is implicit; server assigns `client_id`/`session_id`. Reply includes initial world snapshot (turn=0). |
| `saskan load <save>`           |
1. `handshake.request` → `handshake.reply`  <br>
2. `game.load_game` with save id → reply  <br>
3. `client.welcome` event with restored state | Same as `new`, but world state comes from snapshot.                                                             |
| `saskan tick`                  |
1. (if not already connected) perform handshake as above  <br>
2. `game.advance_turn` → reply  <br>
3. Server emits `turn_summary` event      | Connection/session may persist across ticks.                                                                    |
| `saskan inspect tile <q> <r>`  |
1. (if not connected) perform handshake  <br>
2. `world.inspect_tile` → reply                                                                | No `client.welcome` unless new session started.                                                                 |
| `saskan story test <event-id>` |
1. (if not connected) handshake  <br>
2. `story.test_event` → reply  <br>
3. Possible `story_event` emitted                                   | Debug flow, still uses same activation contract.                                                                |
```

This way, the **handshake** is always the first implicit step when a CLI command establishes a new connection. Persistent sessions may skip repeating it until disconnect.

As we move into the “Welcome to the Saskan Lands” feature, we’ll be implementing the `handshake.reply` → `client.welcome` path for the first time.

---

## Initial design notes (reviewed, verified, see more notes below)

### Structural/consistency checks to verify upon reading

1. 0004 (CLI with Typer) vs repo: CLI module and tests are present; make sure ADR captures current CLI entry and verbs.&#x20;
2. 0005 (Clean layers): Check boundaries across `core/`, `engine/`, `infra/`, and `ui_*` are defined (dependencies point inward, not across UI↔engine directly).&#x20;
3. 0009 (Minimal client–server): Confirm it specifies **TCP / `socketserver`**, not HTTP; ensure no web stack remnants are assumed. (You flagged this discrepancy earlier.)&#x20;
4. 0010 (Services metadata): Expect a source of truth for service names, versions, and capabilities. Verify it’s referenced by handshake (0014) and message contracts (0011).&#x20;
5. 0011 (Message contracts & validations): Look for JSON Schema or equivalent; align with 0003 (JSON predicates) so validations are composable declaratively.&#x20;
6. 0012 (Client relations & delivery semantics): Ensure handshake messages are **at‑most‑once**, idempotent where needed, and define retry/backoff policies.&#x20;
7. 0013 (Message retention): Confirm handshake/session messages are **non‑retained** (or ephemeral TTL), and where logs/metrics record the minimal audit trail.&#x20;
8. 0014 (Startup/handshake/activation): Should bind all the above—version negotiation, capability exchange, and readiness—to a small, testable flow.&#x20;
9. `architecture/client_server_game.md` & `architecture/summary.md`: Verify they frame the above ADRs coherently (layers, protocols, and CLI integration).&#x20;

### Assumptions (to be refined further)

* Transport is **raw TCP** with Python `socketserver`; no HTTP, no WSGI.
* Messages are **JSON**; validations use JSON Schema / predicate DSL (ADR 0003/0011).
* Handshake is **unauthenticated** for PR #2; simple version/capability negotiation only.
* Delivery semantics during handshake: **at‑most‑once**, no durable queues (ADR 0012/0013).

## SCOPE: PR #2 — “Bare‑bones activation handshake”

Out of scope now: auth, encryption, reconnection, persistence, multi‑room routing, gameplay.

### User stories

* **Player (CLI)**: “As a player, I run `saskan connect` and receive a ‘Welcome to the Saskan Lands’ response if the server is ready.” (CLI from ADR 0004; confirms readiness)&#x20;
* **Operator (Server)**: “As an operator, I start the server and see a clear ‘READY on [host\:port](host:port)’ log, with counters for handshakes attempted/succeeded.”
* **Developer (Contract)**: “As a dev, I can validate a handshake request/response against JSON schemas and get precise error messages.”

### Minimal handshake flow (happy path)

1. **Client → Server**: `HELLO` with `{protocol_version, client_version, client_id?, capabilities?}`
2. **Server checks**: protocol compatibility (from services metadata), capacity, readiness.
3. **Server → Client**: `WELCOME` with `{session_id, server_version, motd?, accepted_capabilities}`
4. **Client logs** receipt and transitions to **ACTIVE** state; CLI prints welcome line.

### Error paths

* **Version mismatch** → `REJECT` `{reason:"protocol_version_unsupported", supported:["x.y"]}`
* **Server not ready** → `REJECT` `{reason:"server_not_ready"}`
* **Malformed message** → `REJECT` `{reason:"invalid_contract", details:[…]}`

### Message contracts (draft keys; align w/ 0011)

* `HELLO`: required `protocol_version` (semver string), optional `client_version`, optional `capabilities` (list of strings from 0010).
* `WELCOME`: required `session_id` (URN/UUID), `server_version`; optional `accepted_capabilities`, `motd`.
* `REJECT`: required `reason` (enum); optional `details`.
  (We’ll bind these to JSON Schema in the PR, derived from ADR 0011/0003.)

### State machine (client)

`INIT → CONNECTING (TCP) → SENT_HELLO → ACTIVE (WELCOME) → FAILED (REJECT/timeout)`

* **Timeouts**: TCP connect timeout (e.g., 2s), handshake response timeout (e.g., 1s).
* **Retries**: none for PR #2 (keep delivery semantics simple).

### Delivery semantics & retention (align 0012/0013)

* Handshake messages are **non‑durable**; if dropped, client exits with a clear code.
* No replays; **at‑most‑once**; idempotency not required for `HELLO` in PR #2.
* Logs capture: timestamp, client addr, protocol\_version, outcome, latency bucket.

### Observability

* **Server logs**: “READY”, “HELLO received”, “WELCOME sent/REJECT <reason>”, counts.
* **Metrics (optional counters)**: `handshake_attempts_total`, `handshake_success_total`, `handshake_latency_ms` (bucketed).

### CLI surface (align to ADR 0004)

* `saskan connect --host HOST --port PORT --protocol X.Y`
* Prints one line on success; descriptive error on failure. (No interactive loop in PR #2.)&#x20;

### Config & ports

* Default host/port from env (`SASKAN_HOST`, `SASKAN_PORT`), overridable via CLI.
* Server binds `0.0.0.0:<port>` by default; single‑threaded is fine for PR #2.

### Accetance Tests

* **E2E**: ephemeral server thread; CLI runs `connect`; assert “Welcome…” output within 1s.
* **Contract**: invalid `HELLO` triggers `REJECT/invalid_contract`.
* **Version mismatch**: client protocol “99.0” → `REJECT/protocol_version_unsupported`.
* **Server not ready**: simulate readiness flag false → `REJECT/server_not_ready`.
* **No cross‑layer leaks**: UI CLI imports only client API; client API imports infra/net.

## Open items -- confirm once details are available

* Enumerations (capabilities list from ADR 0010) and exact semver policy.&#x20;
* Predicate/validation mechanism (ADR 0011 vs 0ADR 003)—JSON Schema draft, error shaping. &#x20;
* Delivery semantics wording in ADR 0012 (any mention of retries/backoff we must defer to).&#x20;
* Retention defaults in ADR 0013 (TTL=0 for handshake?).&#x20;
* ADR 0014’s exact activation definition (does “active” require motd, session\_id, both?).&#x20;
* `client_server_game.md` expectations about layering around `infra/net` vs `engine`.&#x20;

### TO DO

reconcile the above plan against ADR's and flag any contradictions, then finalize the PR #2 checklist.

---

## More detailed plan / user stories / use cases and review of ADRs

### ADR highlights

* **Layering matches intent.** `saskan/core`, `engine`, `infra`, `ui_*` are cleanly separated; `ui_cli` exists (Typer), `infra/net` is the right place for the socket server/client. `tests/` has minimal CLI coverage.
* **Docs are strong.** ADRs 0001–0014 are present and readable. Architecture writeups (client\_server\_game.md, summary.md) align with “JSON over TCP, not HTTP” and a local-first engine with a coordinating server.
* **Transport is settled.** ADR‑0009 commits to **TCP, thread‑per‑connection, NDJSON framing**. No web stack remnants. Good.
* **Validation story is consistent.** ADR‑0011 uses **JSON Schema** for message contracts; ADR‑0003 adds a JSON predicate DSL for triggers/action wiring (engine-side).
* **MVP scope is disciplined.** ADR‑0012/0013 keep delivery semantics simple (no broker, no durable queues). ADR‑0014 defines a tight startup/handshake lifecycle.

### Minor nits to fix

* Ensure **single source of truth** for protocol version and capabilities (ADR‑0010) is importable from both server and client (avoid duplication).
* NDJSON framing: document **max line length**, **UTF‑8 only**, and **no embedded newlines** in payload strings (or define escaping).
* Log format: pick keys now (`ts, level, addr, verb, outcome, ms`) to make later metrics trivial.

### ADR summary review

**0003 – JSON predicates + action registry**
Good: data-first triggers, composable predicates, execution at commit boundaries.
Watch: predicate naming/versioning; ensure deterministic evaluation order; unit tests for edge cases (time, RNG, world refs).

**0004 – CLI with Typer**
Good: stable entrypoint and verbs. For handshake, keep CLI thin: `connect` only calls client API. Avoid CLI ↔ engine imports.

**0005 – Clean layers**
Good: boundaries are reflected in the tree. Guardrails to enforce:

* `ui_*` depends only on **client API**, never directly on `engine/core`.
* `engine` depends on `core` and `infra` (as needed), but not on UI.
  A simple `tox -e depguard`/import-lint later will help.

**0008 – Notification taxonomy**
Good: early taxonomy (system, world, chat, etc.) gives you a field on every message. For PR #2 keep it minimal: `system.welcome` only; reserve the rest.

**0009 – Minimal client–server**
Good: **TCP + NDJSON**, thread‑per‑connection, envelope shape.
Clarify now: backpressure policy (block vs drop) and read timeouts for handshake path (e.g., connect 2s, handshake 1s).

**0010 – Services metadata**
Good: namespace + verbs + capability registry. Action item: produce a tiny `services.json` or Python module exposing:

* `protocol_version: "0.1.0"`
* `capabilities: ["welcome"]` (for PR #2)
* `message_kinds`: `HELLO, WELCOME, REJECT`

**0011 – Message contracts & validation**
Good: JSON Schema for **envelope** and **payload**. For handshake, define 3 schemas: `HELLO`, `WELCOME`, `REJECT`. Add a single validator function in `infra`.

**0012 – Client relationships & delivery semantics**
Good: server‑assigned `client_id` (conn‑scoped), optional `session_id` (future). At‑most‑once, no retries for MVP. Keep it that way in PR #2.

**0013 – Message retention**
Good: **no durable queues**. Handshake is ephemeral; only logs persist. Add TTL constants for later (just not used now).

**0014 – Startup, handshake, activation**
Good: lifecycle (`init → ready → draining → stopped`), readiness gating, simple presence map, version negotiation, optional welcome snapshot. For PR #2: implement only **HELLO → WELCOME/REJECT**; snapshot/subscriptions can wait.

**docs/architecture/client\_server\_game.md**
Consistent with ADRs: local deterministic engine; server coordinates; avoid web frameworks. Good to keep.

**docs/architecture/summary.md**
Captures layers, local dev approach, and JSON‑over‑sockets. Matches repo reality.

---

## PR #2: “Bare‑bones activation handshake” — semi‑structured walkthrough

### Goal (thin vertical slice)

Prove server bring‑up + minimal client handshake over TCP using NDJSON. No gameplay, no auth, no persistence. One CLI verb: `connect`.

### Actors / stories

* **Player (CLI):** runs `saskan connect --host --port --protocol X.Y`; sees a one‑line welcome on success; a short reason on failure.
* **Operator (Server):** starts server; sees clear READY log; sees connection/handshake outcomes with counts.
* **Developer (Contracts):** can validate/inspect HELLO/WELCOME/REJECT with JSON Schema; gets deterministic errors for malformed input.

### States & lifecycle

* **Server:** `init` (load config) → `ready` (accept conns) → `draining` (reject new) → `stopped`.
* **Client:** `INIT → CONNECTING → SENT_HELLO → ACTIVE (WELCOME) | FAILED (REJECT/timeout)`.

### Transport & framing

* **TCP, thread‑per‑connection**, blocking I/O.
* **NDJSON**: one JSON object per line; UTF‑8; bounded size (e.g., 8 KB line max).
* **Timeouts:** connect 2s; handshake 1s; read/write 1s. On timeout: close with a `REJECT/server_not_ready` (server) or local error (client).

### Message shapes (envelope + payload)

Common envelope fields (string keys):

* `kind`: `"HELLO" | "WELCOME" | "REJECT"`
* `id`: client‑generated UUID (request id) for HELLO; echoed in response
* `meta`: `{protocol:"0.1.0"}` (server validates; client supplies)

#### HELLO (client → server)

```json
{ kind:"HELLO", id, meta:{protocol}, payload:{
    client_version:"x.y.z",
    capabilities:["welcome"]    // optional, future use
}}
```

#### WELCOME (server → client)

```json
{ kind:"WELCOME", id, meta:{protocol}, payload:{
    server_version:"x.y.z",
    session_id:"urn:uuid:...",  // or simple UUID for now
    motd:"Welcome to the Saskan Lands"
}}
```

#### REJECT (server → client)

```json
{ kind:"REJECT", id, meta:{protocol}, payload:{
    reason:"protocol_version_unsupported|server_not_ready|invalid_contract",
    details: "validation error or hint" // optional
}}
```

### JSON Schema (minimum set for PR #2)

* `envelope.schema.json` for `{kind,id,meta}`.
* `hello.schema.json`, `welcome.schema.json`, `reject.schema.json` for `payload`.
* Validator lives in `infra/schema/validator.py` and is used on both sides.

### Readiness gating (server)

* Start listening socket only after config→ready; otherwise new conns get immediately closed or REJECTed with `server_not_ready`.

### Logging/metrics (MVP)

* Server: `READY host:port`, `CONN open/close addr`, `HELLO ok|reject reason latency_ms`, counters: `handshake_attempts_total`, `handshake_success_total`.
* Client: `connecting…`, `WELCOME session_id`, or `REJECT reason`.

### CLI surface

* `saskan connect --host 127.0.0.1 --port 7777 --protocol 0.1.0`
* Output (success): `Welcome to the Saskan Lands (session <short-id>)`
* Output (reject): `Handshake rejected: <reason>`

### Negative paths to cover

* **Protocol mismatch:** client sends `protocol=99.0`; server replies `REJECT/protocol_version_unsupported` with `supported:["0.1.0"]` (nice‑to‑have).
* **Malformed envelope/payload:** fails schema → `REJECT/invalid_contract`.
* **Server not ready:** REJECT before accepting handshake or closed connection with clear client error.
* **Timeout:** no response in N ms → client exits with `Handshake timed out`.

### Directory placement

* Server: `saskan/infra/net/server.py`
* Client API: `saskan/infra/net/client.py` (used by CLI only)
* Schemas: `saskan/infra/schema/*.json`
* CLI command: `saskan/ui_cli/commands/connect.py` (thin wrapper over client API)
* Config (defaults): `saskan/infra/config/net.py` (host/port/protocol)

### Acceptance test plan

1. **Happy path E2E:** spin server in thread; run client connect; assert welcome line.
2. **Protocol mismatch:** set client protocol to `99.0`; assert REJECT text.
3. **Invalid HELLO:** remove `client_version`; assert REJECT/invalid\_contract.
4. **Server not ready:** simulate readiness flag false; assert REJECT/server\_not\_ready.
5. **Timeout:** delay server reply; client exits with timeout.

### Explicit non‑goals for PR #2

* TLS, auth, resumption, subscriptions, snapshots, multi‑room, chat, gameplay, persistence, external broker.

---

## Design Spec:  Unified “Handshake Spec (PR‑2)”

### Goals

Prove bring‑up/readiness and minimal client activation over TCP.

Keep it one exchange: HELLO → WELCOME | REJECT, then close.

### Transport

TCP, thread‑per‑connection, NDJSON (UTF‑8, one JSON object per line, ≤ 8 KB).

Timeouts: connect 2s, handshake 1s, per read/write 1s.

On any error/timeout: close connection.

### Envelope (same for all messages)

```json
{
  "id": "uuid",               // request id; server echoes
  "ver": "1",                 // envelope version
  "name": "handshake.request|handshake.reply|handshake.reject",
  "ts": "2025-08-21T12:34:56Z",
  "topic": "system",
  "payload": { /* shape per message */ },
  "meta": { "protocol": "0.1.0" }
}
```

### Messages

#### handshake.request (client → server)

Payload:

{
  "client_version": "x.y.z",
  "capabilities": ["welcome"]
}

Required: meta.protocol.

#### handshake.reply (server → client)

Payload:

{
  "server_version": "x.y.z",
  "session_id": "urn:uuid:…",
  "motd": "Welcome to the Saskan Lands",
  "accepted_capabilities": ["welcome"]
}

#### handshake.reject (server → client)

Payload:

{
  "reason": "protocol_version_unsupported|server_not_ready|invalid_contract",
  "details": "human-readable hint (optional)",
  "supported": ["0.1.0"]  // only when reason is protocol_version_unsupported
}

### Validation

Validate envelope first, then payload by name.

validate(name, obj) returns ok | {errors:[{path, keyword, message}]}.

If invalid request → handshake.reject with reason=invalid_contract and a succinct details (do not echo full validator output to clients).

### Readiness & lifecycle

Server listens only in ready; if transitioning to draining, accept then immediately handshake.reject with server_not_ready.

Log lifecycle transitions.

### Logging (server)

On start: READY host:port protocol=0.1.0.

On connection: CONN_OPEN addr=….

On HELLO: HELLO outcome=welcome|reject reason? latency_ms=….

On close: CONN_CLOSE addr=….

Counters (optional now): handshake_attempts_total, handshake_success_total.

Client state machine
INIT → CONNECTING → SENT_HELLO → ACTIVE (on reply) | FAILED (on reject/timeout)

### No retries in PR‑2

CLI contract (Typer)

`saskan connect` --host 127.0.0.1 --port 7777 --protocol 0.1.0

Success: prints Welcome to the Saskan Lands (session \<short-id\>)

Failure: prints Handshake rejected: \<reason\>; exit code ≠ 0.

CLI depends only on client API.

Directory placement (for PR‑2)

Schemas → saskan/infra/schema/{envelope,hello,welcome,reject}.json

Validator → saskan/infra/schema/validator.py

Server → saskan/infra/net/server.py

Client API → saskan/infra/net/client.py

CLI → saskan/ui_cli/commands/connect.py

Services metadata → saskan/infra/config/services.py (or .json)

### Non‑goals (defer)

TLS/auth, heartbeats, reconnection, subscriptions, snapshots, gameplay, persistence.

Minimal edits to docs before code

ADR‑0009: add NDJSON caps (UTF‑8, 8 KB), timeouts, one‑exchange model for PR‑2.

ADR‑0010: define protocol_version="0.1.0", capabilities=["welcome"].

ADR‑0011: add draft version, file locations, and the validator’s error shape.

ADR‑0014: lock handshake.request|reply|reject names and rejection reasons.

Architecture docs: insert one layer diagram; add a telnet/netcat probe snippet.

---

## CLI contract (PR‑2)

### saskan connect

Purpose: Attempt handshake against a server and print a succinct outcome.

Flags

--host, -h (default: from SASKAN_HOST or 127.0.0.1)

--port, -p (default: from SASKAN_PORT or 7777)

--protocol, -r (default: from SASKAN_PROTOCOL or "0.1.0")

--timeout, -t (handshake deadline seconds, default: 1.0)

Success (stdout)

Welcome to the Saskan Lands (session \<short-id\>)

Failure (stderr + exit code)

Reject: Handshake rejected: \<reason\> → exit 10

Timeout: Handshake timed out after 1.0s → exit 11

Network: Unable to connect to 127.0.0.1:7777 → exit 11

Bad flag: Invalid value for --port: 'abc' → exit 12

### saskan version

Purpose: Quick diagnostics; aids bug reports and scripting.

Output (stdout)

saskan-cli=<cli_semver> protocol=<protocol_version> python=<major.minor.patch>

(Keep it one line; machine‑greppable.)

Error taxonomy (CLI side)

User input: invalid flags/env → 12.

Transport: DNS, connect, read/write → 11.

Contract: bad server reply parsing → 11 (network/handshake family).

Application: reject with reason → 10.

Telemetry (CLI)

None in PR‑2 (no phoning home).

Optional local debug (SASKAN_DEBUG=1) prints a single extra line to stderr with timings, e.g.:
DEBUG handshake=243ms.

### Test plan (for ADR‑0004 compliance)

Happy path E2E: server thread up → saskan connect → exit 0, stdout contains “Welcome…”.

Reject: server returns REJECT → exit 10, stderr reason exact.

Timeout: server delays beyond --timeout → exit 11, stderr contains “timed out”.

Bad args: --port abc → exit 12, stderr validation.

Env precedence: set env vars; override with CLI flags; verify effective values in help/behavior.

Layering check: static import‑graph test (CLI doesn’t import engine).

## Documentation snippets to add to ADR‑0004

A “Behavioral Contract” table:

Case	| Stdout	| Stderr	| Exit
Welcome	| `Welcome …`	|  |	0
Reject	|	| `Handshake rejected: <reason>`	| 10
Timeout	|	| `Handshake timed out after <s>`	| 11
Network error	| 	| `Unable to connect to <host>:<port>` |	11
Invalid args	|	| `Invalid value for …`	| 12

The Config Precedence rule and the env var names.

The No cross‑layer imports rule (with example dotted paths allowed).

---

## Example CLI usage blocs (what --help looks like)

### `saskan connect --help`

```text
Usage: saskan connect [OPTIONS]

  Attempt a handshake with the Saskan Lands server.

Options:
  -h, --host TEXT       Server host [default: 127.0.0.1]  [env: SASKAN_HOST]
  -p, --port INTEGER    Server port [default: 7777]      [env: SASKAN_PORT]
  -r, --protocol TEXT   Protocol version [default: 0.1.0] [env: SASKAN_PROTOCOL]
  -t, --timeout FLOAT   Handshake timeout in seconds [default: 1.0]
  --help                Show this message and exit.
```

### `saskan version --help`

```text
Usage: saskan version [OPTIONS]

  Show CLI and protocol versions for diagnostics.

Options:
  --help  Show this message and exit.
```

Example:

```text
saskan-cli=0.1.0 protocol=0.1.0 python=3.12.5
```

## Development checklist for PR-2 feat(first_handshake)

# PR‑2 MVP Checklist — `feat(first_handshake)`

Use this as your PR description. Terse, test‑first, no code pasted in the PR text.

## Scope (frozen)

* One‑shot activation handshake over TCP (NDJSON).
* Messages: `system.handshake.request` → `system.welcome | system.reject`.
* No TLS, auth, retries, or sessions. Close after reply.

---

## 0) Pre‑flight (docs frozen)

* [x] ADR‑0003 updated with Appendices A/B (truth tables + trigger examples).
* [x] ADR‑0004 CLI contract (usage blocks, exit codes).
* [x] ADR‑0005 import rules table committed; `importlinter.ini` + CI step added.
* [x] ADR‑0008 taxonomy for PR‑2 (`system.welcome`, `system.reject`).
* [x] ADR‑0009 transport & limits (NDJSON, 8 KB, timeouts).
* [x] ADR‑0010 services metadata decisions (protocol/caps/ids).
* [x] ADR‑0011 schemas + validator behavior (error mapping).
* [x] ADR‑0014 handshake lifecycle + diagram (caption/legend).

---

## 1) Config & metadata

* [x] Create `saskan/infra/config/services.py` with:

  * [x] `PROTOCOL_VERSION = "0.1.0"`
  * [x] `SERVER_VERSION = "0.1.0"`
  * [x] `SUPPORTED_PROTOCOLS = ["0.1.0"]`
  * [x] `ALLOWED_MESSAGE_NAMES = {"system.handshake.request","system.welcome","system.reject"}`
  * [x] `REJECTION_REASONS = {"protocol_version_unsupported","server_not_ready","invalid_contract"}`
  * [x] i18n IDs: `I18N_WELCOME`, `I18N_REJECT_*`
  * [x] `DEFAULT_LANG = "en-US"`, `SUPPORTED_LANGS = ["en-US","es-ES"]`
* [x] Net defaults in `saskan/infra/config/net.py`:

  * [x] host `0.0.0.0`, port `7777`
  * [x] connect/read/write deadlines (2.0s / 1.0s / 1.0s)
  * [x] env overrides: `SASKAN_HOST`, `SASKAN_PORT`, `SASKAN_PROTOCOL`, `SASKAN_LANG`

---

## 2) Schemas & validator

* [x] Add files under `saskan/infra/schema/`:

  * [x] `envelope.schema.json` (2020‑12; `ver="1"`, `name` regex, `meta.protocol`)
  * [x] `handshake.request.schema.json`
  * [x] `system.welcome.schema.json` (`motd` required, `i18n_id` optional)
  * [x] `system.reject.schema.json` (`reason` enum; `supported` optional)
* [x] Implement `saskan/infra/schema/validator.py`:

  * [x] `validate(name, message) -> {"ok": bool, "errors":[...]}` (JSON Pointer paths)
  * [x] Allow‑list check using `ALLOWED_MESSAGE_NAMES`
  * [x] Protocol negotiation hook via services metadata

---

## 3) i18n bundles (PR‑2 minimum)

* [x] `saskan/data/locales/en-US/messages.yaml`
* [x] `saskan/data/locales/es-ES/messages.yaml`

  * [x] `msg.handshake.welcome`
  * [x] `msg.handshake.reject.{generic,protocol,not_ready,invalid}`
* [x] Client lookup: locale from `SASKAN_LANG`; fallback to `en-US` → `motd`.

---

## 4) Server (infra)

* [ ] `saskan/infra/net/server.py`

  * [ ] `socketserver.ThreadingTCPServer` with one‑exchange policy
  * [ ] NDJSON framing (UTF‑8; accept `\r\n`; **8 KB** cap → drop)
  * [ ] Lifecycle flag: `init → ready → draining → stopped`
  * [ ] Handlers:

    * [ ] Parse line (hard caps first). If unsafe → drop (no reply)
    * [ ] Validate envelope/payload via validator
    * [ ] Protocol negotiation (reject with `supported` on mismatch)
    * [ ] On OK: send `system.welcome` (echo `id`, include `motd`, `i18n_id`)
    * [ ] On fail: send `system.reject` (echo `id` if known)
  * [ ] Logging: `READY`, `CONN_OPEN/CLOSE`, `HELLO outcome=… reason? latency_ms=…`
  * [ ] Draining mode: immediate `server_not_ready` then close

---

## 5) Client API (infra) & CLI (ui\_cli)

* [ ] `saskan/infra/net/client.py`

  * [ ] Connect with 2.0s timeout; send `handshake.request`
  * [ ] Read one line with 1.0s deadline; return typed DTO or error
  * [ ] I18n lookup and fallback logic (or expose text to CLI)
* [ ] `saskan/ui_cli/commands/connect.py`

  * [ ] Flags: `--host/--port/--protocol/--timeout`
  * [ ] Success → stdout: localized welcome; exit `0`
  * [ ] Reject/timeout/net errors → stderr; exit codes `10/11`
* [ ] `saskan/ui_cli/commands/version.py`

  * [ ] Print: `saskan-cli=<ver> protocol=<ver> python=<x.y.z>`

---

## 6) DTOs (no behavior)

* [ ] `saskan/infra/dto/handshake.py`

  * [ ] `HandshakeRequestDTO`, `HandshakeWelcomeDTO`, `HandshakeRejectDTO`

---

## 7) Tests (acceptance first)

**E2E (pytest)**

* [ ] Start server in a thread/fixture; dynamic free port
* [ ] **Happy path**: client connects → welcome within 1s; assert stdout and exit `0`
* [ ] **Protocol mismatch**: reject with `supported`; exit `10`
* [ ] **Invalid request**: malformed payload → reject `invalid_contract`; exit `10`
* [ ] **Server not ready/draining**: reject `server_not_ready`; exit `10`
* [ ] **Timeout**: server sleeps >1s → client exit `11`

**Schema/validator**

* [ ] Envelope required/malformed
* [ ] `additionalProperties` failure
* [ ] Unknown `name` → invalid\_contract
* [ ] Welcome schema enforced (missing `motd` fails in tests)

**i18n**

* [ ] `SASKAN_LANG=es-ES` → Spanish strings
* [ ] Unknown locale → fallback to `en-US` → fallback to `motd`

**Import boundaries**

* [ ] Import‑linter run in CI (already added)

---

## 8) Dev ergonomics

* [ ] Makefile tasks:

  * [ ] `make run-server` (with host/port env)
  * [ ] `make connect` (wrapper around CLI)
  * [ ] `make test` / `make lint`
* [ ] `README` updates:

  * [ ] Quick start (server, connect, netcat probe)
  * [ ] Feature scope & non‑goals for PR‑2

---

## 9) Manual probes (ops appendix)

* [ ] `nc 127.0.0.1 7777` then paste **one line** request JSON; observe one‑line reply
* [ ] Oversize line (>8 KB) is dropped (no reply)
* [ ] Draining mode returns `server_not_ready`

---

## 10) Risk & rollback

* [ ] Guard with feature flag/env if desired (`SASKAN_ENABLE_HANDSHAKE=1`)
* [ ] Rollback plan: stop shipping CLI `connect` in release notes if server not merged

---

## 11) Done‑when (acceptance)

* [ ] All tests green locally and in CI
* [ ] Logs show `READY`, outcomes with latency
* [ ] CLI prints localized welcome in `es-ES` with env set
* [ ] Import‑linter passes; no cross‑layer leaks
* [ ] ADR‑0003/‑0004/‑0005/‑0008/‑0009/‑0010/‑0011/‑0012/‑0013/‑0014 committed and referenced in PR

---

In the format of (`.github/pull_request_template.md`):

# PR-2: MVP Handshake (`feat(first_handshake)`)

## Summary
Implements a one-shot activation handshake over TCP (NDJSON framing).
Scope: `system.handshake.request` → `system.welcome | system.reject`.
No TLS, auth, retries, or sessions. Connection closes after reply.

---

## Checklist

### 0) Pre-flight
- [ ] ADR-0003 updated with Appendices A/B
- [ ] ADR-0004 CLI contract (usage blocks, exit codes)
- [ ] ADR-0005 import rules table + `importlinter.ini` in CI
- [ ] ADR-0008 taxonomy (`system.welcome`, `system.reject`)
- [ ] ADR-0009 transport (NDJSON, 8 KB, timeouts)
- [ ] ADR-0010 services metadata
- [ ] ADR-0011 schemas + validator behavior
- [ ] ADR-0014 lifecycle + state diagram

### 1) Config & Metadata
- [ ] `saskan/infra/config/services.py` with versions, caps, message names, rejection reasons, i18n IDs
- [ ] `saskan/infra/config/net.py` with host/port, deadlines, env overrides

### 2) Schemas & Validator
- [ ] `infra/schema/envelope.schema.json`
- [ ] `infra/schema/handshake.request.schema.json`
- [ ] `infra/schema/system.welcome.schema.json`
- [ ] `infra/schema/system.reject.schema.json`
- [ ] `infra/schema/validator.py` with allow-list + protocol negotiation

### 3) i18n Bundles
- [ ] `data/locales/en-US/messages.yaml`
- [ ] `data/locales/es-ES/messages.yaml`
- [ ] Keys: `msg.handshake.welcome`, `msg.handshake.reject.*`
- [ ] Client lookup by `SASKAN_LANG` with fallback

### 4) Server
- [ ] `infra/net/server.py` (thread-per-conn, NDJSON, 8 KB cap)
- [ ] Lifecycle: `init → ready → draining → stopped`
- [ ] Handlers: parse, validate, negotiate, welcome/reject, close
- [ ] Logging: `READY`, `CONN_OPEN/CLOSE`, `HELLO outcome=…`
- [ ] Draining mode: `server_not_ready`

### 5) Client API & CLI
- [ ] `infra/net/client.py` (connect, send HELLO, read one line)
- [ ] `ui_cli/commands/connect.py` (flags, success stdout, exit codes)
- [ ] `ui_cli/commands/version.py` (prints CLI/protocol/Python versions)

### 6) DTOs
- [ ] `infra/dto/handshake.py` with `Request`, `Welcome`, `Reject` DTOs

### 7) Tests
- [ ] E2E happy path: welcome
- [ ] Protocol mismatch → reject w/ `supported`
- [ ] Invalid request → reject/invalid_contract
- [ ] Draining mode → reject/server_not_ready
- [ ] Timeout → client exit `11`
- [ ] Schema enforcement (required/extra properties)
- [ ] i18n output: `es-ES` vs fallback
- [ ] Import-linter contracts pass

### 8) Dev Ergonomics
- [ ] Makefile tasks: `run-server`, `connect`, `test`, `lint`
- [ ] README quick start (server, connect, netcat probe)
- [ ] Release notes: scope + non-goals

### 9) Manual Probes
- [ ] `nc 127.0.0.1 7777` → paste JSON → reply observed
- [ ] Oversize line dropped silently
- [ ] Draining → `server_not_ready`

### 10) Risk & Rollback
- [ ] Optional feature flag: `SASKAN_ENABLE_HANDSHAKE=1`
- [ ] Rollback plan documented (disable CLI `connect` in release)

### 11) Done-When
- [ ] All tests green locally + CI
- [ ] Logs show READY and handshake outcomes with latency
- [ ] CLI prints localized welcome in `es-ES`
- [ ] ADR-0003 through ADR-0014 merged and referenced

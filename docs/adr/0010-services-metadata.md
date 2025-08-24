# ADR-0010: Services Metadata (Controllers, Brokers, Channels, Topics, Message Structure)

Date: 2025-08-22

Status: Accepted

## Context

We want service architecture that is flexible, controlled, and obvious. Older notes assumed pub–sub with brokers and topics. MVP is request–response, but we should name the concepts and reserve metadata so growth (routing, filtering, replay, UI grouping) is straightforward.

Centralize protocol/version/capability metadata so client, server, schemas, and docs agree without duplication.

## Decision

Define a lightweight services meta-model that applies now and scales later:

### Controllers (now)

In-process request handlers grouped by capability area (e.g., game, world, story, persistence).

Each controller owns a set of name verbs (e.g., game.new_game, world.inspect_tile).

Routing in MVP is a simple name → controller map (no external broker).

### Message structure (reserved fields)

```json
{
  "id": "<uuid>",
  "ver": "1.0",
  "type": "request|reply|error|event",
  "name": "<namespace.verb>",      // e.g., world.inspect_tile
  "ts": "<ISO8601Z>",
  "channel": "control|events",      // logical lane; 'control' only in MVP
  "topic": "story|world|economy|…", // semantic tag for filtering/UX
  "level": "info|warn|critical",    // for 'event'/'error'
  "payload": {...},
  "meta": { "schema": "urn:saskan:msg:...", "trace": "<cid>" }
}
```

### Channels & Topics (future-friendly)

Channel = delivery lane (control for RPC, events for async). MVP uses control only.

Topic = semantic category aligned with ADR‑0008 (notification taxonomy). Settable on replies/events for UI filtering and logs.

### Broker (later)

Introduce an in-proc broker abstraction when events/streaming arrive. It routes by (channel, topic, name); pluggable transports (still optional).

External brokers (ZeroMQ/RabbitMQ) remain out-of-scope until needed.

### Versioning & compatibility

ver in envelope (message format), and meta.schema per payload.

Backward compatibility policy: additive fields are OK; breaking changes require new ver or schema URN.

### Details

1) Storage form & import path

Form: tiny Python module (fast import; no runtime I/O).

Path: saskan.infra.config.services (authoritative).

Rationale: avoids JSON parse at startup, enables type hints and constants, easy reuse in CLI and server.

2) Contents (PR‑2 scope)

PROTOCOL_VERSION: str — wire protocol semver (e.g., "0.1.0").

SERVER_VERSION: str — server/app semver (can equal protocol for PR‑2).

ALLOWED_MESSAGE_NAMES: set[str] — for PR‑2: {"system.handshake.request","system.welcome","system.reject"}.

CAPABILITIES: set[str] — for PR‑2: {"welcome"}.

REJECTION_REASONS: set[str] — {"protocol_version_unsupported","server_not_ready","invalid_contract"}.

SUPPORTED_PROTOCOLS: list[str] — for negotiation (PR‑2: ["0.1.0"]).

DEFAULT_LANG: str — "en-US"; SUPPORTED_LANGS: list[str] — ["en-US","es-ES"] (aligns with ADR‑0008 i18n note).

3) Protocol semantics (SemVer)

MAJOR bump: breaking wire changes (envelope keys, framing rules, message rename).

MINOR bump: additive, backward-compatible (new fields/kinds; clients should ignore unknown fields).

PATCH bump: bugfixes, text changes, no schema impact.

4) Negotiation rule (PR‑2)

Client sends meta.protocol.

Server accepts iff meta.protocol ∈ SUPPORTED_PROTOCOLS; else reject with:

reason="protocol_version_unsupported"

supported=SUPPORTED_PROTOCOLS (ordered by preference, index 0 = preferred).

5) Schema/validator tie‑in

JSON Schemas reference ALLOWED_MESSAGE_NAMES (or a regex + runtime check).

Validator includes a check: name in ALLOWED_MESSAGE_NAMES for PR‑2.

6) i18n tie‑in

Define constants for i18n IDs used by PR‑2:

I18N_WELCOME = "msg.handshake.welcome"

I18N_REJECT_GENERIC = "msg.handshake.reject.generic"

I18N_REJECT_PROTOCOL = "msg.handshake.reject.protocol"

I18N_REJECT_NOT_READY = "msg.handshake.reject.not_ready"

I18N_REJECT_INVALID = "msg.handshake.reject.invalid"

7) Public helper (pure function)

negotiate_protocol(requested: str) -> tuple[bool, str | None, list[str]]

Returns (ok, accepted_protocol, supported_list).

PR‑2 server uses it in handshake path; CLI may import for diagnostics.

## Consequences

Clear naming (namespace.verb) and predictable routing today.

UI/CLI can group by topic without waiting for pub–sub.

Minimal ceremony now; no lock-in that would block future streaming.

## Alternatives considered

Ad-hoc names without namespaces: short-term convenience, long-term ambiguity.

Hard-wired pub–sub from day one: complexity without immediate benefit.

## Notes / Follow-ups

Document controller namespaces (game, world, story, persistence, system).

Reserve channel=events and ensure the server can fan-out to in-proc subscribers later.

Define error taxonomy (code set) and mapping to HTTP-like semantics (400, 404, 409, 500) for consistency, even if not using HTTP.

Establish limits: max event rate, payload size, retention policy (when events land).

Add idempotency_key in meta if any non-idempotent verbs appear (e.g., marketplace orders).

## Example

Example (spec; illustrative, not binding code)

``` python
# saskan/infra/config/services.py

PROTOCOL_VERSION = "0.1.0"
SERVER_VERSION = "0.1.0"

SUPPORTED_PROTOCOLS = ["0.1.0"]  # ordered by preference

ALLOWED_MESSAGE_NAMES = {
    "system.handshake.request",
    "system.welcome",
    "system.reject",
}

CAPABILITIES = {"welcome"}

REJECTION_REASONS = {
    "protocol_version_unsupported",
    "server_not_ready",
    "invalid_contract",
}

DEFAULT_LANG = "en-US"
SUPPORTED_LANGS = ["en-US", "es-ES"]

# i18n identifiers used in PR-2
I18N_WELCOME = "msg.handshake.welcome"
I18N_REJECT_GENERIC = "msg.handshake.reject.generic"
I18N_REJECT_PROTOCOL = "msg.handshake.reject.protocol"
I18N_REJECT_NOT_READY = "msg.handshake.reject.not_ready"
I18N_REJECT_INVALID = "msg.handshake.reject.invalid"


def negotiate_protocol(requested: str) -> tuple[bool, str | None, list[str]]:
    if requested in SUPPORTED_PROTOCOLS:
        return True, requested, SUPPORTED_PROTOCOLS
    return False, None, SUPPORTED_PROTOCOLS
```

## Acceptance tests

Single import path used by server, CLI, and validator.

Protocol negotiation returns reject with supported list on mismatch.

Schemas/validator confirm name ∈ ALLOWED_MESSAGE_NAMES (PR‑2).

i18n bundles include the IDs listed above; client can localize messages using those constants.

No duplicate literals of "0.1.0", message names, or reason enums elsewhere in the code/docs.

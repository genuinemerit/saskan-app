# ADR-0010: Services Metadata

**Date:** 2025-08-22
**Status:** Accepted

## Context

To create a flexible and controlled service architecture, we define a metadata model that supports current needs and future growth. This centralizes protocol/version/capability metadata to ensure consistency across clients, servers, schemas, and documentation.

## Decision

Implement a lightweight services meta-model that is scalable:

### Controllers

Group in-process request handlers by capability (e.g., game, world). Each controller manages specific verbs (e.g., `game.new_game`). Routing is a simple name-to-controller map.

### Message Structure

```json
{
  "id": "<uuid>",
  "ver": "1.0",
  "type": "request|reply|error|event",
  "name": "<namespace.verb>",
  "ts": "<ISO8601Z>",
  "channel": "control",
  "topic": "story|world|economy|…",
  "level": "info|warn|critical",
  "payload": {...},
  "meta": { "schema": "urn:saskan:msg:...", "trace": "<cid>" }
}
```

### Channels & Topics

- **Channel:** Delivery lane (MVP uses 'control').
- **Topic:** Semantic category for filtering/logs.

### Broker (Future)

Introduce an in-process broker for events/streaming. External brokers are out-of-scope until needed.

### Versioning & Compatibility

- **Versioning:** Use `ver` in the envelope and `meta.schema` for payloads.
- **Compatibility:** Additive changes are backward-compatible; breaking changes require new versions.

### Details

1. **Storage Form:** Tiny Python module for fast import and type hints.
2. **Contents:**

   - `PROTOCOL_VERSION`: "0.1.0"
   - `SERVER_VERSION`: "0.1.0"
   - `ALLOWED_MESSAGE_NAMES`: {"system.handshake.request", "system.welcome", "system.reject"}
   - `CAPABILITIES`: {"welcome"}
   - `REJECTION_REASONS`: {"protocol_version_unsupported", "server_not_ready", "invalid_contract"}
   - `SUPPORTED_PROTOCOLS`: ["0.1.0"]
   - `DEFAULT_LANG`: "en-US"
   - `SUPPORTED_LANGS`: ["en-US", "es-ES"]

3. **Protocol Semantics:**

   - **MAJOR:** Breaking changes.
   - **MINOR:** Additive, backward-compatible.
   - **PATCH:** Bugfixes, no schema impact.

4. **Negotiation Rule:** Server accepts if `meta.protocol` is in `SUPPORTED_PROTOCOLS`.

5. **Schema/Validator:** Ensure message names are allowed.

6. **i18n Tie-in:** Define constants for i18n IDs.

7. **Public Helper:**

   ```python
   def negotiate_protocol(requested: str) -> tuple[bool, str | None, list[str]]:
       if requested in SUPPORTED_PROTOCOLS:
           return True, requested, SUPPORTED_PROTOCOLS
       return False, None, SUPPORTED_PROTOCOLS
   ```

## Consequences

- Clear naming and predictable routing.
- UI/CLI grouping by topic without pub-sub.
- No lock-in blocking future streaming.

## Alternatives Considered

- Ad-hoc names: Short-term convenience, long-term ambiguity.
- Hard-wired pub-sub: Complexity without immediate benefit.

## Notes / Follow-ups

- Document controller namespaces.
- Reserve `channel=events` for future use.
- Define error taxonomy and mapping to HTTP-like semantics.
- Establish limits on event rate, payload size, and retention policy.
- Add `idempotency_key` if non-idempotent verbs appear.

## Example

Example configuration file:

```python
# saskan/infra/config/services.py

PROTOCOL_VERSION = "0.1.0"
SERVER_VERSION = "0.1.0"

SUPPORTED_PROTOCOLS = ["0.1.0"]

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

I18N_WELCOME = "msg.handshake.welcome"
I18N_REJECT_GENERIC = "system.reject.generic"
I18N_REJECT_PROTOCOL = "system.reject.protocol"
I18N_REJECT_NOT_READY = "system.reject.not_ready"
I18N_REJECT_INVALID = "system.reject.invalid"


def negotiate_protocol(requested: str) -> tuple[bool, str | None, list[str]]:
    if requested in SUPPORTED_PROTOCOLS:
        return True, requested, SUPPORTED_PROTOCOLS
    return False, None, SUPPORTED_PROTOCOLS
```

## Acceptance Tests

- Single import path used by server, CLI, and validator.
- Protocol negotiation returns supported list on mismatch.
- Schemas confirm name in `ALLOWED_MESSAGE_NAMES`.
- i18n bundles include defined IDs for localization.
- No duplicate literals of "0.1.0" or message names elsewhere.

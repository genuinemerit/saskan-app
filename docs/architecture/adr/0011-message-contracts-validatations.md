# ADR-0011: Message Contracts & Validation

**Date:** 2025-08-20
**Status:** Accepted

## Context

To ensure a flexible, controlled protocol using JSON over TCP, we need explicit, versioned message contracts. This involves defining field names, types, enums, defaults, and compatibility rules.

## Decision

Utilize **JSON Schema** for defining and validating message envelopes and payloads:

- **Single Envelope Schema:** Stable schema for fields like `id`, `ver`, `type`, `name`, `ts`, `channel`, `topic`, `level`, `payload`, `meta`.
- **Per-Message Payload Schemas:** Modular schemas per message `name`.
- **Enum Constraints:** Captured in schema; changes are additive or require a new version.
- **Defaults & Generation Policy:**
  - `id` (UUID) and `ts` (ISO‑8601Z) set by sender.
  - `ver` required; increments on breaking changes.
  - Server-side defaults documented in schema.

### Validation Enforcement

- Validate at ingress and egress.
- On failure, return `type="error"` with structured `code`, `message`, `details`.

### Location of Truth

- Authoritative schemas in `saskan/infra/schema/`.
- Mirror copies in `docs/` for human-readable documentation.
- Use URNs for `$id` to reference schemas.

### Compatibility Policy

- Additive fields are backward compatible if optional.
- Enum expansion is compatible; removal/rename is breaking.
- Breaking changes bump `ver` or schema `$id`.

## Detailed Version

### Files & Locations

- Schemas: `saskan/infra/schema/`
  - `envelope.schema.json`
  - `handshake.request.schema.json`
  - `system.welcome.schema.json`
  - `system.reject.schema.json`
- Validator: `saskan/infra/schema/validator.py`

### JSON Schema Draft & Policy

- Use JSON Schema 2020‑12.
- Additive changes only (MINOR); breaking changes require MAJOR bump.

### Envelope Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "envelope.schema.json",
  "type": "object",
  "required": ["id", "ver", "name", "ts", "meta", "payload"],
  "properties": {
    "id": { "type": "string", "minLength": 1 },
    "ver": { "type": "string", "const": "1" },
    "name": { "type": "string", "pattern": "^[a-z0-9]+(\\.[a-z0-9_-]+)+$" },
    "ts": { "type": "string", "format": "date-time" },
    "audience": { "type": "string", "enum": ["user","operator","dev","all"] },
    "severity": { "type": "string", "enum": ["info","warning","error"] },
    "meta": {
      "type": "object",
      "required": ["protocol"],
      "properties": { "protocol": { "type": "string", "minLength": 1 } },
      "additionalProperties": false
    },
    "payload": {}
  },
  "additionalProperties": false
}
```

### Handshake Payload Schemas

**Request — system.handshake.request**

```json
{
  "$id": "handshake.request.schema.json",
  "type": "object",
  "required": ["client_version"],
  "properties": {
    "client_version": { "type": "string", "minLength": 1 },
    "capabilities": { "type": "array", "items": { "type": "string" }, "default": [] }
  },
  "additionalProperties": false
}
```

**Welcome — system.welcome**

```json
{
  "$id": "system.welcome.schema.json",
  "type": "object",
  "required": ["server_version", "session_id", "motd", "accepted_capabilities"],
  "properties": {
    "server_version": { "type": "string", "minLength": 1 },
    "session_id": { "type": "string", "minLength": 1 },
    "motd": { "type": "string", "minLength": 1 },
    "i18n_id": { "type": "string" },
    "accepted_capabilities": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": false
}
```

**Reject — system.reject**

```json
{
  "$id": "system.reject.schema.json",
  "type": "object",
  "required": ["reason"],
  "properties": {
    "reason": { "type": "string", "enum": [
      "protocol_version_unsupported", "server_not_ready", "invalid_contract"
    ]},
    "i18n_id": { "type": "string" },
    "details": { "type": "string" },
    "supported": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": false
}
```

### Validator Behavior

- Validate envelope first; route by name to payload schema.
- Return structured errors on failure.

### Name Routing & Allow-list

- Check name against `ALLOWED_MESSAGE_NAMES`.
- For PR‑2: allow only specific messages.

### Protocol Negotiation Hook

- After envelope validation, check `meta.protocol`.
- If unsupported, reject without further payload validation.

### Size & Safety Gates

- Enforce hard caps before validation (UTF‑8, ≤8 KB, valid JSON).

## Consequences

- Clear constraints and deterministic behavior.
- Early error detection simplifies debugging and testing.
- Enables future tooling without committing to heavier frameworks.

## Alternatives Considered

- Ad-hoc JSON + docstrings: Faster initially but less reliable.
- OpenAPI/Protobuf: More powerful but unnecessary for MVP.

## Notes / Follow-Ups

- Define an error taxonomy and map to human-readable messages.
- Add CI checks for sample message validation.
- Consider OpenAPI or Protobuf for future HTTP/binary transport needs.
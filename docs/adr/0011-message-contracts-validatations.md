# ADR-0011: Message Contracts & Validation

* **Date:** 2025-08-20
* **Status:** Accepted

## Context

We’re standardizing on JSON over TCP for MVP (ADR‑0009/0010). To keep the protocol *flexible, controlled, and obvious*, messages need explicit, versioned contracts: field names, types, enums, defaults, and compatibility rules.

Single source of truth for wire contracts. Validate envelope → payload deterministically, return precise errors, and keep schemas versioned and small.

## Decision

Use **JSON Schema** to define and validate both the **envelope** and **payloads**.

* **Single envelope schema** (stable): fields like `id`, `ver`, `type`, `name`, `ts`, `channel`, `topic`, `level`, `payload`, `meta`.
* **Per‑message payload schemas** (modular): one schema per `name` (e.g., `world.inspect_tile.request`, `world.inspect_tile.reply`).
* **Enum constraints** (e.g., `topic`, `type`, `level`) captured in schema; changes are additive or via new version.
* **Defaults & generation policy**

  * `id` (UUID) and `ts` (ISO‑8601Z) are **set by the sender**; for client→server requests, the **client** sets them. The server **must set** them for replies/events if missing, but missing values should be treated as protocol errors during development.
  * `ver` is required; increments on breaking envelope changes.
  * Any server‑side defaults (e.g., `level="info"`) are documented in schema via `default` and mirrored in docs.

* **Validation enforcement**

  * Validate **at ingress and egress** (server and client façades).
  * On validation failure: return `type="error"` with structured `code`, `message`, `details`.

* **Location of truth**

  * Authoritative schemas live in repo under `saskan/infra/schema/` (runtime consumption).
  * Mirror copies (or symlinks) in `docs/` for human‑readable docs.
  * Use URNs (e.g., `urn:saskan:msg:envelope:1`) for `$id` so messages can reference their schema.

* **Compatibility policy**

  * Additive fields are backward compatible if optional.
  * Enum expansion is compatible; removal or rename is breaking.
  * Breaking changes bump `ver` (envelope) or the schema `$id` (payload); support a grace period where both are accepted.

### Detailed version

1. Files & locations

Schemas in saskan/infra/schema/:

envelope.schema.json

handshake.request.schema.json

system.welcome.schema.json

system.reject.schema.json

Validator module: saskan/infra/schema/validator.py

1. JSON Schema draft & policy

Use JSON Schema 2020‑12.

Additive changes only (MINOR): new optional fields / enum values.

Breaking changes require protocol MAJOR bump (tie to ADR‑0010).

1. Envelope (common to all)

Minimal, explicit, tight. Required unless marked optional.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "envelope.schema.json",
  "type": "object",
  "required": ["id", "ver", "name", "ts", "meta", "payload"],
  "properties": {
    "id":   { "type": "string", "minLength": 1 },           // request correlation
    "ver":  { "type": "string", "const": "1" },             // envelope version
    "name": { "type": "string", "pattern": "^[a-z0-9]+(\\.[a-z0-9_-]+)+$" },
    "ts":   { "type": "string", "format": "date-time" },
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

Notes:

name grammar enforces `<namespace>.<kind>`.

audience/severity optional (ADR‑0008).

payload validated by per‑message schema after envelope passes.

1. Handshake payload schemas (PR‑2)

Request — system.handshake.request

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

Welcome — system.welcome

```json
{
  "$id": "system.welcome.schema.json",
  "type": "object",
  "required": ["server_version", "session_id", "motd", "accepted_capabilities"],
  "properties": {
    "server_version": { "type": "string", "minLength": 1 },
    "session_id":     { "type": "string", "minLength": 1 },
    "motd":           { "type": "string", "minLength": 1 },   // fallback text
    "i18n_id":        { "type": "string" },                   // optional
    "accepted_capabilities": {
      "type": "array", "items": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

Reject — system.reject

```json
{
  "$id": "system.reject.schema.json",
  "type": "object",
  "required": ["reason"],
  "properties": {
    "reason":    { "type": "string", "enum": [
      "protocol_version_unsupported", "server_not_ready", "invalid_contract"
    ]},
    "i18n_id":   { "type": "string" },
    "details":   { "type": "string" },
    "supported": { "type": "array", "items": { "type": "string" } }  // only for protocol mismatch
  },
  "additionalProperties": false
}
```

1. Validator behavior (spec)

Step 1: Validate envelope; if it fails → return invalid_envelope error list.

Step 2: Route by name to a payload schema; if unknown name → invalid_contract (unknown kind).

Step 3: Validate payload; return structured errors.

No partial mutation: validator is pure; it never alters data.

Strictness: additionalProperties: false everywhere for PR‑2.

Error shape (returned by validator)

```json
{
  "ok": false,
  "errors": [
    {
      "scope": "envelope|payload",
      "name": "system.handshake.request",    // if known, else null
      "path": "$.payload.client_version",    // JSON Pointer
      "keyword": "type|enum|required|pattern|additionalProperties",
      "message": "client_version: expected string"
    }
  ]
}
```

Server maps this to:

system.reject with reason="invalid_contract" and a single concise details (do not echo the full errors array to clients). Full list goes to logs.

1. Name routing & allow‑list

Validator must check name is in ALLOWED_MESSAGE_NAMES (from ADR‑0010).

For PR‑2: allow only
{"system.handshake.request","system.welcome","system.reject"}.

1. Protocol negotiation hook

After envelope OK, check meta.protocol via services metadata.

If not supported → system.reject (protocol_version_unsupported, include supported list).

Skip payload validation in that case (you already know it’s a mismatch).

1, Size & safety gates (tie to ADR‑0009)

Validator is called only after hard caps (UTF‑8, ≤ 8 KB line, JSON parse) are satisfied.

If JSON can’t be parsed safely (no id certainty) → drop connection (no reply).

1, Test matrix (acceptance)

Happy path: request valid → welcome valid.

Unknown name: name:"foo.bar" → invalid_contract.

Missing required in request → invalid_contract (payload error path points to missing key).

Protocol mismatch → reject with supported.

Additional property present → invalid_contract (additionalProperties).

Welcome schema enforced in server replies (property omission test).

i18n_id optional in welcome/reject; absence does not fail.

Large but under cap → schema still enforced; malformed → dropped by hard cap.

## Consequences

* Clear constraints (types/enums) and deterministic behavior (defaults, id/timestamp policy).
* Early error detection at the boundary; easier debugging and automated tests.
* Enables future tooling (codegen/docs) without committing to RPC/HTTP frameworks.

## Alternatives considered

* **Ad‑hoc JSON + docstrings**: faster initially; brittle and ambiguous.
* **OpenAPI/Protobuf now**: powerful, but heavier than needed for the socket MVP; can adopt later at the same boundary.

## Notes / Follow‑ups

* Define an **error taxonomy** (codes like `invalid_message`, `unknown_verb`, `conflict`, `internal`) and map to human‑readable messages.
* Add a CI check that validates a corpus of sample messages against schemas.
* When/if HTTP is introduced, consider **OpenAPI** as an additional contract surface; when/if binary transport is needed, consider **Protobuf** while keeping the same logical fields.

---

### Where do enum constraints like `topic` live?

In the **envelope schema** under an `enum`. The **source of truth** is the file under `saskan/infra/schema/`. The **policy for adding topics** should reference ADR‑0008 (Notification Taxonomy).

### Do we need this ADR now?

Yes. It nails down *how* we express and enforce message structure without committing to heavier infrastructure. It also prevents drift between client, server, and docs as you start the minimal request–response PR.

## Prototype envelope schema draft

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

## Additional contracts

Add i18n_id as an optional string in welcome and reject payload schemas.

Keep motd required in welcome for PR‑2 to guarantee a fallback.

## Tight version

Here’s the **final pass on ADR‑0011 (Message Contracts & Validation)**—tight, actionable, and ready to freeze.

## ADR‑0011 — Finalized

### Schema index (files, PR‑2)

* `saskan/infra/schema/envelope.schema.json`
* `saskan/infra/schema/handshake.request.schema.json` (for `system.handshake.request`)
* `saskan/infra/schema/system.welcome.schema.json`
* `saskan/infra/schema/system.reject.schema.json`

### Policy

* Draft: **JSON Schema 2020‑12**.
* Additive changes only in MINOR; breaking changes require protocol **MAJOR** bump (ties to ADR‑0010).
* `additionalProperties: false` everywhere for PR‑2.

### Envelope (required keys)

`id, ver="1", name(<namespace>.<kind>), ts(ISO‑8601), meta{protocol}, payload`

* Optional: `audience("user|operator|dev|all")`, `severity("info|warning|error")`.
* Name allow‑list (ADR‑0010/PR‑2):
  `{ "system.handshake.request", "system.welcome", "system.reject" }`.

### Payloads (PR‑2)

* **handshake.request**: `client_version: str`, `capabilities: [str]=[]`
* **system.welcome**: `server_version: str`, `session_id: str`, `motd: str`, `i18n_id?: str`, `accepted_capabilities: [str]`
* **system.reject**: `reason: enum{protocol_version_unsupported, server_not_ready, invalid_contract}`, `i18n_id?: str`, `details?: str`, `supported?: [str]` (only for protocol mismatch)

### Validator contract (spec)

* Location: `saskan/infra/schema/validator.py`
* API (spec): `validate(name: str, message: dict) -> {"ok": bool, "errors": [..]}`

  * On success: `{"ok": true}`
  * On failure: `{"ok": false, "errors":[{"scope":"envelope|payload", "path":"$.payload.foo", "keyword":"required|type|enum|pattern|additionalProperties", "message":"…"}]}`
* Flow:

  1. Enforce **hard caps** first (UTF‑8, ≤8 KB, valid JSON) — see ADR‑0009.
  2. Validate **envelope**; if fail and `id` unknown → close (no reply). If `id` known → map to reject (below).
  3. Route by `name` (allow‑list); unknown → payload reject.
  4. Validate **payload** schema.
  5. Protocol negotiation: after envelope; if unsupported → short‑circuit to reject with `supported`.

## Error mapping (wire behavior)

* **Invalid/unknown name or payload failure** → reply `system.reject` with `reason="invalid_contract"` and concise `details`; full validator errors go to logs only.
* **Protocol mismatch** → `system.reject` with `reason="protocol_version_unsupported"` and `supported`.
* **Envelope failure + no reliable id** → drop connection (no reply).

## Testing matrix (acceptance)

1. Valid request → valid welcome.
2. Unknown `name` → reject/invalid\_contract.
3. Missing required in request → reject/invalid\_contract (path points to missing key).
4. Extra property present → reject/invalid\_contract (`additionalProperties`).
5. Protocol mismatch → reject/protocol\_version\_unsupported with `supported`.
6. Welcome contract enforced (simulate omission to ensure tests fail).
7. `i18n_id` optional—present or absent both pass.
8. Non‑JSON / >8 KB line → dropped by server before validator (as per ADR‑0009).

## Doc snippets to paste

* **Envelope regex** for `name`: `^[a-z0-9]+(\.[a-z0-9_-]+)+$`
* **Reserved envelope fields**: `audience`, `severity` (optional, advisory only).
* **Pointer format** in errors: JSON Pointer (e.g., `$.payload.client_version`).

## Open items (minor, can defer if needed)

* Whether to include a **numeric `ver`** for envelope as `"1"` or `1`—current spec uses string; keep consistent.
* Decide if `session_id` format needs a regex (e.g., `^urn:uuid:[0-9a-f-]+$`)—can add later (additive).

---

If that matches your intent, consider ADR‑0011 **frozen** for PR‑2.

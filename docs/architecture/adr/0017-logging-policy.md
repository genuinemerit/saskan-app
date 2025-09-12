# ADR-0017: Logging Schema & Verbosity Policy

**Date:** 2025-09-10  
**Status:** Draft  
**Supersedes/Expands:** ADR-0009 (handshake log sketches)

## Context

ADR-0009 sketches a few lifecycle log lines (READY, HELLO, etc.) but our system needs a consistent, queryable logging **schema** and **verbosity policy** that applies across shells (CLI, PySide, PyGame) and services. We already emit JSONL via a custom formatter and store per-stream files (server/events/debug). We want:

- Stable machine-queryable events (`evt`), not human prefixes buried in strings.
- Environment-controlled **volume** (level), **detail** (metadata fields), and **payload inclusion**.
- Room for growth (gameplay messages, assets, AI calls) without breaking queries.

## Decision

1. **Canonical format:** JSON Lines (one JSON object per line), UTF-8.
2. **Event code:** Every record includes an `evt` field; event names are UPPER_SNAKE (e.g., `READY`, `HELLO`, `MSG_SENT`).
3. **Separation of concerns:**
   - **Level** controls *which events* are emitted (`TRACE|DEBUG|INFO|WARN|ERROR|CRITICAL`).
   - **Formatter profile** controls *which fields* are included (minimal vs debug-rich).
   - **Payload mode** controls *how much of the message payload* is logged.
4. **Environment control (env vars):**
   - `SASKAN_ENV=dev|test|staging|prod`
   - `SASKAN_LOG_PAYLOAD=none|handshake|all` (default: `handshake`)
   - `SASKAN_LOG_DEBUG_META=auto|on|off` (default: `auto` → `on` in dev, `off` otherwise)
   - `SASKAN_SHOW_LOG=0|1` (console echo; default off)
5. **Streams/files:** Keep split files (e.g., `server.jsonl`, `events.jsonl`, `debug.jsonl`) with rotation. No console echo by default.

## Record Schema (minimal, always present)

| Field      | Type    | Notes                                   |
|------------|---------|-----------------------------------------|
| `ts`       | string  | ISO8601 UTC                             |
| `level`    | string  | `TRACE`..`CRITICAL`                     |
| `logger`   | string  | e.g., `saskan.server`                   |
| `evt`      | string  | event code (see taxonomy)               |
| `message`  | string  | short human hint                        |
| `corr`     | string  | correlation id (optional but recommended) |
| `session_id` | string | when applicable                        |

### Debug metadata (included when `SASKAN_LOG_DEBUG_META=on` or `auto` in `dev`)

`module`, `funcName`, `lineno`, `thread`, `process` (and `pathname` only when needed for deep debugging).

### Payload field

`payload` may be included based on `SASKAN_LOG_PAYLOAD`. Large blobs must be trimmed or summarized (see “Payload policy”).

## Event Taxonomy (initial set)

### Lifecycle & handshake

- `READY` — server ready (`host`, `port`, `protocol`)
- `CONN_OPEN` — inbound connection (`addr`)
- `HELLO` — handshake outcome (`outcome`, `latency_ms`, optional `reason`, optional `payload` per policy)
- `CONN_CLOSE` — connection closed (`addr`)

### Messaging

- `MSG_RECV` — message received (`name`, essentials)
- `MSG_SENT` — message sent (`name`, essentials)

### Game loop (expand as features arrive)

- `CMD` — command accepted (`name`, essentials)
- `TICK` — turn advanced (`turn`, `delta_ms`)
- `STATE_SNAP` — snapshot written (`id`, `size_bytes`)

### Assets & AI

- `ASSET_FETCH` — client/server asset action (`asset_id`, `variant_id`, `status`)
- `AI_GEN` — AI generation request/finish (`job_id`, `status`, timings)

### I/O & errors

- `IO_WARN`, `IO_ERR` — filesystem/network issues (include `op`, `path/url`, status/errno)

Event names are stable; we’ll append new ones as features land. Avoid renaming—add new events instead.

## Payload Policy

- Default: `SASKAN_LOG_PAYLOAD=handshake`
  - Include handshake/welcome payload essentials (e.g., `server_version`, `session_id`, `i18n_id`, `accepted_capabilities`, `motd`).
  - For gameplay and other messages, log **essentials only** (ids, counts, durations), not full payloads.
- `none`: never include `payload`.
- `all`: include `payload` for all events (dev only; may be heavy).

**Trimming:** payloads > 4 KiB are truncated with `payload_trunc=true` and `payload_bytes=<n>`.  
**Redaction:** always redact secrets/PII (tokens, auth, emails) with `***`.

## Formatter Profiles

- **Minimal** (prod/staging default): base fields + `evt` + essentials; no file/line by default.
- **Debug** (dev default): minimal + debug metadata fields.
- Controlled by `SASKAN_LOG_DEBUG_META`.

## Levels per Environment

- **dev:** default `TRACE`/`DEBUG`; console echo opt-in.
- **test/CI:** `INFO`; console enabled to surface in CI logs; payloads `none` or `handshake`.
- **staging:** `INFO`; payloads `handshake`; enable targeted `DEBUG` per component/session via dynamic overrides.
- **prod:** `INFO`; payloads `handshake` or `none`; enable time-boxed `DEBUG` overrides when diagnosing issues.

## Correlation

Include `corr` on every server-side record that is part of a request/response flow; propagate to clients/shells. Include `session_id` when available.

## Sampling & Flood Control

- Optional sampling for high-volume events (e.g., `MSG_SENT`) in prod; never sample errors.
- Burst coalescing: when identical events repeat rapidly, emit `suppressed=<N>` summaries.

## File Strategy & Rotation

- Keep separate rotating files: `server.jsonl`, `events.jsonl`, `debug.jsonl`.
- Rotation by size (10MB) with 5 backups (current defaults).
- No console echo unless `SASKAN_SHOW_LOG=1`.

## Security

- Redact secrets/PII at write time (token, auth headers, emails, IPs where required).
- Never log private keys or credentials.
- Audit logs periodically with jq queries baked into CI (lint for `payload` size, presence of forbidden keys).

## Alternatives Considered

- Free-form plaintext: rejected; hurts queryability and parsing.
- Single monolithic file: rejected; stream separation simplifies ops and retention.
- CLI flags for verbosity: rejected; env-driven config is simpler and consistent across shells.

## Consequences

- Stable schema that supports jq queries and downstream shipping (vector/fluent-bit) later.
- Reduced noise in prod without losing debuggability in dev.
- Clear knobs to adjust volume/detail without code changes.

## Acceptance Criteria

- All new/modified logs include `evt`.
- Dev: debug metadata present; Prod: minimal profile by default.
- Payload inclusion matches `SASKAN_LOG_PAYLOAD`.
- Handshake logs (`HELLO`) include essentials; non-handshake logs avoid full payloads.
- jq smoke queries:
  - `select(.evt=="HELLO") | {ts,outcome,latency_ms}`
  - `select(.level|IN("ERROR","CRITICAL"))`
  - event counts by `evt`.

## Migration Notes

- Introduce thin wrappers (e.g., `infra/log/events.py`) that set `evt` and apply payload policy.
- Replace direct `log.info(str(dict))` call sites with wrappers incrementally.
- Keep ADR-0009 examples as “developer hints,” but treat ADR-0017 as normative for schema/policy.

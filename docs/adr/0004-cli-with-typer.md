# ADR-0004: CLI with Typer

Date: 2025-08-17

Status: Accepted

Context: We want a productive CLI for world-building and testing, with strong help UX.

## Decisions

- Use Typer for a multi-command CLI. Commands mirror client API: new, load, tick, inspect, plan, commit, story test, with --format table|json. Commands are thin wrappers over pure functions.

- A thin, stable CLI that:

  - Exposes user flows (e.g., connect/handshake) without leaking engine internals.
  - Delegates work to a client API (not directly to engine/core).
  - Produces predictable stdout/stderr and exit codes for scripting.

### Command topology

- Root command: saskan

- PR‑2 scope (only):
  - `saskan connect` — handshake probe
  - `saskan version` — prints CLI/app/protocol versions (sanity/probing)

- Reserve namespaces for later (don’t implement yet): game, dev, admin.

### Config precedence

- CLI flags > environment > defaults.

- Keys for PR‑2: host, port, protocol.

- Environment: SASKAN_HOST, SASKAN_PORT, SASKAN_PROTOCOL.

### I/O discipline

- stdout: user‑facing, single‑line success messages.
- stderr: errors (reject, timeout, validation issues).
- Logs: never to stdout/stderr from CLI; logs belong to server.

### Exit codes

- 0 success (WELCOME received).
- 10 reject (protocol/version/etc.).
- 11 timeout / network error.
- 12 invalid CLI args or config.

### Layering

- ui_cli → client API (infra/net/client) only.
- No imports from engine/core in CLI modules.

### Help & UX

- Concise --help.
- Defaults shown in help (resolved env/defaults).
- Dry‑run flag is out‑of‑scope for PR‑2 (avoid feature creep).

## Consequences

Consistent ergonomics, autogen help, easy testing.

Typer dependency; minor learning curve from argparse.

## Alternatives considered

argparse (baseline, more boilerplate), Click (similar ergonomics; Typer aligns better with type hints).

## Notes/Follow-ups

- Establish examples in help text. See skunkworks/feat(first_handshake)
- Add Typer test helpers later

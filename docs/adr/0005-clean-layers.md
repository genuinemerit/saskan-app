# ADR-0005: Clean Layering & Purity Boundaries

Date: 2025-08-21

Status: Accepted

## Intent

- Prevent spaghetti and enable future engine/UI swaps.
- Enforce a one‑directional dependency flow and clear responsibilities:

```text
ui_*  →  client API (infra/net client)  →  infra  →  engine  →  core
```

- No lateral “reach‑through,” no back‑edges.

## Decision

### Enforce these boundaries

- core/ domain models and hex/sim math are pure (no IO, no globals).
- engine/ orchestrates turn pipeline; systems return events; only a single commit mutates state.
- infra/ owns persistence, messaging, logging, config.
- UI layers communicate only via client API/messages.
- One RNG service, seeded per turn, passed explicitly.

#### Authoritative import graph

| Layer    | May import from…                                        | Must NOT import from…                                                          |
| -------- | ------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `ui_*`   | `ui_*` (local), `infra.net.client`, `infra.config`      | `engine`, `core`, `infra.net.server`, `infra.persistence`                      |
| `infra`  | `infra.*`, `engine` (facades only), `core` (pure types) | `ui_*`                                                                         |
| `engine` | `engine.*`, `core.*`                                    | `ui_*`, `infra.net.server/client`, `infra.persistence` (except via interfaces) |
| `core`   | `core.*` only                                           | everything else                                                                |
| `tests`  | any (white‑box allowed)                                 | —                                                                              |

Add an explicit exception hook: test helpers may cross layers, production code may not.

#### DTO & validation boundaries

DTOs crossing layers are plain data (no methods).

JSON Schema lives in infra/schema; all wire validation is done in infra (not in UI/engine).

Engine validates domain invariants internally; it never parses wire JSON.

#### Config & logging boundaries

Config source of truth in infra/config (env + defaults).

Logging backends in infra/log; UI prints user messages only; server writes logs.

#### Net split

infra/net/server is server‑only; no UI import.

infra/net/client is client API; only UI uses it.

### Cycles & friend modules

No cyclic imports across layers.

If an interface is needed (e.g., persistence), define an abstract port in engine and an adapter in infra.

### Consequences

- High testability; easier refactors (e.g., alternate UIs or simulation detail).

- Slight overhead for event plumbing and state commits.

### Alternatives considered

Active-record style models (convenient, leaky IO), ad-hoc mutation across systems (fast initially, brittle).

## Notes/Follow-ups

Add property tests for invariants (conservation, non-negative populations, acyclic agency DAG). Define JSON Schemas for snapshots, triggers, config, intents, messages.

## Concrete guardrails

1. Import ruleset (document in ADR)

- Allowed from … import … patterns per table above.

- Ban relative imports that jump layers (e.g., from ..engine import … in UI).

1. Static checks in CI (later)

- Add import-linter contract (or snakeviz/import-linter style):

  - Contract A: ui _may import only ui_ and `saskan.infra.net.client`, `saskan.infra.config`.

  - Contract B: engine not allowed to import `saskan.infra.*` or `saskan.ui_*`.

  - Contract C: core not allowed to import outside `saskan.core.*`.

1. Packaging boundaries

- Each layer has __init__.py that exports only public symbols (hide internals).

- Public API of client lives at saskan.infra.net.client.

1. Schema boundary

- All schemas: `saskan/infra/schema/*.json`; single validator module `saskan/infra/schema/validator.py`.

- UI/engine import only the typed DTOs, never the raw schemas.

## Acceptance checks

- Import matrix is defined (see above)
- Diagram shows arrows only downward (UI→infra→engine→core)
- DTO/schema boundaries are defined (see above)

### Code

- No `ui_*` imports from engine/core.
- `infra/net/server` unused by CLI modules.
- JSON schemas present only under `infra/schema`.

### Tests

- A basic import‑graph test that fails if `ui_cli` imports `engine` or `core`.
- Smoke E2E still passes (proving the boundaries aren’t breaking functionality).

## Allowed Imports (authoritative)

Modules may import the __Python stdlib__ and third‑party libraries freely. Cross‑layer imports are restricted as follows:

| Layer    | May import from…                                                                                    | Must **not** import from…                                                                                                          |
| -------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `ui_*`   | `saskan.ui_*` (same UI package), `saskan.infra.net.client`, `saskan.infra.config`                   | `saskan.engine.*`, `saskan.core.*`, `saskan.infra.net.server`, `saskan.infra.persistence.*`                                        |
| `infra`  | `saskan.infra.*`, **facades only** from `saskan.engine.*`, **pure types only** from `saskan.core.*` | `saskan.ui_*`                                                                                                                      |
| `engine` | `saskan.engine.*`, `saskan.core.*`                                                                  | `saskan.ui_*`, `saskan.infra.net.server`, `saskan.infra.net.client`, `saskan.infra.persistence.*` (except via abstract interfaces) |
| `core`   | `saskan.core.*` only                                                                                | anything outside `saskan.core.*`                                                                                                   |
| `tests`  | any project package (white‑box allowed)                                                             | —                                                                                                                                  |
**Notes & clarifications**

- **DTO/Schema boundary:** JSON Schema lives under `saskan.infra.schema`. UI and engine consume **DTOs**, not raw schemas.
- **Abstract interfaces (ports):** If engine needs persistence/networking, define an interface in `engine` and implement the adapter in `infra`. Engine imports the interface only; `infra` depends on engine to implement the adapter (Dependency Inversion).
- **Relative imports:** Disallow cross‑layer relative hops (e.g., from `ui_cli` doing `from ..engine import …`).
- **Stdlib/third‑party:** Permitted everywhere (e.g., `json`, `typing`, `socketserver`, `pydantic/jsonschema lib`).

### Examples

**Allowed (UI → client API):**

```python
# saskan/ui_cli/commands/connect.py
from saskan.infra.net.client import handshake_probe
from saskan.infra.config import NetConfig
```

**Disallowed (UI reaching into engine):**

```python
# ❌ Not allowed
from saskan.engine.systems import world_clock
```

**Allowed (Engine using Core):**

```python
# saskan/engine/systems/handshake.py
from saskan.core.model.session import SessionId
```

**Disallowed (Engine pulling Infra):**

```python
# ❌ Not allowed
from saskan.infra.net.server import ThreadingServer
```

# ADR-0005: Clean Layering & Purity Boundaries

**Date:** 2025-08-21
**Status:** Accepted

## Intent

- Prevent spaghetti code and facilitate future engine/UI swaps.
- Enforce a one-directional dependency flow:

```text
ui_*  →  client API (infra/net client)  →  infra  →  engine  →  core
```

## Decision

### Enforce Boundaries

- **Core:** Pure domain models and math; no IO or globals.
- **Engine:** Orchestrates turn pipeline; single commit mutates state.
- **Infra:** Manages persistence, messaging, logging, config.
- **UI:** Communicates via client API/messages only.
- **RNG Service:** Seeded per turn, passed explicitly.

#### Import Rules

| Layer    | Allowed Imports                                            | Disallowed Imports                                                   |
| -------- | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| `ui_*`   | `ui_*`, `infra.net.client`, `infra.config`                 | `engine`, `core`, `infra.net.server`, `infra.persistence`            |
| `infra`  | `infra.*`, `engine` (facades), `core` (pure types)         | `ui_*`                                                               |
| `engine` | `engine.*`, `core.*`                                       | `ui_*`, `infra.net.server/client`, `infra.persistence` (except interfaces) |
| `core`   | `core.*` only                                              | everything else                                                      |
| `tests`  | any (white-box allowed)                                    | —                                                                    |

- **DTOs:** Plain data crossing layers; JSON Schema in `infra/schema`.
- **Config/Logging:** Source of truth in `infra/config`; logging in `infra/log`.

### Cycles & Interfaces

- No cyclic imports across layers.
- Define interfaces in `engine`, adapters in `infra`.

## Consequences

- High testability and easier refactors.
- Slight overhead for event plumbing and state commits.

## Alternatives Considered

- Active-record models (convenient but leaky IO).
- Ad-hoc mutation (fast initially, brittle).

## Notes/Follow-ups

- Add property tests for invariants.
- Define JSON Schemas for snapshots, triggers, etc.

## Guardrails

1. **Import Ruleset:** Document allowed patterns; ban cross-layer relative imports.
2. **Static Checks:** Use import-linter contracts in CI.
3. **Packaging Boundaries:** Each layer exports only public symbols.
4. **Schema Boundary:** All schemas in `infra/schema`; UI/engine use typed DTOs only.

## Acceptance Checks

- Defined import matrix and downward-only diagram.
- DTO/schema boundaries established.

### Code Examples

**Allowed (UI → client API):**

```python
from saskan.infra.net.client import handshake_probe
from saskan.infra.config import NetConfig
```

**Disallowed (UI → Engine):**

```python
# ❌ Not allowed
from saskan.engine.systems import world_clock
```

**Allowed (Engine → Core):**

```python
from saskan.core.model.session import SessionId
```

**Disallowed (Engine → Infra):**

```python
# ❌ Not allowed
from saskan.infra.net.server import ThreadingServer
```

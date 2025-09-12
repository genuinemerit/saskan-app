# Project Structure

## Project Tree

At the top level is the repository, with `saskan/` being the only installable package. Documentation, including ADRs, resides outside the package. To generate a detailed project tree diagram, run:

```bash
bash scripts/make-tree.sh
```

## Notes

- Only `saskan/` is packaged; `data/` under it ensures assets ship with the wheel.
- `docs/adr/` holds decision history; keep each record short and dated.
- `infra/schema/` is the runtime validator location; `data/schemas/` can mirror for authoring.
- Tests are separated into `unit/` (pure) vs. `integration/` (engine+infra paths).
- Keep all hex geometry in `ui_pygame/render/hex_projector.py` (pixel math) and `core/hex/` (axial/cube math). Avoid duplicates.

## Summaries of Packages

### saskan (root package)

**Purpose:**
App entry/metadata; binds subpackages; central types and constants shared across layers (sparingly).

**Components:**

- `__init__` (version, paths)
- Minimal config loader façade
- Typed IDs
- Error types

**MVP Use Cases:**

1. Import root to access version and paths
2. Central error types for CLI/server

**Anti-patterns:**
Avoid stuffing globals/state here and circular imports to subpackages.

**Patterns:**
“Narrow waist” — light, stable surface; shared types, not logic.

### core

**Purpose:**
Pure domain model + hex geometry + world state; no I/O.

**Components:**

- Subpackages: `hex/` (axial/cube math), `model/` (World, Tile, Node, Edge, Faction, Actor, Resource, StoryFlag), `selectors/` (queries over state), `rules/` (validation invariants)
- Classes: Lightweight dataclasses / value objects; state containers

**MVP Use Cases:**

1. Build a tiny hex world from a seed
2. Query neighbors/rings/range
3. Validate invariants (no negative populations, etc.)

**Anti-patterns:**
Methods performing I/O; pandas/numpy leaking into entities; hidden mutation.

**Patterns:**
Functional core/imperative shell; value semantics; single authority for hex math.

### engine

**Purpose:**
Orchestrates the turn pipeline; systems compute events; single commit mutates state.

**Components:**

- Subpackages: `systems/` (Ecology, Agriculture, Population, Logistics, Economy, Politics, Agency, Story, Visibility), `turns/` (phase runner), `events/` (typed event records), `rng/` (seeded generator), `intents/` (player/A.I. intents)
- Classes: `TurnRunner`, `EventBus` (in-proc), `System` interfaces

**MVP Use Cases:**

1. Advance one turn over a 32×32 hex map
2. Fire a simple story trigger and enqueue effects
3. Produce a turn summary (counts, timings)

**Anti-patterns:**
Systems mutating state directly; order-dependent hidden side effects; global RNG.

**Patterns:**
Event sourcing (lightweight): systems → events → commit; explicit phase ordering; deterministic RNG passed as a dependency.

### infra

**Purpose:**
All side-effects: persistence, messaging, config, logging, schema validation.

**Components:**

- Subpackages: `persistence/` (SQLite/SQLAlchemy models, snapshot I/O), `net/` (JSON over TCP client/server, message envelope), `config/` (layered config), `log/` (structured logs), `schema/` (JSON Schemas; validators)
- Classes: `SnapshotStore`, `SqlSessionFactory`, `MessageBroker` (sockets), `Config`

**MVP Use Cases:**

1. Save/load per-turn snapshots
2. Local loopback client–server with `advance_turn`
3. Validate trigger/config JSON against schemas

**Anti-patterns:**
Letting infra types bleed into `core`/`engine`; ad-hoc JSON without schemas; leaking stack traces across the wire.

**Patterns:**
Ports & Adapters (hexagonal): adapters here, ports in engine; explicit schemas; structured logging with correlation IDs.

### ui\_cli

**Purpose:**
First UI; Typer commands thinly wrapping client API; debug and world-building tooling.

**Components:**

- Subpackages: `commands/` (new, load, tick, inspect, plan, commit, story-test), `render/` (table/json formatters), `client/` (calls into infra.net)
- Objects: `App` (command group), format utilities

**MVP Use Cases:**

1. `saskan new --seed …` then `tick`
2. `inspect tile q r` and `inspect node id`
3. Dry-run a `story-test event_id`

**Anti-patterns:**
Business logic in command handlers; printing debug blobs without structure; coupling CLI to engine internals.

**Patterns:**
Thin CLI, fat services; consistent output modes (table|json); helpful `--help` examples.

### ui\_pyside

**Purpose:**
Menus, dialogs, settings (not the map loop); forward commands to client API.

**Components:**

- Subpackages: `views/` (menus, settings, load/save dialogs), `viewmodels/` (bind UI to client), `i18n/` (string tables/gettext glue)
- Classes: `MainWindow`, `SettingsViewModel`

**MVP Use Cases:**

1. Start/load game and advance one turn from a menu
2. Tweak basic settings
3. Show turn summary dialog

**Anti-patterns:**
Running the simulation loop here; mixing PyGame canvas with Qt widgets directly.

**Patterns:**
MVVM-lite; UI only calls client API; centralized i18n.

### ui\_pygame

**Purpose:**
Map canvas + input handling for the map; renders state snapshots; integrates timers/event loop for visualization.

**Components:**

- Subpackages: `render/` (hex projection, layers), `input/` (map interactions), `hud/` (minimal overlays)
- Classes: `MapView`, `HexProjector`, `LayerRenderer`

**MVP Use Cases:**

1. Render static world with panning/zoom
2. Highlight rings/ranges/paths
3. Display per-turn diffs (added/changed tiles/nodes)

**Anti-patterns:**
Owning game state; duplicating hex math (must delegate to `core.hex`).

**Patterns:**
Renderer as a pure consumer of read-only state; strict separation of pixel vs. axial coords.

### sims

**Purpose:**
Numeric/algorithmic simulators (numpy/pandas) encapsulated behind simple interfaces; no domain leakage.

**Components:**

- Subpackages: `ecology/`, `population/`, `logistics/`, each exposing pure functions taking/returning plain Python data (lists/dicts/tuples)
- Utilities: Calibration/parameter sets

**MVP Use Cases:**

1. Compute agriculture yield for a region (inputs: fertility, weather)
2. Estimate migration flows along edges
3. Calculate famine risk index

**Anti-patterns:**
Returning DataFrames to the engine; reading files from inside sims; using global state.

**Patterns:**
“Functional kernel” — numpy inside, plain data out; parameterized, testable functions with fixed seeds.

---

## Patterns and Anti-Patterns

### Cross-cutting “Good Thinking” Patterns to Embrace

- **Functional Core, Imperative Shell:** Pure `core`/`sims`; orchestration and I/O at the edges.
- **Explicit Data Contracts:** JSON Schemas for snapshots, triggers, configs, and messages; validate at boundaries.
- **Event-Driven Internals:** Systems produce events; one commit applies them → debuggable and revertible.
- **Determinism by Design:** Single RNG service, seeded per turn, passed explicitly.
- **Narrow Interfaces:** UI talks only via client API; one hex-math module; one persistence façade.
- **Observability Early:** Per-phase timings, event counts, and “why a trigger fired” logs.

### Cross-cutting Anti-Patterns to Avoid

- **Leaky Abstractions:** UI importing engine/core internals; infra types inside domain.
- **Hidden Mutation:** Systems quietly changing state; global singletons.
- **Over-modeling:** Deep hierarchies/monolith classes (keep entities lean; behavior in systems).
- **Data–Code Entanglement:** Lore text embedded in code; predicates implemented as arbitrary Python before the schema is stable.

# Project Structure

## Project Tree

Top-level is the repo; `saskan/` is the only installable package. 

Docs (incl. ADRs) live outside the package.

```
saskan-lands/
├─ README.md
├─ LICENSE
├─ pyproject.toml                # poetry config
├─ .python-version               # optional (pyenv)
├─ .gitignore
├─ .env.example                  # sample env
├─ Makefile                      # dev shortcuts (lint, test, run)
├─ .pre-commit-config.yaml       # black/ruff/isort/mypy
├─ .editorconfig
├─ docs/
│  ├─ index.md                   # project overview
│  ├─ architecture.md            # diagrams, boundaries
│  ├─ glossary.md                # ADR, DSL, MVP, RNG, etc.
│  ├─ adr/                       # Architecture Decision Records
│  │  ├─ 0001-hex-grid.md
│  │  ├─ 0002-snapshots.md
│  │  ├─ 0003-triggers-json.md
│  │  ├─ 0004-cli-typer.md
│  │  └─ 0005-boundaries.md
│  └─ diagrams/                  # draw.io/mermaid/png
├─ scripts/                      # dev scripts (no runtime deps)
│  ├─ gen_dummy_world.sh
│  └─ format_all.sh
├─ tests/
│  ├─ conftest.py
│  ├─ unit/
│  │  ├─ test_hex.py
│  │  ├─ test_triggers.py
│  │  └─ test_systems_ecology.py
│  └─ integration/
│     └─ test_turn_pipeline.py
└─ saskan/
   ├─ __init__.py                # version, narrow shared types
   ├─ core/                      # pure domain + hex math
   │  ├─ __init__.py
   │  ├─ hex/                    # axial/cube math, distance, rings
   │  │  └─ __init__.py
   │  ├─ model/                  # World, Tile, Node, Edge, etc.
   │  │  └─ __init__.py
   │  ├─ selectors/              # read-only queries over state
   │  │  └─ __init__.py
   │  └─ rules/                  # invariants/validators
   │     └─ __init__.py
   ├─ engine/                    # turn orchestration + systems
   │  ├─ __init__.py
   │  ├─ events/                 # event records/types
   │  │  └─ __init__.py
   │  ├─ rng/                    # seeded RNG service
   │  │  └─ __init__.py
   │  ├─ intents/                # player/AI intents
   │  │  └─ __init__.py
   │  ├─ systems/                # ecology/agriculture/...
   │  │  ├─ __init__.py
   │  │  ├─ ecology.py
   │  │  ├─ agriculture.py
   │  │  ├─ population.py
   │  │  ├─ logistics.py
   │  │  ├─ economy.py
   │  │  ├─ politics.py
   │  │  ├─ agency.py
   │  │  └─ visibility.py
   │  └─ turn/                   # ordered phases, commit
   │     └─ __init__.py
   ├─ infra/                     # IO: persistence, net, config, logs
   │  ├─ __init__.py
   │  ├─ persistence/
   │  │  ├─ __init__.py
   │  │  ├─ orm.py               # SQLAlchemy models (SQLite)
   │  │  ├─ snapshots.py         # per-turn snapshot I/O
   │  │  └─ seed_io.py           # import/export seeds/maps
   │  ├─ net/
   │  │  ├─ __init__.py
   │  │  ├─ server.py            # JSON-over-TCP
   │  │  └─ client.py
   │  ├─ config/
   │  │  ├─ __init__.py
   │  │  └─ loader.py            # layered config (defaults/env/file)
   │  ├─ log/
   │  │  ├─ __init__.py
   │  │  └─ logger.py            # structured logging
   │  └─ schema/
   │     ├─ __init__.py
   │     ├─ snapshots.schema.json
   │     ├─ triggers.schema.json
   │     ├─ config.schema.json
   │     └─ messages.schema.json
   ├─ ui_cli/                    # Typer-based CLI
   │  ├─ __init__.py
   │  ├─ commands/
   │  │  ├─ __init__.py
   │  │  ├─ new.py
   │  │  ├─ load.py
   │  │  ├─ tick.py
   │  │  ├─ inspect.py
   │  │  ├─ plan.py
   │  │  └─ story_test.py
   │  ├─ render/
   │  │  ├─ __init__.py
   │  │  └─ formatters.py        # table|json
   │  └─ client/
   │     └─ __init__.py          # thin wrapper over infra.net.client
   ├─ ui_pyside/                 # Qt menus/dialogs (later)
   │  ├─ __init__.py
   │  ├─ views/
   │  │  └─ __init__.py
   │  ├─ viewmodels/
   │  │  └─ __init__.py
   │  └─ i18n/
   │     └─ __init__.py
   ├─ ui_pygame/                 # map canvas & interactions (later)
   │  ├─ __init__.py
   │  ├─ render/
   │  │  ├─ __init__.py
   │  │  └─ hex_projector.py     # axial↔pixel only here
   │  ├─ input/
   │  │  └─ __init__.py
   │  └─ hud/
   │     └─ __init__.py
   ├─ sims/                      # numpy/pandas sims (pure-in/pure-out)
   │  ├─ __init__.py
   │  ├─ ecology/
   │  │  └─ __init__.py
   │  ├─ population/
   │  │  └─ __init__.py
   │  └─ logistics/
   │     └─ __init__.py
   ├─ data/                      # non-Python assets (loaded at runtime)
   │  ├─ config/                 # tunables per system
   │  ├─ maps/                   # seeds/heightmaps
   │  ├─ story/                  # triggers/effects packs
   │  ├─ locales/                # i18n (e.g., en/LC_MESSAGES/*.po)
   │  └─ schemas/                # shared JSON Schemas (optional dup)
   └─ tools/                     # lightweight utilities (non-core)
      ├─ __init__.py
      └─ exporters.py
```

## Notes

* Only `saskan/` is packaged; `data/` under it ensures assets ship with the wheel.
* `docs/adr/` holds decision history; keep each record short and dated.
* `infra/schema/` is the runtime validator location; `data/schemas/` can mirror for authoring.
* Tests separate `unit/` (pure) vs. `integration/` (engine+infra paths).
* Keep *all* hex geometry in `ui_pygame/render/hex_projector.py` (pixel math) and `core/hex/` (axial/cube math). No duplicates.

## Summaries of Packages

“Packages” here are the dirs with `__init__.py`: `saskan`, `core`, `engine`, `infra`, `ui_cli`, `ui_pyside`, `ui_pygame`, `sims`.

# saskan (root package)

* **Purpose:** App entry/metadata; binds subpackages; central types and constants shared across layers (sparingly).
* **Components:** `__init__` (version, paths), minimal config loader façade, typed IDs, error types.
* **MVP use cases:**

  1. Import root to access version and paths; 2) Central error types for CLI/server.
* **Anti-patterns:** Stuffing globals/state here; circular imports to subpackages.
* **Patterns:** “Narrow waist” — light, stable surface; shared types, not logic.

# core

* **Purpose:** Pure domain model + hex geometry + world state; no I/O.
* **Components:**

  * Subpackages: `hex/` (axial/cube math), `model/` (World, Tile, Node, Edge, Faction, Actor, Resource, StoryFlag), `selectors/` (queries over state), `rules/` (validation invariants).
  * Classes: lightweight dataclasses / value objects; state containers.
* **MVP use cases:**

  1. Build a tiny hex world from a seed; 2) Query neighbors/rings/range; 3) Validate invariants (no negative populations, etc.).
* **Anti-patterns:** Methods performing I/O; pandas/numpy leaking into entities; hidden mutation.
* **Patterns:** Functional core/imperative shell; value semantics; single authority for hex math.

# engine

* **Purpose:** Orchestrates the turn pipeline; systems compute events; single commit mutates state.
* **Components:**

  * Subpackages: `systems/` (Ecology, Agriculture, Population, Logistics, Economy, Politics, Agency, Story, Visibility), `turns/` (phase runner), `events/` (typed event records), `rng/` (seeded generator), `intents/` (player/A.I. intents).
  * Classes: `TurnRunner`, `EventBus` (in-proc), `System` interfaces.
* **MVP use cases:**

  1. Advance one turn over a 32×32 hex map; 2) Fire a simple story trigger and enqueue effects; 3) Produce a turn summary (counts, timings).
* **Anti-patterns:** Systems mutating state directly; order-dependent hidden side effects; global RNG.
* **Patterns:** Event sourcing (lightweight): systems → events → commit; explicit phase ordering; deterministic RNG passed as a dependency.

# infra

* **Purpose:** All side-effects: persistence, messaging, config, logging, schema validation.
* **Components:**

  * Subpackages: `persistence/` (SQLite/SQLAlchemy models, snapshot I/O), `net/` (JSON over TCP client/server, message envelope), `config/` (layered config), `log/` (structured logs), `schema/` (JSON Schemas; validators).
  * Classes: `SnapshotStore`, `SqlSessionFactory`, `MessageBroker` (sockets), `Config`.
* **MVP use cases:**

  1. Save/load per-turn snapshots; 2) Local loopback client–server with `advance_turn`; 3) Validate trigger/config JSON against schemas.
* **Anti-patterns:** Letting infra types bleed into `core`/`engine`; ad-hoc JSON without schemas; leaking stack traces across the wire.
* **Patterns:** Ports & Adapters (hexagonal): adapters here, ports in engine; explicit schemas; structured logging with correlation IDs.

# ui\_cli

* **Purpose:** First UI; Typer commands thinly wrapping client API; debug and world-building tooling.
* **Components:**

  * Subpackages: `commands/` (new, load, tick, inspect, plan, commit, story-test), `render/` (table/json formatters), `client/` (calls into infra.net).
  * Objects: `App` (command group), format utilities.
* **MVP use cases:**

  1. `saskan new --seed …` then `tick`; 2) `inspect tile q r` and `inspect node id`; 3) Dry-run a `story-test event_id`.
* **Anti-patterns:** Business logic in command handlers; printing debug blobs without structure; coupling CLI to engine internals.
* **Patterns:** Thin CLI, fat services; consistent output modes (table|json); helpful `--help` examples.

# ui\_pyside

* **Purpose:** Menus, dialogs, settings (not the map loop); forward commands to client API.
* **Components:**

  * Subpackages: `views/` (menus, settings, load/save dialogs), `viewmodels/` (bind UI to client), `i18n/` (string tables/gettext glue).
  * Classes: `MainWindow`, `SettingsViewModel`.
* **MVP use cases:**

  1. Start/load game and advance one turn from a menu; 2) Tweak basic settings; 3) Show turn summary dialog.
* **Anti-patterns:** Running the simulation loop here; mixing PyGame canvas with Qt widgets directly.
* **Patterns:** MVVM-lite; UI only calls client API; centralized i18n.

# ui\_pygame

* **Purpose:** Map canvas + input handling for the map; renders state snapshots; integrates timers/event loop for visualization.
* **Components:**

  * Subpackages: `render/` (hex projection, layers), `input/` (map interactions), `hud/` (minimal overlays).
  * Classes: `MapView`, `HexProjector`, `LayerRenderer`.
* **MVP use cases:**

  1. Render static world with panning/zoom; 2) Highlight rings/ranges/paths; 3) Display per-turn diffs (added/changed tiles/nodes).
* **Anti-patterns:** Owning game state; duplicating hex math (must delegate to `core.hex`).
* **Patterns:** Renderer as a pure consumer of read-only state; strict separation of pixel vs. axial coords.

# sims

* **Purpose:** Numeric/algorithmic simulators (numpy/pandas) encapsulated behind simple interfaces; no domain leakage.
* **Components:**

  * Subpackages: `ecology/`, `population/`, `logistics/`, each exposing pure functions taking/returning plain Python data (lists/dicts/tuples).
  * Utilities: calibration/parameter sets.
* **MVP use cases:**

  1. Compute agriculture yield for a region (inputs: fertility, weather); 2) Estimate migration flows along edges; 3) Calculate famine risk index.
* **Anti-patterns:** Returning DataFrames to the engine; reading files from inside sims; using global state.
* **Patterns:** “Functional kernel” — numpy inside, plain data out; parameterized, testable functions with fixed seeds.

---

# Patterns and Anti-Patterns

## Cross-cutting “good thinking” patterns to embrace

* **Functional Core, Imperative Shell:** Pure `core`/`sims`; orchestration and I/O at the edges.
* **Explicit Data Contracts:** JSON Schemas for snapshots, triggers, configs, and messages; validate at boundaries.
* **Event-Driven Internals:** Systems produce events; one commit applies them → debuggable and revertible.
* **Determinism by Design:** Single RNG service, seeded per turn, passed explicitly.
* **Narrow Interfaces:** UI talks only via client API; one hex-math module; one persistence façade.
* **Observability Early:** Per-phase timings, event counts, and “why a trigger fired” logs.

## Cross-cutting anti-patterns to avoid

* **Leaky Abstractions:** UI importing engine/core internals; infra types inside domain.
* **Hidden Mutation:** Systems quietly changing state; global singletons.
* **Over-modeling:** Deep hierarchies/monolith classes (keep entities lean; behavior in systems).
* **Data–Code Entanglement:** Lore text embedded in code; predicates implemented as arbitrary Python before the schema is stable.




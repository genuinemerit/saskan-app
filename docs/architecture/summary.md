# Architecture / High-level

* **Layered structure**: Keep a clear separation between

  * **Core game logic** (rules, entities, world simulation)
  * **Persistence** (SQLite + SQLAlchemy ORM)
  * **Presentation** (PySide for UI menus, PyGame for canvas & loop).
    This keeps spaghetti away, and you can later swap/expand any layer (e.g., replace PyGame loop with Unity or Godot).

* **Client/server**:

  * For prototyping, keep the server dumb and lightweight — run both client and server locally at first.
  * Design messages as **plain JSON over sockets** — human-readable, easy to debug. Later, if needed, swap in protobuf/msgpack.

## Tooling / Scaffolding

* **Poetry + tox** for clean packaging/testing.
* **SQLAlchemy models** for core entities (player, town, NPC, world state).
* **Alembic** if schema migration becomes necessary (but maybe skip until DB stabilizes).
* **Logging** early on — even a simple structured logger saves headaches.

## Data Handling

* **Relational DB (SQLite)**: for persistent entities and history.
* **JSON files**: for configs, maps, cultural tables, event probabilities, etc.
* **Numpy/Pandas**: for simulations (ecology, population, economy). Consider wrapping these in service modules so you can scale complexity later.

## UI / UX

* **PySide**: Good for menus, dialogs, settings.
* **PyGame**: Focus it only on the game loop, timers, canvas. Keep the overlap minimal (don’t let UI bleed into game loop).
* **Internationalization**: Early habit — wrap UI strings in gettext or even a thin string-table class.

### UI strategy

**CLI first (ui\_cli/):**

* Commands: `new`, `tick`, `inspect <tile|node|region>`, `plan <intent>`, `commit`, `log`.
* Output: compact tables + JSON dump option for debugging.
* Input: simple REPL + history; keep it stateless against server where possible.

**Later (PySide + PyGame):**

* PySide owns menu/settings/dialogs.
* PyGame owns render surface + input for the map.
* UI talks to client API only (never imports engine/core directly).

## Development Approach

* **Start with “toy loops”**: e.g., a world-tick loop that simulates a small town’s food supply with random events. Then add UI hooks, then persistence.
* **Entity-first**: Define your world entities in code + ORM early (Player, Town, Resource, NPC). Keep the models lean and composable.
* **Pull prototypes**: Make each imported experiment a **module** rather than tangled code. If something works, integrate; if not, you can unplug it.

## High-level structure

```text
saskan/
  core/                # pure game domain (no IO/UI)
  data/                # JSON configs, seed content, locale files
  engine/              # turn loop, systems, rules, scripting
  infra/               # persistence, messaging, logging, config
  ui_cli/              # initial CLI tooling
  ui_pyside/           # menus/dialogs (later)
  ui_pygame/           # canvas + event loop integration (later)
  sims/                # ecology/population/economy simulators
  tools/               # one-off utilities, importers, exporters
  tests/
```

## Core principles

* Pure domain in `core/` (deterministic, side-effect free).
* IO at edges (`infra/`), orchestration in `engine/`.
* Small, composable “systems” that run in an ordered turn pipeline.
* Data-driven where it helps (JSON), Python where logic matters.
* Early i18n, early logging, early tests.

## Domain model (v0, minimal)

### Entities (core/)

* `World`: size, seed, calendar/time, ruleset refs.
* `Tile`: terrain, biome, fertility, water, elevation, flags.
* `Region`: named collections of tiles (political/biome).
* `Node`: towns, shrines, agencies, waypoints (ID, coords, capacity).
* `Edge`: roads/rivers/trails between nodes; cost, throughput, condition.
* `Faction`: culture, ethics, relations, resources, tech level.
* `Actor`: player/NPC; stats, inventory, location, intents.
* `Resource`: grain, livestock, metals, energy; units + quality grade.
* `Event`: atomic world change (facts, deltas).
* `StoryFlag`: canonical lore state toggles (for scripting).

Keep entities small; attach behavior via **systems** rather than methods where possible.

### Map model

* **Grid**: orthogonal or hex (choose early; hex recommended for travel cost).
* **Layers**: terrain, elevation, moisture, ownership, visibility/FoW.
* **Overlays**:

  * Graphs: `transport_graph` (cyclic), `trade_graph`, `communication_graph`.
  * DAGs: `agency_influence_dag` (for extra-terrestrial/Enclosure causal chains).
* **Addressing**: `q,r` for hex (or `x,y`); never mix pixel coords into domain.
* **Chunking**: simple chunks (e.g., 64×64) to bound operations and paging.

### Turn pipeline (engine/turns.py)

Ordered, explicit phases—each phase consumes/produces events:

1. **Input/Intent** (collect player + AI intents)
2. **Validation/Rules** (resolve conflicts, legality)
3. **World Sim**

   * ecology → agriculture → population → logistics → economy → politics
4. **Story/Script** (evaluate triggers, dispatch scripted beats)
5. **Apply/Commit** (reduce events to new state; single commit)
6. **Visibility** (compute FoW, notifications)
7. **Persistence snapshot** (autosave/rollback point)
8. **Output** (messages to UI)

Each phase is a pluggable system with a stable interface.

### Systems (engine/systems/\*)

* `EcologySystem` (pollinators, fertility, climate drift)
* `AgricultureSystem` (yields, famine risk)
* `PopulationSystem` (growth/migration, labor allocation)
* `LogisticsSystem` (edge flows, capacity, decay)
* `EconomySystem` (prices, barter indices, scarcity)
* `PoliticsSystem` (factions, legitimacy, coercion/consent)
* `AgencySystem` (DAG propagation, interventions)
* `StorySystem` (triggers, consequences, flag mutations)
* `VisibilitySystem` (FoW, intel diffusion)

Each takes `(state, rng, params) -> events`.

### Scripting & story hooks

**Goals:** data-first for triggers, Python callbacks for consequences.

* **Event specs**: JSON with fields: `id`, `when` (trigger), `where` (scope), `requires` (StoryFlags), `weight`, `effects` (named actions + parameters).
* **Trigger language (simple)**: predicates on world state (e.g., `tile.biome == "steppe" AND region.famine_index > 0.7`).
* **Action registry**: Python functions registered under string keys, e.g., `"spawn_refugees"`, `"set_story_flag"`, `"modify_price_index"`.
* **Namespaces**: keep Saskan-lore canon in `data/story/` with IDs; never hard-code lore text in systems.
* **Localization**: story text stored as message IDs; render via i18n layer.

### Persistence (infra/persistence)

* **SQLite + SQLAlchemy ORM** for long-lived entities.
* **JSON sidecars** for static configs, maps, story packs.
* **Versioning**: `schema_version` table + optional Alembic later.
* **Save/Load**: snapshot world state per turn (lightweight: store deltas or seed+event log); retain last N checkpoints.

### Messaging (client/server)

**Transport:** Python sockets (TCP), JSON messages, newline-delimited or length-prefixed.

**Envelope (always):**

```json
{ "id": "<uuid>", "type": "<command|event|reply|error>", "name": "<verb>", "payload": {...}, "ts": "<iso8601>" }
```

**Core commands (v0):**

* `new_game`, `load_game`, `save_game`
* `get_world_summary`, `get_region`, `get_tile`, `get_node`
* `submit_intents` (list of player intents)
* `advance_turn` (server runs pipeline; returns summary + notifications)

**Events out:**

* `turn_summary`, `story_event`, `world_change`, `notification`

**Error contract:** explicit `code`, `message`, `details` (no stack traces across the wire).

### Data & configuration

* `data/config/`: tunables per system (JSON).
* `data/maps/`: seeds, generated maps, imported heightmaps.
* `data/story/`: story packs (triggers, actions, localized strings).
* `data/locales/`: `en/LC_MESSAGES/*.po` (or a light string table for MVP).
* `data/schemas/`: JSON Schemas for validation (configs, story, intents, messages).

### Testing & quality

* **Unit**: systems are pure → easy to test with fixed seeds.
* **Property tests**: invariants (no negative population, conserved flows).
* **Golden files**: turn summaries snapshots for regression.
* **Integration**: end-to-end turn with tiny map.
* **Perf sanity**: budget per phase; fail CI if phase > threshold.

Tooling: `pytest`, `tox`, `pre-commit` (black, ruff, isort, mypy basic), `hypothesis` for property tests.

### Logging & telemetry

* Structured logs (JSON). Levels: `TRACE` (dev), `INFO` (turn summaries), `WARN/ERROR`.
* Per-turn log bundle: seed, params hash, duration per phase, event counts.

### Internationalization

* Wrap all UI/notifications in message IDs from day one.
* Use gettext or a minimal key→string table; store lore text out of code.
* Keep date/number formats locale-aware (even if English-only initially).

### Mathematical tooling

* `numpy`/`pandas` only inside `sims/` modules.
* Keep boundaries: sims accept/return plain Python structures (or dataclasses), not DataFrames, to avoid leaking into domain.

### Build & env

* `poetry` for deps.
* Dev scripts: `make dev`, `make test`, `make run-server`, `make run-cli`.
* `.env` for tunables; config layering: defaults → file → env.

#### MVP milestones (practical sequence)

##### M0 – Skeleton & CLI (1–2 days of focused work)

* Project layout, config loader, logging.
* Deterministic world generator (tiny hex map), minimal entities.
* Turn pipeline scaffold with 2–3 trivial systems.
* CLI: `new`, `inspect`, `tick`.

##### M1 – Persistence & Graphs

* SQLite models for `World/Tile/Node/Edge/Faction`.
* Transport graph + basic path cost; save/load.
* JSON schema validation for configs/story.

##### M2 – Story hooks

* Trigger evaluation engine + action registry.
* A small story pack tied to your existing lore (3–5 events).
* Notifications surfaced in CLI.

##### M3 – Simulation pass

* Ecology→Agriculture→Population minimal loop (famine risk shows up).
* Turn summaries + regression tests.

##### M4 – UI split

* Client/server over sockets (local).
* PySide stub menus; PyGame map viewer (static render first).

## Risks to watch early

* **Scope creep** in story engine—start with a tiny predicate language.
* **Bleeding concerns** between UI and engine—enforce the boundaries.
* **Data validity**—introduce JSON Schema validation early.
* **Performance traps**—don’t let pandas leak into the core.

## Decisions - ADRS

* Hex vs orthogonal grid (recommend hex).
* Save format: event-log + seed vs full snapshots (start with snapshots; add event-log later).
* Trigger language: custom mini-DSL vs JSON predicates (start with JSON predicates).
* CLI parser: `argparse` vs `typer` (typer is nicer, still simple).

### ADR set = Architecture Decision Records

Short, dated notes that capture a decision, its context, options considered, and consequences. One ADR per decision; stored in-repo (e.g., `docs/adr/0001-hex-grid.md`). They prevent “why did we choose X?” amnesia.

#### Hex grid: what to lock down

* **Coordinate system**: use **axial (q, r)** for logic, **odd-r** or **even-r** offsets only at UI edges. Keep pixel math isolated.
* **Neighbor deltas (axial)**: the six neighbors are fixed vectors; make a constant table and never recompute.
* **Distance**: use axial→cube conversion under the hood (Manhattan in cube space / 2). Expose a single `hex_distance(a, b)` function.
* **Rings & ranges**: build on the neighbor deltas + distance; these power AoE, visibility, and region growth.
* **Chunking**: decide a chunk size (e.g., 64×64 axial window) for paging and perf.
* **Projection**: pick **pointy-top** or **flat-top** now (affects axial↔pixel formulas and neighbor layout). For Civ-like maps, **pointy-top** is common.

##### Minimal geometry surface (no code, just contracts)

* `axial -> cube` and `cube -> axial`
* `neighbors(hex) -> [hex×6]`
* `distance(a, b) -> int`
* `line(a, b) -> [hex…]` (for LoS/path preview; uses hex lerp + rounding)
* `ring(center, radius) -> [hex…]`
* `range(center, radius) -> [hex…]`
* `axial <-> pixel` (isolated in a renderer helper)
* `wrap_policy` (none / horizontal / both): defines how coords normalize at edges.

### Snapshots: format & lifecycle

* **Granularity**: one JSON (or msgpack) per turn: `header` + `state` + `meta`.
* **Header**: game id, turn number, schema version, RNG seed, ruleset hash.
* **State**: world dims, tiles (chunked), nodes/edges/factions/actors, story flags, visibility layers.
* **Meta**: timings, event counts, provenance (git commit), notes.
* **Retention**: rolling window (e.g., last 20 turns) + manual “milestones”.
* **Integrity**: include a hash of `state` and ruleset; validate on load.

### Triggers as JSON predicates

* **Shape**:

  * `when`: predicate over state (boolean)
  * `scope`: selector (tiles/regions/nodes) reducing evaluation set
  * `requires`: story flags / once-only guards
  * `weight`: selection bias when multiple fire
  * `effects`: list of named actions with parameters
* **Predicate ops** (keep small): `and/or/not`, comparisons, `in`, numeric ranges, distance, counts/aggregates over a scope.
* **Evaluation cycle**: determine candidate scopes → evaluate `when` → resolve conflicts (priority/weight) → enqueue effects → commit at end of turn.
* **Observability**: log which predicates fired with inputs/outputs for debugging.

### Typer: usage model (no code, just design)

* **CLI shape**:

  * `saskan new [--seed …]`
  * `saskan load <save>`
  * `saskan tick [--steps N] [--verbose]`
  * `saskan inspect tile <q> <r> | node <id> | region <id>`
  * `saskan plan <intent-json|path>`
  * `saskan commit` (advance with queued intents)
  * `saskan story test <event-id>` (dry-run a trigger)
* **Conventions**:

  * Commands map 1:1 to client API calls.
  * Rich help strings and examples; Typer gives you subcommand help for free.
  * Validation: fail fast on bad args; point users to `saskan … --help`.
  * Output modes: `--format table|json`; JSON is machine-friendly for scripting.
* **Testing**: exercise commands through Typer’s testing helpers (later), but design commands to be thin wrappers around pure functions.

## Guardrails to keep it clean

* One module owns hex math; everyone else calls it.
* One module owns RNG; seeded per turn; passed, not imported globally.
* Systems return events; only the commit phase mutates world state.
* JSON schemas for: snapshots, triggers, config, intents, and messages.
* Lint/type checks in pre-commit; property tests for invariants (no negative populations, conserved flows, acyclic agency DAG, etc.).

## Open choices to settle next

* **World wrap** (torus vs none) for movement and distance semantics.
* **Height/moisture model** inputs (procedural vs imported raster) to seed ecology.
* **Notification taxonomy** (player-facing categories + i18n message IDs).

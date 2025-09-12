# High-Level Architecture

## Layered Structure

- **Core Game Logic:** Handles rules, entities, and world simulation.
- **Persistence:** Utilizes SQLite with SQLAlchemy ORM for data storage.
- **Presentation:** PySide for UI menus and PyGame for the game canvas and loop. This separation allows easy swapping or expansion of layers.

## Client/Server Model

- Start with a lightweight server running locally alongside the client.
- Use plain JSON over sockets for messaging, allowing easy debugging and future protocol upgrades.

## Tooling and Scaffolding

- Use **Poetry** and **tox** for packaging and testing.
- Implement core entities using **SQLAlchemy models**.
- Introduce **Alembic** for schema migrations when necessary.
- Establish early logging practices to simplify debugging.

## Data Handling

- **Relational DB (SQLite):** For persistent entities and history.
- **JSON Files:** Store configurations, maps, and event probabilities.
- **Numpy/Pandas:** For simulations, wrapped in service modules for scalability.

## UI/UX Strategy

- **PySide:** Manages menus, dialogs, and settings.
- **PyGame:** Focuses on the game loop and rendering, minimizing overlap with UI components.
- Implement internationalization early using gettext or a string-table class.

### CLI First Approach

- Commands: `new`, `tick`, `inspect <tile|node|region>`, `plan <intent>`, `commit`, `log`.
- Output: Compact tables and JSON dumps for debugging.
- Input: Stateless REPL with history.

### Later UI Development

- PySide handles menus and dialogs.
- PyGame manages the render surface and map input.
- UI communicates only through the client API.

## Development Approach

- Begin with "toy loops" to simulate basic scenarios.
- Define world entities and ORM models early.
- Modularize prototypes for easy integration or removal.

## High-Level Structure

```text
saskan/
  core/                # Game domain logic
  data/                # Configurations and seed content
  engine/              # Turn loop and systems
  infra/               # Persistence, messaging, logging
  ui_cli/              # Initial CLI tools
  ui_pyside/           # Menus and dialogs
  ui_pygame/           # Canvas and event loop
  sims/                # Simulators for ecology, population, economy
  tools/               # Utilities and importers/exporters
  tests/
```

## Core Principles

- Keep the domain logic pure and side-effect free.
- Place IO operations at the edges and orchestrate in the engine.
- Use small, composable systems in an ordered turn pipeline.
- Favor data-driven designs where beneficial, using Python for complex logic.
- Prioritize early implementation of internationalization, logging, and testing.

## Domain Model (v0)

### Entities

- **World:** Size, seed, calendar, ruleset references.
- **Tile:** Terrain, biome, fertility, water, elevation.
- **Region:** Collections of tiles.
- **Node:** Towns, shrines, waypoints.
- **Edge:** Roads and trails between nodes.
- **Faction:** Culture, ethics, resources.
- **Actor:** Player/NPC attributes and inventory.
- **Resource:** Types and quality grades.
- **Event:** Atomic world changes.
- **StoryFlag:** Lore state toggles.

Entities should remain small, with behavior attached via systems.

### Map Model

- **Grid:** Choose hex for travel cost.
- **Layers:** Terrain, elevation, ownership, visibility.
- **Overlays:** Graphs and DAGs for transport and influence.

### Turn Pipeline

1. **Input/Intent:** Collect player and AI intents.
2. **Validation/Rules:** Resolve conflicts.
3. **World Simulation:** Ecology, agriculture, politics.
4. **Story/Script:** Evaluate triggers.
5. **Apply/Commit:** Update state.
6. **Visibility:** Compute FoW.
7. **Persistence Snapshot:** Autosave.
8. **Output:** Communicate with UI.

Each phase is a pluggable system.

### Systems

- **EcologySystem:** Fertility and climate drift.
- **AgricultureSystem:** Yields and famine risk.
- **PopulationSystem:** Growth and labor allocation.
- **LogisticsSystem:** Edge flows and decay.
- **EconomySystem:** Prices and scarcity.
- **PoliticsSystem:** Faction dynamics.
- **AgencySystem:** Propagation and interventions.
- **StorySystem:** Trigger evaluation.
- **VisibilitySystem:** Intel diffusion.

### Scripting & Story Hooks

- **Event Specs:** JSON format with triggers and effects.
- **Trigger Language:** Simple predicates on world state.
- **Action Registry:** Python functions for consequences.
- **Namespaces:** Keep lore in `data/story/`.

### Persistence

- **SQLite + SQLAlchemy ORM:** For long-lived entities.
- **JSON Sidecars:** For static configs and story packs.
- **Versioning:** Schema version table with optional Alembic.
- **Save/Load:** Snapshot world state per turn.

### Messaging

- **Transport:** Python sockets with JSON messages.
- **Envelope:**

  ```json
  { "id": "<uuid>", "type": "<command|event|reply|error>", "name": "<verb>", "payload": {...}, "ts": "<iso8601>" }
  ```

- **Core Commands:** `new_game`, `load_game`, `save_game`, etc.
- **Events Out:** `turn_summary`, `story_event`, etc.

### Data & Configuration

- **Config Directory:** Tunables per system.
- **Maps Directory:** Seeds and generated maps.
- **Story Directory:** Triggers and actions.
- **Locales Directory:** Localization files.
- **Schemas Directory:** JSON Schemas for validation.

### Testing & Quality

- **Unit Tests:** Pure systems are easy to test.
- **Property Tests:** Invariants like conserved flows.
- **Golden Files:** Regression snapshots.
- **Integration Tests:** End-to-end turns.
- **Performance Sanity:** Phase budgets.

Tooling includes `pytest`, `tox`, and `pre-commit` hooks.

### Logging & Telemetry

- Structured logs in JSON format.
- Per-turn log bundle with event counts and timings.

### Internationalization

- Wrap UI strings in message IDs.
- Use gettext or a string table for localization.

### Mathematical Tooling

- Use `numpy`/`pandas` within `sims/` modules.
- Maintain boundaries by returning plain Python structures.

### Build & Environment

- Use `poetry` for dependencies.
- Dev scripts for common tasks.
- `.env` for configuration layering.

#### MVP Milestones

1. **M0 – Skeleton & CLI:** Basic project setup and CLI commands.
2. **M1 – Persistence & Graphs:** SQLite models and transport graph.
3. **M2 – Story Hooks:** Trigger evaluation and action registry.
4. **M3 – Simulation Pass:** Minimal ecology and agriculture loop.
5. **M4 – UI Split:** Local client/server and initial UI stubs.

## Risks to Watch

- Avoid scope creep in the story engine.
- Enforce boundaries between UI and engine.
- Introduce JSON Schema validation early.
- Prevent performance issues by containing pandas usage.

## Decisions - ADRs

- Hex grid vs orthogonal grid.
- Save format: snapshots vs event-log.
- Trigger language: JSON predicates.
- CLI parser: `argparse` vs `typer`.

### Architecture Decision Records (ADRs)

Store decisions with context and options considered in `docs/adr/`.

#### Hex Grid Considerations

- **Coordinate System:** Use axial coordinates.
- **Neighbor Deltas:** Fixed vectors in a constant table.
- **Distance Calculation:** Axial to cube conversion.
- **Chunking:** Decide chunk size for paging.
- **Projection:** Choose pointy-top or flat-top layout.

##### Minimal Geometry Surface

- Functions for coordinate conversions and distance calculations.

### Snapshots: Format & Lifecycle

- **Granularity:** One JSON per turn.
- **Header:** Game metadata.
- **State:** World dimensions and entities.
- **Meta:** Timings and provenance.
- **Retention:** Rolling window of turns.
- **Integrity:** Include a hash for validation.

### Triggers as JSON Predicates

- **Shape:** Predicate structure with effects.
- **Predicate Ops:** Basic logical operations.
- **Evaluation Cycle:** Determine scopes and evaluate predicates.
- **Observability:** Log predicate activity.

### Typer Usage Model

- **CLI Shape:** Commands map to client API calls.
- **Conventions:** Rich help strings and examples.
- **Testing:** Use Typer’s helpers for command testing.

## Guardrails

- Centralize hex math and RNG management.
- Systems return events; only commit phase mutates state.
- Use JSON schemas for validation.
- Lint/type checks and property tests ensure code quality.

## Open Choices

- Decide on world wrap semantics.
- Choose inputs for height/moisture models.
- Develop a notification taxonomy.

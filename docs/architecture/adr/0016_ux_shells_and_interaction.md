# ADR-0016 UX Shells and Interactions (CLI, PyGame, PySide)

/docs/ references:

- architecture/architecture_summary.md
- architecture/client_server_game.md
- architecture/project_structure.md
- reference/glossary/IPC.md
- reference/glossary/HUD.md

---

- **Date:*- 2025-09-08
- **Status:*- Accepted

## Context

We will ship three UX “shells” that interact with the same client–server core: a **CLI*- for fast iteration, a **PyGame*- canvas for map rendering & input, and **PySide*- widgets for menus, dialogs, and settings. These must remain loosely coupled, speak the same message contracts, and evolve from a simple, single-process prototype to richer, multi-process UX without architectural churn. Prior notes already emphasize a layered structure, CLI-first workflow, and clean separation of PyGame (canvas/loop) and PySide (widgets) with JSON-over-sockets messaging. &#x20;

## Decision

Adopt a **multi-shell UX architecture*- with strict boundaries:

1. **CLI*- is the thin, canonical driver for developer flows and automated tests. It only calls the client API (request–reply), never engine internals. Output supports table/JSON formats. &#x20;
2. **PyGame*- owns the **render surface + map input**, consuming read-only state and producing user intents. All hex→pixel math lives in the renderer helper; axial/cube math stays in `core`. No state ownership.&#x20;
3. **PySide*- owns **menus, dialogs, settings, i18n surfaces**. It never runs the sim loop. It issues commands and displays summaries/logs. &#x20;
4. **Integration path*- proceeds in stages:

   - Stage A: **One shell at a time*- (CLI or PyGame or PySide) driving the same server.
   - Stage B: **Side-by-side shells*- via simple IPC (JSON over local socket) if both PySide and PyGame must appear together.
   - Stage C: Optional embedding of PyGame inside a PySide widget, reusing the same message schema internally. &#x20;

## Architectural Principles

- **Functional core, imperative shell.*- UI never mutates game state directly; all mutations go through commands → events → commit.&#x20;
- **Single source of truth.*- The server (engine) is authoritative; shells are projections.
- **Message contracts at the seams.*- All shells speak the same envelope & payload shapes; enums (e.g., notification `topic`) follow the taxonomy. (See ADR-0011/0008.)&#x20;
- **Ports & Adapters mindset.*- UI shells are adapters; swapping one doesn’t ripple into engine/core/infra.&#x20;
- **Determinism & testability first.*- The CLI path is the reference execution for headless CI and golden-file regression.&#x20;

## Roles & Responsibilities (per shell)

### CLI

- **Role:*- Developer UX, automation, diagnostics.
- **Responsibilities:*- Handshake; send commands (`new`, `tick`, `inspect`); render concise output.
- **MVP use cases:*- bootstrap world; advance turns; inspect tiles/nodes; dry-run story events.&#x20;
- **Do not:*- contain business logic or access engine internals.&#x20;

### PyGame

- **Role:*- High-performance canvas for the hex map & HUD overlays.
- **Responsibilities:*- Render snapshots; process map input; highlight rings/paths; show per-turn diffs.&#x20;
- **Do not:*- duplicate hex math from `core`; own authoritative state; run turn loop.&#x20;

### PySide

- **Role:*- Desktop shell for menus, settings, dialogs, logs, i18n.
- **Responsibilities:*- Session controls (new/load/save), settings UI, modal flows, status panels.
- **Do not:*- embed sim loop; reimplement canvas logic; bleed UI types into engine.&#x20;

## Interaction Patterns

### A. Single-shell flows (simple)

- **CLI-only:*- `handshake → new_game/load → tick/inspect → notifications/log`. Baseline for testing.&#x20;
- **PyGame-only:*- `handshake → welcome snapshot → render → input→intents → advance_turn`.
- **PySide-only:*- `handshake → menu actions → dialogs → summaries`.

### B. Dual-shell flows (moderate)

- **PySide host + PyGame child*- using **JSON-over-local-socket IPC**:

  - PySide sends “presentation” commands (e.g., `load_map`, `focus_region`).
  - PyGame emits UI events (e.g., `unit_selected`) back to PySide.
  - Both talk to the game server independently for their needs or proxy via PySide.&#x20;

### C. Embedded flow (advanced)

- Embed PyGame as a widget **only after*- B is stable; reuse the same message schema internally so migration is mechanical.&#x20;

## Integration Guidelines

- **One event loop per process.*- Keep PyGame and PySide loops separate unless/until you choose embedding; use IPC to coordinate.&#x20;
- **Thin clients.*- All shells use the client API; no shell imports `engine` or `core` directly.&#x20;
- **Renderer purity.*- PyGame renderer consumes immutable snapshots and deltas; no DB or network inside render loops.&#x20;
- **i18n early.*- All user strings surfaced via message IDs; PySide is the primary i18n surface; CLI mirrors IDs in logs where helpful.&#x20;
- **Asset handling.*- Images/audio are referenced via manifest/URLs; shells load appropriate variants (cache-busted) per ADR-0015; “first splash” follows this.&#x20;
- **Observability.*- Each shell prefixes logs (`[CLI]`, `[PG]`, `[QT]`) and includes correlation IDs from the message envelope. (Consistent with earlier logging guidance.)&#x20;

## Evolution Path (simple → complex)

1. **MVP (Single shell):*- CLI drives server; optional PyGame *or- PySide demo (“First Splash”).&#x20;
2. **Dual shell (Side-by-side):*- PySide + PyGame via local socket IPC; keep message schemas identical to network envelopes.&#x20;
3. **Embedded canvas:*- PyGame embedded in PySide; maintain separation of concerns (renderer vs menus) even within one process.&#x20;
4. **Multiplayer polish:*- Same shells, but client registry & subscriptions support multiple active clients; UX filters events by topic/category.&#x20;

## Anti-Patterns to Avoid

- **UI/engine coupling:*- shells importing `engine`/`core` internals or mutating state directly.&#x20;
- **Geometry duplication:*- re-implementing hex math in PyGame instead of calling the shared helper.&#x20;
- **Two event loops in one process without IPC discipline:*- tangled threads/callbacks; prefer clear IPC or explicit embedding plan.&#x20;
- **Asset bytes in messages:*- violates ADR-0015; always pass URLs + metadata.&#x20;

## Notes / Follow-ups

- Provide a **renderer selector*- in UX (“`--ui=cli|pygame|pyside`”) that picks exactly one for a run; dual-shell mode requires explicit `--with-ipc`.&#x20;
- Document **capability hints*- (e.g., `image_max`, `wants_notifications`) in handshake/welcome so shells self-tune.&#x20;
- Keep **project tree*- alignment: `ui_cli/`, `ui_pygame/`, `ui_pyside/` with clear subpackages (`render/`, `views/`, etc.).&#x20;

---

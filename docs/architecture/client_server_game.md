# Summary: Client/Server Architecture

## PyGame + PySide Integration

- **PyGame:** Core engine for maps, rendering, input, and complex HUD.
- **PySide:** Adds widgets like menus and logs without reinventing them in PyGame.

### Considerations

- Use PyGame as the main canvas with PySide as dockable panels or embed PyGame in a PySide widget for a unified UI.
- Ideal for building tools like data browsers, world editors, and debugging panels.

## Database Layer

- **SQLite (Development):** Suitable for testing and potential client-side storage.
- **Postgres (Production):** Offers richer features and consistent migration paths.
- **SQLAlchemy:** Abstracts database differences, ensuring seamless transitions.

### Role of the Database

- Holds authoritative world state, enabling full campaign persistence, debugging, and hot-reloading.

## Multiplayer Architecture

- Avoid large HTTP stacks; use a simple message server with local engines for each client.

### Implementation Strategy

- Each client operates its own local engine (PyGame/PySide + SQLite).
- A lightweight messaging server coordinates player actions:
  - Handles move data and broadcasts events.
  - Options include Python’s asyncio/socketserver or ZeroMQ.

### Benefits

- Deterministic local game logic with networking for synchronizing deltas.
- Parallel development of single-player and multiplayer modes.
- Background jobs simulate unseen world parts.
- Dev tools can query and visualize the world independently.

### Testing Approach

- Run server and clients on separate ports/processes on a single machine.
- Utilize Python's socketserver, asyncio, or multiprocessing for mock testing.

### Networking Tools

- **asyncio:** Native, handles chat and signals.
- **ZeroMQ:** Simple, effective for pub/sub patterns.
- **Twisted:** Robust but heavier option.

### Mock Testing

- Use multiple processes on localhost to simulate clients.
- Employ SQLite for client-side databases, periodically dumped for debugging.

### Starting Point: socketserver

- **Advantages:** No external dependencies, easy setup, transition to asyncio possible without major changes.

## Minimum Viable Product (MVP)

1. **Prototype Message Server:**
   - Implement basic message echo functionality between clients.

2. **Define Delta Format:**
   - Establish minimal data requirements for world state synchronization using JSON packets initially.

3. **Turn-Handling Logic:**
   - Decide on synchronous or asynchronous turn advancement based on player actions.

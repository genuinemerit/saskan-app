# Summary, Snippets, Notes on Client/Server and architecture

## PyGame + PySide

- PyGame: For the core engine (maps, rendering, input, more complex HUD).

- PySide: Layer in widgets (menus, inspectors, logs) without having to re-invent everything in PyGame.

Maybe: keep PyGame as "main canvas" and run PySide in a parent window or as dockable panels.

Maybe: embed the PyGame surface in a PySide widget if we want a single window UI.

👉 For a tools-heavy game like Saskan Lands, we can build proper data browsers, world editors, and debugging panels.

## Database Layer (SQLAlchemy, SQLite, Postres)

- SQLite in dev: perfect for testing. May also be suitable for client-side storage.

- Postgres in production: consistent migration path, richer features for multiplayer, though that may not be a concern if we have good separation.

- SQLAlchemy abstracts away 99% of the differences. See prototyping in previous projects: mint/app/models.py

- The DB holds the authoritative world state.  We can persist full campaigns this way, which should make debugging and hot-reloading easier.

## Multiplayer Architecture

We don’t need Flask or a big HTTP stack. A simple message server and local engines for each client works for this style of game.

### How It Could Work

- Each client runs its own local engine (PyGame/PySide + SQLite).
- A lightweight messaging server coordinates players:
  - Receives move data (turn submissions).
  - Broadcasts events, game state deltas, and chat.
  - Could be Python’s asyncio/socketserver or ZeroMQ.

Clients update their local DB based on the messages received.

👉 The beauty: most game logic stays deterministic and local, and networking is only about synchronizing deltas.

- Avoid web frameworks and keep all control over game state.
- Easier to develop single-player and multiplayer in parallel:
  - Single-player = just don’t spin up the message server. (?) 
  - Multiplayer = attach to the server, apply deltas.
- Run background jobs to simulate parts of the world players aren’t looking at.
- Build dev tools that query and visualize the world without touching the game engine.

### Mocking this up with ports

We can easily test this by having a single machine run the "server" on one port and each client on its own port (or separate processes).

Python’s socketserver, asyncio, or even multiprocessing.connection.Listener and Client are perfect for mocking.

### Possible tooling

#### Networking:

- asyncio (native, can handle chat + signals)
- ZeroMQ (very simple, great for pub/sub and request/response patterns)
- Twisted (if you want robust networking but it’s heavier)

Mock testing:

- Run N clients as separate processes on localhost, each connecting to the server on a different port.
- SQLite DB per client, periodically dumped for debugging.

Start Simple: socketserver

- What it is: A part of Python's standard library designed for simple TCP or UDP servers.

Why it’s great:

- No external dependencies.
- Dead simple to start a server and accept messages.
- Can switch to asyncio later without rewriting the game logic.

See: docs/skunkworks/socketserver.md

### Minimum Viable Product

- Prototype the message server:

  - Send a "move submitted" message from one client and echo it to the others.

- Define the delta format:

  - What minimal data do you need to synchronize world state?
  - Can be JSON packets at first, then optimize later.

- Build turn-handling logic in the server:

  - Does the server wait for all players before advancing? Or can it handle simultaneous actions?




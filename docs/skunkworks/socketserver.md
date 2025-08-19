# socketserver

## Overview

Saskantinon Game Architecture – Early Dev Summary
Core Philosophy

Server is the only source of truth – owns & writes the world state (DB).

Clients are dumb but pretty – render what the server tells them and send actions.

Messages stay lightweight – actions up, deltas down.

1. Server

Maintains the authoritative world DB (SQLite early, Postgres later).

Processes all player actions: move, chat, combat, etc.

Updates DB, then sends delta messages (changes) to all connected clients.

2. Clients

Maintain an in-memory cache of relevant world data.

Render GUI (maps, units, menus) using the cache.

Send actions to the server; never write to the DB.

Apply deltas from the server to keep cache up-to-date.

3. Message Flow

Action → Server

{"type": "action", "player_id": "A", "move": "travel", "target": "Byenung"}


Delta → Clients

{"type": "delta", "changes": [
    {"table": "units", "id": "U123", "field": "location", "new": "Byenung"}
]}


Chat & Broadcast

{"type": "chat", "to": "B", "message": "Hello!"}
{"type": "broadcast", "message": "Storm in the Eastern Provinces"}

4. Early Dev Setup

Run the server in one terminal (socketserver or asyncio).

Run multiple CLI clients (one per terminal).

Send actions and watch deltas flow before adding GUI.

5. Avoid Rabbit Holes

No RabbitMQ, Celery, or DB replication until it hurts.

Only add complexity when existing architecture fails under real load.

6. Future Enhancements (Only If Needed)

DB replication: Clients maintain read-only SQLite copies if deltas become too big.

Chunking: Only send data for the player’s visible region.

Event log: Switch to event sourcing if debugging desyncs becomes hard.

## Sample skeleton

```python
import socketserver

class GameRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        print(f"[SERVER] Received: {data.decode()}")
        # Echo back to client for now
        self.request.sendall(data.upper())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.TCPServer((HOST, PORT), GameRequestHandler) as server:
        print(f"Server running on {HOST}:{PORT}")
        server.serve_forever()
```

## Client

```python
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(("localhost", 9999))
    sock.sendall(b"Hello Game Server")
    response = sock.recv(1024)
    print(f"[CLIENT] Got: {response.decode()}")
```

## Multi-Client Support

Keep each client alive (e.g., chat, notifications) without blocking other players.

```python
with socketserver.ThreadingTCPServer((HOST, PORT), GameRequestHandler) as server:
    server.serve_forever()
```

Keep track of all connections

Have everyone’s connection handle, so server can target individuals or broadcast.

```python
clients = {}  # {player_id: socket}

class GameRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        player_id = self.register_client()
        try:
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                self.process_message(player_id, data)
        finally:
            self.unregister_client(player_id)
```

## Message Formats and Types

- Start with simple JSON packets
- Evolve into more structured protocols later.
- JSON is human-readable → makes debugging easy.

```python
{"type": "move", "player_id": 1, "move": "ATTACK", "target": "Byenung"}

{"type": "chat", "to": "playerB", "message": "Hello!"}

{"type": "broadcast", "message": "Torrential downpour in the eastern provinces"}

{"type": "action", "player_id": "A", "move": "attack", "target": "NPC-23"}
```

## Processing Messages

```python
def process_message(self, player_id, data):
    message = json.loads(data.decode())
    msg_type = message["type"]

    if msg_type == "chat":
        target_id = message["to"]
        clients[target_id].sendall(data)

    elif msg_type == "broadcast":
        for pid, sock in clients.items():
            if pid != player_id:  # optionally skip sender
                sock.sendall(data)

    elif msg_type == "action":
        # Game logic, update DB, notify affected players
        self.handle_action(message)
```

Examples:

- Direct chat (peer-to-peer): Player A sends a chat message with to: PlayerB → server relays only to B.

- Travel/fight with another player: Same pattern. Player A sends an action with the target player.

- Broadcast: Any player (or the server itself) sends a broadcast message, and the server pushes it to everyone.

- Scheduled broadcasts (like the “union-mandated break” or weather event) using a simple timer thread on the server.

## Incremental Roadmap

1. Echo server: Get clients talking to server.

2. Broadcast: Server sends a message from one client to all others.

3. Game logic: Server becomes the arbiter of turn progression and state deltas.

4. SQLite: Store world state and sync only the changes.

At this point, we’ll have enough of a foundation that swapping in asyncio or ZeroMQ (if we want pub/sub style) is straightforward.

Scaling up:

- Start small: single-threaded broadcast and peer-to-peer works fine for 2–10 players.

- Upgrade to ThreadingTCPServer or asyncio only if you need bigger concurrency.

- This pattern makes it easy to evolve into “rooms” or “zones” (eastern provinces, battlefields, etc.) where only relevant players get the broadcast.

- Log all messages and world state changes to SQLite.

- Replay turns or debug desyncs easily.

- Swap the CLI for PyGame or PySide UI but keep the same messaging backbone.

## Start with CLI

1. Low overhead:

- You don’t have to mess with PyGame/PySide yet.
- Just run a while True: loop, prompt for input, send/receive messages.

2. Clear visibility:

- Each terminal window is a “player view.”

- The server window shows what’s being received and broadcast.
- Easier to debug than building a GUI too early.

3. Rapid iteration:

- Change message formats, add message types, and test instantly.
- No need to worry about the engine UI until the messaging is solid.

## Data Management

- Server: owns the DB (SQLite now, Postgres later).
- Clients: stateless (just caches data from server).
- All data changes flow through the server → DB → broadcast to clients.
- This gets us 100% deterministic world state with the smallest complexity.

Example DB flow:

1. Player A sends:

```json
{"type": "action", "player_id": "A", "move": "travel", "target": "Byenung"}

```

2. Server applies move → updates DB.

3. Server sends delta:

```json
{"type": "delta", "changes": [
    {"table": "player_location", "id": "A", "new": "Byenung"}
]}
```

4. All clients update their local view.

## Client UI handling

1. Initial load. On connect, client requests current snapshot.

```json
{"type": "get_world"}
```

Client sends full state: world map, positions, resources, etc.

2. Incremental updates

Every time something changes, server sends a delta:

```json
{"type": "delta", "changes": [
    {"table": "units", "id": "U123", "field": "location", "new": "Byenung"}
]}
```

Client updates its local cache and re-renders the affected elements.

Rendering:

GUI (PyGame, PySide) reads from the local cache (dicts, arrays, etc.).

It doesn’t talk to the DB or make assumptions about other players’ states.

Build the client without any graphics at first (just CLI):

Receive deltas → print to terminal.

Send actions → type into prompt.

Once messaging is solid, swap the terminal printouts for PyGame rendering.

The local rendering is entirely driven by server messages, not by a client-owned DB.
That’s the foundation. If later we add offline or single-player mode, we can run the server + DB inside the client, but the architecture doesn’t change.

## Client DB Read-only Model

Option: clients can read from the DB (or a read-only replica) to avoid bloated message packets. But there’s a balance to strike:

1. Hybrid Model: Messages + Read Access

Server: Still the only one that can write/modify the DB.

Clients: Can read the DB for large or static data, but rely on lightweight messages for real-time updates.

Why This Works

Avoids sending massive JSON blobs for world state over and over.

Clients can query world data on-demand (e.g., map tiles, unit metadata).

Server only sends keys, IDs, or delta hints instead of full datasets.

2. Example Flow

Server sends minimal update:

{"type": "delta", "update": {"tile_id": 42, "status": "flooded"}}


Client queries DB (read-only):

SELECT * FROM map_tiles WHERE id=42;


Client re-renders tile 42 using local data:

Reads everything it needs (terrain, resources, owner, visuals) from DB.

3. How Clients Access the DB
Option A: Local Copy (Replica)

Each client maintains a read-only SQLite copy of the world DB.

Server sends deltas and clients apply those changes locally.

Best for offline play and minimal bandwidth.

Cons:

You reintroduce some syncing complexity. (Still easier than full distributed writes!)

Option B: Direct Read Access to Central DB

Clients can query the server’s DB directly (read-only credentials).

Messages from the server include the keys/IDs they should query.

Cons:

Requires secure DB connections for every client.

Can create latency spikes if clients are hammering the DB for many reads.

4. Smart Middle Ground (Recommended for You)

Cache-heavy clients:

Clients hold an in-memory cache of frequently accessed data (map, metadata).

Server sends only IDs + deltas.

Periodic sync:

Clients occasionally request full table updates (e.g., every 10 turns) to keep in sync.

On-demand fetch:

If a delta references something the client doesn’t know about, it requests that one record.

Example

Server sends:

{"type": "delta", "tile": 42, "changed": ["status"]}


Client checks cache:

Has tile 42? Yes → update status only.

Has tile 42? No → request full tile data from server or read-only DB.

5. Avoiding Bloat Without a DB Read

If you don’t want clients reading the DB, you can still avoid bloat:

Chunk the world: Only send data about the player’s immediate surroundings.

Use snapshots: Send one full snapshot at connection, then only deltas.

But letting clients read the DB (even as replicas) does let you avoid large repetitive packets.

Key Insight

Clients can read, but never write, the DB. Messages from the server become hints (keys, IDs, deltas) that tell the client what parts of the DB to refresh.

This is exactly how Civ, Factorio, and even big MMOs work.

## Mockup

- Terminal 1: Run the server (server.py)
- Terminal 2, 3, 4: Run client programs (client.py) with different player IDs.

```bash
python server.py

python client.py --player-id A
python client.py --player-id B
```

In each client terminal:

```text
> chat B Hello!
> broadcast Storm incoming!
> action move north
```

Server terminal displays the flow:

```text
[A]: chat -> B: Hello!
[B]: broadcast -> all: Storm incoming!
```

- See the message routing logic very explicitly.

- CLI-based testing makes it easy to experiment with JSON messages, game state changes, and delta syncing before adding any visual complexity.

## Summary

Server = The Brain

Owns the authoritative world state (DB).

Processes all actions, resolves conflicts, updates the DB.

Pushes deltas (state changes) to all clients.

Clients = Eyes, Hands, and Mouth

Eyes: Render the current world state based on what the server sends.

Hands: Send “actions” (move, chat, attack, build) back to the server.

Mouth: Relay updates to the user (UI, chat messages, map changes).

The client never makes game state decisions itself.

No desyncs: Everyone sees the same world because the server is the only source of truth.

Security: Clients can’t cheat by modifying their own DB—they don’t have one.

Simpler architecture:

No distributed DB syncing.

Messages become your single “contract” between client and server.

- This is the simplest thing that will actually work.
- Can build a complete multiplayer prototype with just socketserver and JSON.
- No extra libraries, no async headaches.
- Dead easy to debug (especially with print statements and SQLite for state).
- If we want to switch later, the interface is clean enough to refactor.

socketserver (or really any basic TCP server) can handle both direct peer-to-peer messages and broadcasts really cleanly. It’s just a matter of how you design the message flow and maintain the list of connected clients.

---

1. Start With the Simplest Model

Server is authoritative: it writes the DB.

Clients:

Load an initial snapshot of the world (maps, units, etc.) when they connect.

Receive only deltas from the server after that.

Cache what they’ve seen; if they’re missing something, request it.

No replication, no direct DB reads, no clever caching—just lightweight messages + a client cache.

2. Add Complexity Only When You Feel Pain

If your deltas start to feel bloated:
→ Add chunking (send only what’s in the player’s “fog of war”).

If clients need to query big static data (like map metadata):
→ Give them a read-only local cache (SQLite copy).

If syncing caches becomes a mess:
→ Introduce delta logs or event sourcing.

You don’t start with these. You earn them.

3. The Happiness Formula

Solve the immediate problem in the simplest way.

Test with a few players/clients.

Only add complexity when your existing solution actively breaks or drags you down.

4. The Key Question for Each Feature

Do I actually need this now, or is it “future-me” worrying?

If I add it, is it going to make the rest of the system heavier?

Most of the time, the simplest path is:

Server-controlled DB.

Clients as renderers + action messengers.

Small deltas and initial snapshots.

That alone will get you pretty far—especially since your game is turn-based (“Civ Lite”) and doesn’t need Twitch-level real-time sync.

Keep It Small and Happy

One authoritative server (writes DB, sends deltas).

Multiple dumb clients (render world, send actions).

Messages = lightweight JSON via socketserver or asyncio.

Caching? Start with in-memory caches. Replication? Nope.

When (if!) you hit scaling walls, then you can think about event queues or Celery-style task management.

# IPC - Inter-Process Communication

It’s the umbrella term for how two separate programs (or processes) talk to each other.

If you run PySide as your main app and spin up PyGame as a child process, IPC is the channel that lets them pass messages back and forth:

Lightweight forms:

- Standard input/output (child prints JSON, parent reads it).
- Local sockets (TCP or Unix domain sockets).
- Named pipes (FIFO files).

Heavier forms:

- Shared memory, message queues, or database-like backends.
- For our “small steps” approach, JSON-over-a-socket is perfect:
  - Each message is a JSON line (\n-terminated).
  - Parent (PySide) can send commands like {"cmd": "load_map", "map_id": "TABLUNQUE_01"}.
  - Child (PyGame) can emit events like {"evt": "unit_selected", "id": "A17"}.

It keeps the two event loops separate, but still lets them behave like one app. Later, if you embed PyGame inside PySide, you can reuse the same message schema internally.

Expect more ADRs! “ADR-IPC” to lock down transport (socket vs. pipe), schema, and lifecycle would be the natural companion to ADR-0011 (contracts) and ADR-0014 (i18n labels).

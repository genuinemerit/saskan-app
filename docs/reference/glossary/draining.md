# Draining

Graceful shutdown mode for a server: stop admitting new work while allowing in-flight operations to finish.

- Use: in PR-2 (request–reply), accept the TCP connection, reply with a `system.reject` (reason: `server_not_ready`), then close.
- Goal: give clients a clear, deterministic “server is closing” response instead of hanging or refusing the socket.

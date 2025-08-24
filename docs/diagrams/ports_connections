# Client/Host ports and connections

Client host                                     Server host
===========                                     ===========

App (CLI)
  |                                              App (Server)
  | socket()                                     |
  | bind(0.0.0.0:0)   ← OS picks ephemeral       | socket()
  |  e.g., 10.0.1.5:53842                        | bind(0.0.0.0:7777)   (fixed)
  | connect(203.0.113.10:7777) ----------------> | listen()
  |                                              | accept() → (client=10.0.1.5:53842)
  | send(HELLO) -------------------------------->| recv()
  | recv(WELCOME/REJECT) <-----------------------| send()
  | close()                                      | close()

## Key points

Client source port is ephemeral (picked by OS): typically a high port (e.g., 49152–65535). You don’t configure it.

Server port is well‑known/fixed (e.g., 7777). Both sides must agree on this.

A TCP connection is identified by the 4‑tuple:
(client_ip, client_ephemeral_port, server_ip, server_fixed_port).

Multiple clients can connect simultaneously because their ephemeral ports differ.

The server can accept many connections on the same fixed port; each accept() returns a distinct socket bound to a unique 4‑tuple.

## NAT/firewall notes (quick)

Outbound from client usually allowed: NAT/firewall tracks the 4‑tuple and lets return traffic back to the client’s ephemeral port.

Inbound to server requires the server’s fixed port (7777) to be open on its firewall and forwarded if behind NAT.

## Operational defaults for PR‑2

Server: host=0.0.0.0, port=7777.

Client: connect to the same host:port; its source port is ephemeral and managed by the OS.

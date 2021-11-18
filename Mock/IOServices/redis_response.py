#!/usr/bin/python3.9
"""
:module:    redis_response.py
:host:port: curwen:52020
:channel:   redis_io_services

Mockup for handling Redis requests, creating and sending responses.

Start up / shut down this service using `control_servers.sh`

Handle messages like `*.%.+.$`, where...
    % : topic = ("schema", "log", "harvest", "monitor")
    * : category = ("owl", "redis", "sqlite", "topic")
    + : plan = ("get", "put", "remove", "update", "meta")
    $ : service = ("subscribe", "request")
Send messages like `*.%.+.^`, where ...
    ^ : service = ("publish", "response")

Main behaviors:
- Interpret Redis requests and subscriptions.
- Use redis_io.py methods to handle Redis backend.
    - Write, update, read, get metadata from Redis.
    - Write to `schema`, `log` namespaces, with no expiration.
    - Read from `schema`, `log`, `harvest` namespaces.
- Assemble the response.
    - Store in `harvest` namespace, with expiration.
    - Send response to requestor and/or subscribers.
"""

import argparse
import asyncio
import uuid

from bow_msgs import BowMessages  # type: ignore
ms = BowMessages()


async def main(args):
    me = uuid.uuid4().hex[:8]
    reader, writer = await asyncio.open_connection(
        args.host, args.port)
    me = "redis_io_responder_" + uuid.uuid4().hex[:8]
    sock = writer.get_extra_info("sockname")
    # Responders listen to a designated channel.
    channel = args.listen.encode()
    # Refactor prints to write to Redis Monitor namespace,
    #  then construct a subscription service to read from it.
    # Display the messages from the Monitor namespace on GUI
    # Use kivy to build the GUI. Same GUI should eventually
    # provide nicer front-end for control_servers.sh too.
    mon = f"Responder: {me} | " +\
        f"Socket: {sock} | Host: {args.host}:{str(args.port)}"
    print(mon)
    await ms.send_msg(writer, channel)
    try:
        while data := await ms.read_msg(reader):
            print(f'Received by {me}: {data[:20]}')
        print('Connection ended.')
    except asyncio.IncompleteReadError:
        print('Server closed.')
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    """
    Schema identifying servers, clients, ports would be useful.
    Schema identifying what to listen for, what to send, by whom.
    Eventually config UFW to only allow ports open that we want to use.
    "listen" identifies a "channel".
    afaik a channel could handle n requests, and n responses.
    It is also not the same thing as a topic, which is something that
      can be subscribed to (via a particular channel).
    Maybe investigate using unix sockets instead of ports.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='curwen')
    parser.add_argument('--port', default=52020)
    parser.add_argument('--listen', default='/queue/redis_io_services')
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

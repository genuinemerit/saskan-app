#!/usr/bin/python3.9
"""
:module:    redis_response.py
:host:port: curwen:52020
:channel:   redis_io_services

HandleRedis requests, creating and sending responses.
This is a Messaging Gateway for Redis-related services.

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

from BowDataSchema.BowQuiver.msgseq import MsgSequencer  # type: ignore
MS = MsgSequencer()


async def main(args):
    me = uuid.uuid4().hex[:8]
    reader, writer = await asyncio.open_connection(
        args.host, args.port)
    me = "redis_io_responder_" + uuid.uuid4().hex[:8]
    sock = writer.get_extra_info("sockname")
    # Responders listen to a designated __channel__.
    channel = args.listen.encode()
    # Refactor prints to write to Redis Monitor namespace,
    #  then construct a subscription service to read from it.
    # Display the messages from the Monitor namespace on GUI
    # Use kivy to build the GUI. Same GUI should eventually
    # provide nicer front-end for control_servers.sh too.
    mon = f"Responder: {me} | " +\
        f"Socket: {sock} | Host: {args.host}:{str(args.port)}"
    print(mon)
    await MS.send_msg(writer, channel)
    try:
        while data := await MS.read_msg(reader):
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
    afaik a channel could handle _n_ requests, and _n_ responses.
    It is also not the same thing as a topic, which is something that
      can be subscribed to via a particular channel.
    The hierarchial design for a message-based system refers to...
    - A "channel" is a communication path, a host and a port.
    - A "topic" is a communication topic, category handled on a channel.
    - A "plan" is a communication plan describing a set of services on a topic.
    - A "service" is a communication service, which may be either a
        "request" or a "subscription", on the one hand, or a "response"
        or a "publication", on the other.
    - A "server" is a traffic broker for a set of services (a plan) on a topic.
    - A "schema" defines the acceptable format of a particular message.
    - A "message" is a communication message, that is, a specific transfer
        of data between a client and a server.
    - A "package" is a message that is in transit.
    - A "record" is a message that is in storage, either cached or persisted.
    - A "key" is a a unique identifier for a message.
    - A "value" is a message payload, that is, the body of a message, typically
      unrelated to handling of the message itself.
    - A "header" or "meta" are fields that describe a message and assist in
      handling its transfer, processing, retrieval, and storage.
    - A "field" is a named data element within the header or body of a message.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='curwen')
    parser.add_argument('--port', default=52020)
    parser.add_argument('--listen', default='/queue/redis_io_services')
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

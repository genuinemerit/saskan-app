#!/usr/bin/python3.9
"""
:module:    redis_server.py
:host:port: 127.0.0.1:52020

Mockup for serving Redis connections and IO.
Replace with appropriate component-level services.

Main behaviors:

- Bring up Redis server if not running.
- Create namespaces if they do not exist.
- Create Redis connections.
- GET:
  - Record(s) from SANDBOX, SCHEMA, or RESULT databases.
- SET:
  - Record(s) to SANDBOX, SCHEMA, or RESULT databases.
- XADD:
  - Record(s) to LOG database.
- XRANGE:
  - Record(s) from LOG database.
"""

import asyncio
from asyncio import StreamReader, StreamWriter, gather
from collections import defaultdict, deque
from typing import DefaultDict, Deque

from bow_msgs import BowMessages  # type: ignore
ms = BowMessages()

SUBSCRIBERS: DefaultDict[bytes, Deque] = defaultdict(deque)


async def server(reader: StreamReader, writer: StreamWriter):
    peername = writer.get_extra_info('peername')
    subscribe_chan = await ms.read_msg(reader)
    SUBSCRIBERS[subscribe_chan].append(writer)
    print(f'Remote {peername!r} subscribed to {subscribe_chan!r}')
    try:
        while channel_name := await ms.read_msg(reader):
            data = await ms.read_msg(reader)
            print(f'Sending to {channel_name!r}: {data[:19]!r}...')
            conns = SUBSCRIBERS[channel_name]
            if conns and channel_name.startswith(b'/queue'):
                conns.rotate()
                conns = deque([conns[0]])
            await gather(*[ms.send_msg(c, data) for c in conns])
    except asyncio.CancelledError:
        print(f'Remote {peername} closing connection.')
        writer.close()
        await writer.wait_closed()
    except asyncio.IncompleteReadError:
        print(f'Remote {peername} disconnected')
    finally:
        print(f'Remote {peername} closed')
        SUBSCRIBERS[subscribe_chan].remove(writer)


async def main(*args, **kwargs):
    """Launch the Redis server.
    It uses no arguments at this time.
    """
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()

try:
    asyncio.run(main(server, host='127.0.0.1', port=52020))
except KeyboardInterrupt:
    print('Bye!')

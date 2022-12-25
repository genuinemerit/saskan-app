#!/usr/bin/python3.9
"""
:module:    saskan_server.py
:host:port: set by arguments

Serve up connections and IO for channel(s)
on specified host/port.

Main behaviors:

- Handle traffic for channels on specified host/port.
"""

import asyncio
import sys
from asyncio import StreamReader, StreamWriter, gather
from collections import defaultdict, deque
from typing import DefaultDict, Deque

from BowQuiver.msg_sequencer import MsgSequencer   # type: ignore
ms = MsgSequencer()

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
    Make sure responder and requesters for this server use
      the same host name and port.
      Host name and port need to be exactly the same.
    """
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()

try:
    asyncio.run(main(server, host=sys.argv[1], port=sys.argv[2]))
except KeyboardInterrupt:
    print('Bye!')

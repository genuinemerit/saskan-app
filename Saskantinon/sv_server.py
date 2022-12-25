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

from sv_sequencer import MsgSequencer
MS = MsgSequencer()

SUBSCRIBERS: DefaultDict[bytes, Deque] = defaultdict(deque)


async def server(reader: StreamReader, writer: StreamWriter):
    """Handle traffic for a single channel = unique combo of hosts:ports
    """
    peername = writer.get_extra_info('peername')
    subscribe_chan = await MS.read_msg(reader)
    SUBSCRIBERS[subscribe_chan].append(writer)
    print(f'Remote {peername!r} subscribed to {subscribe_chan!r}')
    try:
        while channel_name := await MS.read_msg(reader):
            data = await MS.read_msg(reader)
            print(f'Sending to {channel_name!r}: {data[:19]!r}...')
            conns = SUBSCRIBERS[channel_name]
            if conns and channel_name.startswith(b'/queue'):
                conns.rotate()
                conns = deque([conns[0]])
            await gather(*[MS.send_msg(c, data) for c in conns])
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
    """Launch a socket server on a channel.

    Args:
    - host: host name(s) or IP address(es)
    - port: port number(s)

    Responder and requesters must use same channel.

    """
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()

try:
    """Run the server in asynchronous/non-blocking mode
    main = name of main routine to run
    server = name of callback when a new client connects

    Command line arguments:
    1 = channel name
    2 = host = host name(s) or IP address(es)
    3 = port = port number(s)
    """
    print(f"Starting {sys.argv[1]} server on {sys.argv[2]}:{sys.argv[3]}")
    asyncio.run(main(server, host=sys.argv[2], port=sys.argv[3]))
except KeyboardInterrupt:
    print('Bye!')

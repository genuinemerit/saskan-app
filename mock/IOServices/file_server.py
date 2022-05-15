#!/usr/bin/python3.9
"""
:module:    file_server.py
:host:port: 127.0.0.1:52010

Mockup for serving IO Services messages.

Main behaviors:

- Manage client message broker for IO Services messages
  communicating to any other authorized components.

- Manage comms for pub-sub topics -->
  - `/ontology_file` or `/queue/ontology_file`

- Listen
{
"name": "GetOntologyFile_Request",
"namespace": "net.genuinemerit.data",
"fields": {
    "version": "0.1.0",
    "hash": "lkjasdfl;k908sdf09as0fposfkl;f980",
    "handshake": {"token": "uwoepir980237498weufpoijdlks;i"},
    "topics": ["/queue/ontology_file"]]
    }
}

- Send
{
"name": "GetOntologyFile_Response",
"namespace": "net.genuinemerit.data",
"fields": {
    "version": "0.1.0",
    "hash": "asdf98a7d0f897adsf89asdfjksdfkj",
    "handshake": {"auth": ["ontology_file/GetOntologyFile/reader"]},
    "topics": ["/queue/ontology_file"]],
    "file": "saskan_ontology_xml.owl"
    }
}

"""
import asyncio
from asyncio import StreamReader, StreamWriter, gather
from collections import defaultdict, deque
from typing import DefaultDict, Deque

from bow_msgs import BowMessages  # type: ignore
ms = BowMessages()

SUBSCRIBERS: DefaultDict[bytes, Deque] = defaultdict(deque)


async def server(reader: StreamReader, writer: StreamWriter):
    """
    See: https://tinyurl.com/j7y4vf42 for more info on the
    StreamWriter.get_extra_info() function. `peername` returns
    remote address to which the socket is connected.
    """
    peername = writer.get_extra_info('peername')
    subscribe_chan = await ms.read_msg(reader)
    SUBSCRIBERS[subscribe_chan].append(writer)
    # Start thinking about unifying all console messages into a common format.
    # Consider sending to a common channel which  can be subscribed to by a
    #   GUI, a logger, an analyzer, and so on.
    print(f'Remote {peername!r} subscribed to {subscribe_chan!r}')
    try:
        while channel_name := await ms.read_msg(reader):
            data = await ms.read_msg(reader)
            # Not sure why this is limited to 19 characters.
            # That's apparently what the prototype decided was
            #   max length of the topic name.
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
    """Launch the file server.
    It uses no arguments at this time.
    """
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()

try:
    asyncio.run(main(server, host='127.0.0.1', port=52010))
except KeyboardInterrupt:
    print('Bye!')
    asyncio.get_event_loop().stop()

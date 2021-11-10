#!/usr/bin/python3.9
"""
:module:    data_admin_server.py

Mockup for serving Data Admin messages.
Eventually this will be replaced by a real module
  and moved to component bow-data-admin.

Main behaviors:

- Manage client message broker for Data Admin messages
  communicating to the BowDataSchema component.

- Manage comms for pub-sub topic --> `saksan_concept` or `queue_saskan_concept`
    - Communicate with the Bow Data Schema component

- Send
    - Request_GetSaskanDataObject(
        topic_name: str,
        concept_name: str,
        data_object_type: str,
        auth_token: str)

- Listen
    - Generic
        - AcknowledgeRequest()
        - DenyRequest()
        - AcceptRequest()
        - Request_Channel(`saksan_concept`)

    - Response_GetSaskanDataObject(
        topic_name: str,
        concept_name: str,
        data_object_type: str,
        auth_token: str)

Subscribers to channel 'saksan_concept' stored in a deque.
"""
import asyncio
from asyncio import StreamReader, StreamWriter, gather
from collections import defaultdict, deque
from typing import DefaultDict, Deque

from data_admin_msgs import read_msg, send_msg

SUBSCRIBERS: DefaultDict[bytes, Deque] = defaultdict(deque)


async def server(reader: StreamReader, writer: StreamWriter):
    """
    Produce a long-lived coroutine for each connection.
    Get host and port from the connection.

    First message must be a Request_Channel message.
    Add the writer to list of clients subscribed to channel.

    Next message must be a Request_GetSaskanDataObject message.
    The second message is sent to all clients subscribed to the channel.

    Wait for the messages to arrive.
    Get subscribers from the deque.
    If requested channel names starts with `queue_` send only to
      then next subscriber in the deque rotation rather than all.
      This is how we manage having multiplke workers.

    Gather coroutines for sending messages to each writer.
    This will be modified later. As is, message distribution will
      slow to the speed of the slowest subscriber.

    Remove writer from subscribers
    """
    peername = writer.get_extra_info('peername')
    subscribe_chan = await read_msg(reader)
    SUBSCRIBERS[subscribe_chan].append(writer)
    print(f'Remote {peername!r} subscribed to {subscribe_chan!r}')
    try:
        while channel_name := await read_msg(reader):
            data = await read_msg(reader)
            print(f'Sending to {channel_name!r}: {data[:19]!r}...')
            conns = SUBSCRIBERS[channel_name]
            if conns and channel_name.startswith(b'/queue'):
                conns.rotate()
                conns = deque([conns[0]])
            await gather(*[send_msg(c, data) for c in conns])
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
    """Launch the server.  """
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()

try:
    asyncio.run(main(server, host='127.0.0.1', port=25000))
except KeyboardInterrupt:
    print('Bye!')
    # Trying this...
    asyncio.get_event_loop().stop()

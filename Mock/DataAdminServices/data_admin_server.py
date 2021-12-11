#!/usr/bin/python3.9
"""
:module:    data_admin_server.py
:host:port: localhost:52000

Mockup for serving Data Admin messages.
Eventually this will be replaced by a real module
  and moved to component bow-data-admin.

Main behaviors:

- Manage client message broker for Data Admin messages
  communicating to the BowDataSchema component.

- Manage comms for pub-sub topic --> `saksan_concept` or `queue_saskan_concept`
    - Communicate with the Bow Data Schema component

- Send
    - GetSaskanDataObject_Request(
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

    - GetSaskanDataObject_Response(
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

import bow_msgs

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
    subscribe_chan = await bow_msgs.read_msg(reader)
    SUBSCRIBERS[subscribe_chan].append(writer)
    print(f'Remote {peername!r} subscribed to {subscribe_chan!r}')
    try:
        while channel_name := await bow_msgs.read_msg(reader):
            data = await bow_msgs.read_msg(reader)
            print(f'Sending to {channel_name!r}: {data[:19]!r}...')
            conns = SUBSCRIBERS[channel_name]
            if conns and channel_name.startswith(b'/queue'):
                conns.rotate()
                conns = deque([conns[0]])
            await gather(*[bow_msgs.send_msg(c, data) for c in conns])
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
    # Try a series of ports until I find what works best.
    # Ports 1024 to 49151 are "registered",
    #   those between 49152 and 65535 are "private".
    # For my private services, I want to use those above 49152.
    # asyncio.run(main(server, host='127.0.0.1', port=25000))
    # Using a named host works fine. All the services using it need
    #   to use the name instead of the IP address.
    asyncio.run(main(server, host='127.0.0.1', port=52000))
except KeyboardInterrupt:
    print('Bye!')
    # Trying this...
    asyncio.get_event_loop().stop()

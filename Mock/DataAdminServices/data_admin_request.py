#!/usr/bin/python3.9
"""
:module:    data_admin_request.py
:host:port: localhost:52000

Mockup for serving Data Admin messages.

Main behaviors:

- Manage client message broker for Data Admin messages
  communicating to the BowDataSchema component.

- Manage comms for pub-sub topic --> `saksan_concept` or `queue_saskan_concept`
    - Communicate with the Bow Data Schema component

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
"""

import argparse
import asyncio
import uuid

import bow_msgs


async def main(args):
    """
    Create a listener identiy using uuid.
    Open server connection.
    Provide channel name as an input argument.
    Send the channel name.
    Wait for data to appear on the socket.
    """
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    reader, writer = await asyncio.open_connection(
        args.host, args.port)
    print(f'I am {writer.get_extra_info("sockname")}')
    channel = args.listen.encode()
    await bow_msgs.send_msg(writer, channel)
    try:
        while data := await bow_msgs.read_msg(reader):
            print(f'Received by {me}: {data[:20]}')
        print('Connection ended.')
    except asyncio.IncompleteReadError:
        print('Server closed.')
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    """
    Provide host, port, topic as command line arguments with defaults.
    ???: Why not close the connection?
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=52000)
    parser.add_argument('--listen', default='/topic/saskan_concept')
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

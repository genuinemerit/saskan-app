#!/usr/bin/python3.9
"""
:module:    data_admin_sender.py
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
    - Request_GetSaskanDataObject(
        topic_name: str,
        concept_name: str,
        data_object_type: str,
        auth_token: str)

@DEV
- Not clear what is meant by "Data Admin" in this context.
- This is an earlier prototype. See IOServices for a better one.
"""
import argparse
import asyncio
import uuid
from itertools import count

import bow_msgs


async def main(args):
    """
    Claim an identity for the "sender".
    Make a connection.
    As a sender, just send null message for listen request.
        (first message)
    Send message to desired channel.
    Be sure to encode as bytes.
        (second message)
    For the loop sending 2nd msg, use an iter count.
        It returns an integer for each loop iteration,
        which can be useful for debugging.
    A delay between sends is set as an input argument.
    Message payload is either a bytestring of specified size,
        or a specific encoded string. (just examples)
    Send channel name, then mesage payload.

    @DEV:
    - May have my terminology mixed up. This is a mockup sender.
    - A "sender" is a requestor, not a responder.
    - The real "listener" is the server component. It is the
        component that receives messages and directs them to
        a handler.
    - See code in IOServices for better understanding.
    """
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    print(f'I am {writer.get_extra_info("sockname")}')

    channel = b'/null'
    await bow_msgs.send_msg(writer, channel)

    chan = args.channel.encode()
    try:
        for i in count():
            await asyncio.sleep(args.interval)
            data = b'X'*args.size or f'Msg {i} from {me}'.encode()
            try:
                await bow_msgs.send_msg(writer, chan)
                await bow_msgs.send_msg(writer, data)
            except OSError:
                print('Connection ended.')
                break
    except asyncio.CancelledError:
        writer.close()
        await writer.wait_closed()

if __name__ == '__main__':
    """
    Optionally set as arguments:
    - host: str
    - port: int
    - channel: str  (set up to expect multiple listener workers)
    - size: int (bytes)
    - interval: float (seconds)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=52000, type=int)
    parser.add_argument('--channel', default='/topic/queue_saskan_concept')
    parser.add_argument('--interval', default=1, type=float)
    parser.add_argument('--size', default=0, type=int)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
        # asyncio.get_event_loop().close()

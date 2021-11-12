#!/usr/bin/python3.9
"""
:module:    file_sender.py
:host:port: 127.0.0.1:52010

Mockup for serving IO Services.

Main behaviors:

- Manage comms for pub-sub topics -->
  - `/ontology_file` or `/queue/ontology_file`


Need to wrap my head around exactly what "listen" and "send" do.

Am I "sending" the request or the response?
- I am sending the RESPONSE.
- I am publishing to the subscriber-listeners based on some event.
- The event can be EITHER
    - a get_ontology_file request from the "listener".
  OR
    - detecting some change to the ontology_file.
- What I send may vary (?) based on what users (listeners) are authorized for.

Am I "listening" for the request or the response?
- I am listening for the RESPONSE.
- I MAY be subscribing to the publisher of the `ontology_file` topic.
    - The type of subscription is determined by the roles assigned to the user-listener.

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
import argparse
import asyncio
import uuid
from itertools import count

import bow_msgs


async def main(args):
    """
    For uuid, see: https://docs.python.org/3/library/uuid.html
    uuid4 is a random UUID.
    """
    # Not sure why it is taking only the first part of the uuid.
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    # Could probably blank out (_) the reader here. It is not used.
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    # Could capture this into a variable for use in better console msgs.
    print(f'I am {writer.get_extra_info("sockname")}')

    channel = b'/null'
    await bow_msgs.send_msg(writer, channel)

    chan = args.channel.encode()
    try:
        for i in count():
            await asyncio.sleep(args.interval)
            # Modify this to save the ontology file to Redis if
            # it is not already there, or if it is out of date.
            # Then provide the Redis key to the ontology_file as data.
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
    parser.add_argument('--port', default=52010, type=int)
    parser.add_argument('--channel', default='/queue/ontology_file')
    parser.add_argument('--interval', default=1, type=float)
    parser.add_argument('--size', default=0, type=int)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

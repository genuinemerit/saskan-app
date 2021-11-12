#!/usr/bin/python3.9
"""
:module:    redis_sender.py
:host:port: 127.0.0.1:52020

Mockup for serving Redis IO Services.

Main behaviors:

- Handle Redis requests.
- Send responses after handling Redis requests.
"""
import argparse
import asyncio
import uuid
from itertools import count

import bow_msgs


async def main(args):
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
            # Modify this to provide the Redis key to RESULT record.
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
    parser.add_argument('--port', default=52020, type=int)
    parser.add_argument('--channel', default='/queue/ontology_file')
    parser.add_argument('--interval', default=1, type=float)
    parser.add_argument('--size', default=0, type=int)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

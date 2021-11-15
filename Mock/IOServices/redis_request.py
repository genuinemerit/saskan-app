#!/usr/bin/python3.9
"""
:module:    redis_request.py
:host:port: curwen:52020

Mockup for serving up requests to for Redis IO Services.

Not sure if this needs to be a separate client, or if
it serves a purpose, collecting requests for this channel
from app-level needs.
"""
import argparse
import asyncio
import uuid
from itertools import count

from bow_msgs import BowMessages  # type: ignore
ms = BowMessages()


async def main(args):
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    me = uuid.uuid4().hex[:8] + "_redis_request"
    sock = writer.get_extra_info("sockname")
    # Refactor to write to monitoring log
    print(f"Started {me} at {sock} on {args.host}:{str(args.port)}")
    # Requestors send a null message to the server to indicate they are ready.
    # They are not responsible for managing traffic on a channel.
    channel = b'/null'
    await ms.send_msg(writer, channel)
    chan = args.channel.encode()
    try:
        for i in count():
            await asyncio.sleep(args.interval)
            # Test message.
            # Replaced w/ requests relating to channel "redis_io_services".
            data = b'X'*args.size or f'Msg {i} from {me}'.encode()
            try:
                await ms.send_msg(writer, chan)
                await ms.send_msg(writer, data)
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
    # parser.add_argument('--host', default='localhost')
    parser.add_argument('--host', default='curwen')
    parser.add_argument('--port', default=52020, type=int)
    parser.add_argument('--channel', default='/queue/ontology_file')
    parser.add_argument('--interval', default=1, type=float)
    parser.add_argument('--size', default=0, type=int)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

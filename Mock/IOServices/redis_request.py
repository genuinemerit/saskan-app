#!/usr/bin/python3.9
"""
:module:    redis_listener.py
:host:port: 127.0.0.1:52020

Mockup for generating Redis request messages.

Main behaviors:

- Subscribe to Redis-related channel.
- Send a request message to Redis IO Services.
- Receive a response message from Redis IO Services.
- Do something with the response.
"""

import argparse
import asyncio
import uuid

from bow_msgs import BowMessages  # type: ignore
ms = BowMessages()


async def main(args):
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    reader, writer = await asyncio.open_connection(
        args.host, args.port)
    print(f'I am {writer.get_extra_info("sockname")}')
    channel = args.listen.encode()
    await ms.send_msg(writer, channel)
    try:
        while data := await ms.read_msg(reader):
            print(f'Received by {me}: {data[:20]}')
        print('Connection ended.')
    except asyncio.IncompleteReadError:
        print('Server closed.')
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    """
    Not entirely sure what value is needed for --listen.
    Don't know that we would want that to be available via an arg?
    OR is that the right way to use this abstractly? (yes)
    Consider what kind of set-up we want to use for ports and
    tie that into UFW (Unix Firewall) configuration.
    Consider checking first what ports are open in the range I want.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=52020)
    parser.add_argument('--listen', default='/queue/GetRedisMessage')
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

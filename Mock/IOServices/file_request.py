#!/usr/bin/python3.9
"""
:module:    file_listener.py
:host:port: 127.0.0.1:52010

Mockup for serving IO Services messages.

Main behaviors:

Am I "listening" for the request or the response?
- I am listening for RESPONSEs from the publisher of the `ontology_file` topic.
- I MAY be subscribing to the publisher of the `ontology_file` topic.
- I MAY be un-subscribing from the publisher of the `ontology_file` topic.
    - The type of subscription is determined by the roles assigned to the
    user-listener.

- Manage comms for pub-sub topics -->
  - `/ontology_file` or `/queue/ontology_file`

- Listen

Request sub:
"name": "GetOntologyFile_Subscribe",

Request unsub:
"name": "GetOntologyFile_Unsubscribe",

Request file refresh:
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

Handle:
"name": "GetOntologyFile_Refresh"


Need to keep thinking this through.
Is it better to think "publisher" or "subscriber"
  rather than "listener" or "sender"?
For "low level" services like IO and "console info",
  the listeners and senders are triggerd, used, called (?),
  by multiple components, right? Do I think of the the components
  as "users" of the service, rather than thinking of the service
  as a "user"?
In my prototype so far, the "sends" (and "listens" ?) are triggered
  by mockup code.
In a real system, they would be triggered by a "user" -- a component-function.

Next iteration:
- Set up some mockup Avro schemas.
- Set up some mockup records on Redis.
- Set up some mockup records on LDAP.
- Extend the start_stop manager to cover all the services, not just Data Admin.
- Break out (some?) "listen" and "send" events into a separate bash file.
  - Trigger them to mockup actual components using the services.

Pretty cool! I like that it is all sockets so far, all handled via asyncio.
At a certain point:
- Try moving all or some of it to genuinemerit.net.
- Remember to spend some time on security features.
"""

import argparse
import asyncio
import uuid

from bow_msgs import BowMessages  # type: ignore
ms = BowMessages()


async def main(args):
    """
    Work on abstracting all texts, as in bow-data component.
    """
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    reader, writer = await asyncio.open_connection(
        args.host, args.port)
    # Get the address of me, of this socket.
    print(f'I am {writer.get_extra_info("sockname")}')
    channel = args.listen.encode()
    await ms.send_msg(writer, channel)
    try:
        while data := await ms.read_msg(reader):
            # Look carefully at what is being printed here.
            # If it could be sensitive, the restrict it from printing
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
    Don't know that we would want that to be available via an arg.
    Eventually these will move to genuinemerit.net.
    Consider what kind of set-up we want to use for ports.
    Tie that into UFW (Unix Firewall) configuration.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=52010)
    parser.add_argument('--listen', default='/queue/ontology_file')
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

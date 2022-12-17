#!/usr/bin/python3.9
"""
:module:    redis_request.py
:host:port: curwen:52020

Mockup/tester for serving requests to Redis IO Services.
Move into a test suite.
Actual functionality will be handled in App calls.

@DEV
- Can this also serve an ongoing functional purpose, e.g.,
  collecting requests for this channel from app-level needs?
- Kind of a broker for requests?
"""
import argparse
import asyncio
import random
import uuid
from itertools import count
from os import urandom
from pprint import pprint as pp

from BowQuiver.saskan_schema import SaskanSchema  # type: ignore
from BowQuiver.msg_sequencer import MsgSequencer  # type: ignore

SS = SaskanSchema()
MS = MsgSequencer()

random.seed(a=urandom(32))


async def main(args):
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    me = "redis_io_requestor_" + uuid.uuid4().hex[:8]
    sock = writer.get_extra_info("sockname")
    # Refactor to write to monitoring log
    mon = f"Requestor: {me} | " +\
        f"Socket: {sock} | Host: {args.host}:{str(args.port)}"
    print(mon)
    # Requestors send a null message to the server to indicate they are ready.
    # Since they are not responsible for managing traffic on a channel,
    # the initial message indicates a null channel.
    channel = b'/null'
    await MS.send_msg(writer, channel)
    chan = args.channel.encode()
    try:
        # This is prototype code, just sending a series of meaningless
        # messages. We want to start sending meaningful messages that
        # can be used to test the responder. Note that the request
        # prototypes are not yet set up to act as subscribers, only
        # as requestors. They don't "listen" for anything. It is the
        # "responders" who are "listening" for requests on the channel.
        # In a next iteration, we will need to add a subscriber mode,
        # where the response is sent back to the requestor.
        for i in count():
            await asyncio.sleep(args.interval)
            # Test message.
            # Replace w/ tests of requests relating to channel
            #   "redis_io_services". Then eventually put a GUI
            #    in front of this for creating schemas, etc.
            # Not quite sure what is going on in the prototype.
            #   The client is sending a message to the server,
            # which passes it along to the response handler.
            # I think the "size" is an integer sent in the first
            # 4 bytes, which tells the server how many bytes to
            # expect in the data portion of the message.
            # The encode() function usually has some params.
            # Not sure why the example I was following didn't just
            # use bytes() here? With no params, it uses the
            # default encoding, whatever that means. I am accustomed
            # to either using bytes() or encode('utf-8').
            data = b'X'*args.size or f'Msg {i} from {me}'.encode()
            try:
                await MS.send_msg(writer, chan)
                await MS.send_msg(writer, data)
            except OSError:
                print('Connection ended.')
                break
        # Next iteration prototype. Send one of several different
        # test messages, choosing which one randomly.
        msg_ty = random.randint(0, 2)
        if msg_ty == 0:
            # Use the bow_serde class to verify, convert the message.
            # convert_py_dict_to_msg_jzby() converts to javascript,
            # compresses using zlib and base64 encodes.

            # This get a little into meta-meta. I want to send a message
            # to tell redis_io_services to write a schema which describes
            # a message. Chicken/egg. How can the responder recognize a
            # message about writing schemas if it doesn't have a schema
            # to work from? At some point I need to "seed" Redis/Schema
            # with the base set of schemas. I'll work on defining those
            # as part of the next iteration of prototype messages...

            # Be clear on distinctions between "channel", "topic", and
            # "message-name"/redis-key.
            # A channel is mainly connected to a "requestor" (a "service
            # listener") node. A set of topics is handled on a given channel.
            # Some channels are tied to a particular type of store or
            # resource. For example, `redis_io` or `file_io`.

            # Message names consist of:
            #   channel.topic.plan.service <== and it is the redis key.
            # This grammar applies to Schema, Harvest namespaces.
            # Items in the Monitor and Log namespaces use incrementally-
            # sequenced time stamps as key prefixes.
            """
            self.field_ty: set = ("array", "hash", "set", "string")
            self.msg_cat: set = ("owl", "redis", "sqlite", "topic")
            self.msg_plan: set = ("get", "put", "remove", "update", "meta")
            self.msg_svc: set = ("publish", "subscribe", "request", "response")
            """
            data: dict = {
                "type": "record",
                "name": "redis.schema.put.request",
                "namespace": "net.genuinemerit.schema",
                # >> maybe we have a special token for this type of request? <<

                # The schema that describes THIS message needs fields that
                # describe a schema.
                # "name": "channel", "type": "string"
                # "name": "topic", "type": "string"
                # "name": "plan_ty", "type": "string"
                # "name": "service_ty", "type": "string"
                # "name": "namespace", "type": "string"
                # "name": "doc", "type": "string"

                "fields": {
                    "namespace": "net.genuinemerit.schema",
                    "store": "redis",
                    "channel": "redis_io",
                    "topic": "ontology_file",
                    "plan_ty": "put",
                    "service_ty": "request",
                }
            }
        elif msg_ty == 1:
            data: dict = {
                "type": "record",
                "name": "redis.schema.put.request",
                "namespace": "net.genuinemerit.schema",
                "fields": {
                    "namespace": "net.genuinemerit.schema",
                    "store": "redis",
                    "channel": "redis_io",
                    "topic": "ontology_file",
                    "plan_ty": "get",
                    "service_ty": "subscribe",
                }
            }
        elif msg_ty == 2:
            data: dict = {
                "type": "record",
                "name": "redis.schema.put.request",
                "namespace": "net.genuinemerit.schema",
                "fields": {
                    "namespace": "net.genuinemerit.schema",
                    "store": "redis",
                    "channel": "redis_io",
                    "topic": "ontology_file",
                    "plan_ty": "remove",
                    "service_ty": "request",
                }
            }
        try:
            # Tho most OS's use little-endian, most comm protocols
            # use big-endian.
            # I guess the message needs to be less than 10,000 bytes?
            # Should probably have a check for that.
            size = len(data).to_bytes(4, 'big')
            # >>> Need to do a bit of debugging here. <<<

            pp(("data sent to bow_serde: ", data))

            data = size + SS.convert_py_dict_to_msg_jzby(data)
            await MS.send_msg(writer, chan)
            await MS.send_msg(writer, data)
        except OSError:
            print('Connection ended.')
    except asyncio.CancelledError:
        writer.close()
        await writer.wait_closed()

if __name__ == '__main__':
    """Host and port must be same as redis_server.py
    - Channel must be the one defined in redis_response.py
    - size: int (bytes)
    - interval: float (seconds) sleep between sends (a test throttle)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='curwen')
    parser.add_argument('--port', default=52020, type=int)
    parser.add_argument('--channel', default='/queue/redis_io_services')
    parser.add_argument('--interval', default=1, type=float)
    parser.add_argument('--size', default=0, type=int)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

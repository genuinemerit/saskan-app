#!/usr/bin/python3.9
"""
:module:    bow_msgs.py

Mockup for handling Data Admin messages.
Eventually this will be replaced by a real module
  and moved to component bow-data-admin.

These 2 functions are the same for all messages.
But using relative imports in Python is a pain.
So just include a copy of this file in the same directory.
Maybe eventually use the `bow_quiver` approach for this.

Main behaviors:

- Read a generic message:
    - {size: bytes(4) --> int,
       data: bytes(size) --> bytes}

- Write a generic message
    - {size: bytes(4) --> int,
       data: bytes(size) --> bytes}
"""
from asyncio import StreamReader, StreamWriter


async def read_msg(stream: StreamReader) -> bytes:
    """
    First 4 bytes are the size of the message.
    Convert them to an integer and read the rest of the message.
    """
    size_bytes = await stream.readexactly(4)
    size = int.from_bytes(size_bytes, byteorder='big')
    data = await stream.readexactly(size)
    return data


async def send_msg(stream: StreamWriter, data: bytes):
    """
    First send the size of the message in 4 bytes.
    Then send the message.
    """
    size_bytes = len(data).to_bytes(4, byteorder='big')
    stream.writelines([size_bytes, data])
    await stream.drain()

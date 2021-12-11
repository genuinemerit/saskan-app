#!/usr/bin/python3.9
"""
:module:    bow_serde.py

Mockup for handling message serialization / deserialization functions.
These would be used mainly by IOServices::redis_io, maybe others.
Using my own approach instead of Avro packages.

N.B.
- This is a mockup prototype.
- This is likely to be a generic function, maybe put in bow-quiver.

Main behaviors:

1. Serialize a message to a string.
- Read Python dict for a message
- Verify that it is well constructed according to my grammar
- Convert it to JSON
- If it is OK, compress and serialize as bytes

2. Deserialize a message from a string.
- Decompress and deserialize bytes to a string
- Convert JSON to Python dict

3. Return result to the caller.

@DEV
- Maybe eventually add an encrypt / decrypt option.
- Is this where to verify message formats match grammars
  as defined in Redis::Schema?
"""
import json
import zlib
from pprint import pprint as pp  # noqa: F401


class BowSerDe(object):
    """Generic Message ser/de handling."""

    def __init__(self):
        """Initialize BoW message de/serialization object."""
        pass

    def verify_grammar(self, msg_d: dict) -> str:
        """Parse Python dict for BoW goodness. If OK, convert to JSON."""
        # TAG - Do grammar checking here.
        msg_j: str = json.dumps(msg_d)

        pp(("js version of msg: ", msg_j))

        return(msg_j)

    def convert_py_dict_to_msg_jzby(self, msg_d: dict) -> object:
        """Convert Python dict to compressed JSON bytes."""
        msg_j = self.verify_grammar(msg_d)
        return zlib.compress(bytes(msg_j, 'utf-8'))

    def convert_msg_jzby_to_py_dict(self, msg_jzby: bytes) -> dict:
        """Convert compressed JSON bytes to Python dict."""
        msg_j = zlib.decompress(msg_jzby)
        return json.loads(msg_j)


# if __name__ == "__main__":
#     TAG - Put PyTest code here.
#     BSD = BowSerDe()

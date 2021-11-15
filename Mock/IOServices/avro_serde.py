#!/usr/bin/python3.9
"""
:module:    avro_serde.py

Mockup for handling core Avro serialization / deserialization functions.
These would be used mainly by IOServices::redis_io.

N.B. This is a mockup, and is not intended to be used in production.
- Avro is also used to handle response/request messages.
- This class is only for ser/de of Avro messages.

Main behaviors:
- Read JSON for a schema
- Convert it to an avro object
- Write avro object to file
- Write avro object to Redis
- Read avro object from file
- Read avro object from Redis
- Serialize avro object to bytes
- Deserialize bytes to avro object
"""
import json
import zlib
from pprint import pprint as pp  # noqa: F401

# from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter  # type: ignore
from avro.schema import parse  # type: ignore


class AvroSerDe(object):
    """Generic Avro ser/de handling."""

    def __init__(self):
        """Initialize Avro ser/de."""
        pass

    def verify_avro(self, avro_d: dict) -> str:
        """Parse Python dict for Avro goodness and convert to JSON."""
        avro_j: str = json.dumps(avro_d)
        _ = parse(avro_j)
        return(avro_j)

    def convert_py_dict_to_avro_binary(self, avro_d: dict) -> object:
        """Convert Python dict to Avro binary object."""
        return DatumWriter(self.verify_avro(avro_d))

    def convert_avro_binary_to_py_dict(self, avro_o: object) -> dict:
        """Convert Avro binary object to JSON."""
        schema: str = DatumReader(avro_o)
        return json.loads(schema)

    def convert_py_dict_to_avro_jzby(self, avro_d: dict) -> object:
        """Convert Python dict to compressed Avro JSON bytes."""
        avro_j = self.verify_avro(avro_d)
        return zlib.compress(bytes(avro_j, 'utf-8'))

    def convert_avro_jzby_to_py_dict(self, avro_jzby: bytes) -> dict:
        """Convert compressed Avro JSON bytes to Python dict."""
        avro_j = zlib.decompress(avro_jzby)
        return json.loads(avro_j)


if __name__ == "__main__":
    AVR = AvroSerDe()

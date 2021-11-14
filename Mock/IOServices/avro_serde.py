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
from pprint import pprint as pp               # noqa: F401

import json
import zlib
from avro.schema import parse                 # type: ignore
# from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter  # type: ignore


class AvroSerDe(object):
    """Generic Avro ser/de handling."""

    def __init__(self):
        """Initialize Avro ser/de."""
        pass

    def verify_avro_object(self, avro_dict: dict) -> str:
        """Parse Python dict for Avro goodness."""
        avro_json: str = json.dumps(avro_dict)
        _ = parse(avro_json)
        return(avro_json)

    def convert_py_dict_to_avro_binary(self, avro_dict: dict) -> object:
        """Convert Python dict to Avro Object."""
        return DatumWriter(self.verify_avro_object(avro_dict))

    def convert_avro_binary_to_py_dict(self, avro_obj: object) -> dict:
        """Convert Avro Object to JSON Schema."""
        schema: str = DatumReader(avro_obj)
        return json.loads(schema)

    def convert_py_dict_to_avro_json_zip(self, avro_dict: dict) -> object:
        """Convert Python dict to compressed Avro JSON bytes."""
        avro_json = self.verify_avro_object(avro_dict)
        return zlib.compress(bytes(avro_json, 'utf-8'))

    def convert_avro_json_zip_to_py_dict(self, avro_json_zip: bytes) -> dict:
        """Convert compressed Avro JSON bytes to Python dict."""
        avro_json = zlib.decompress(avro_json_zip)
        return json.loads(avro_json)


if __name__ == "__main__":
    AVR = AvroSerDe()

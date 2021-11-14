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

# import datetime
import json
from avro.schema import parse                 # type: ignore
# from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter  # type: ignore


class AvroSerDe(object):
    """Generic Avro ser/de handling."""

    def __init__(self):
        """Initialize Avro ser/de."""
        pass

    def convert_schema_to_avro(self, json_dict: dict) -> object:
        """Convert JSON Schema to Avro Object."""
        schema_json: str = json.dumps(json_dict)
        schema: object = parse(schema_json)
        schema = DatumWriter(schema)
        return schema

    def convert_avro_to_schema(self, avro_obj: object) -> str:
        """Convert Avro Object to JSON Schema."""
        schema: str = DatumReader(avro_obj)
        return schema


if __name__ == "__main__":
    AVR = AvroSerDe()

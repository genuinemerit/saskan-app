# saskan/tools/validate_json.py

1. JSON meta-schema vs your schema

Meta-schema ("$schema": "https://json-schema.org/draft/2020-12/schema") tells the validator what dialect the schema itself is written in.

Your schema (e.g. envelope.schema.json) is the file you write with type, properties, required, etc.

Your data (e.g. handshake_request.json) is what you validate.

So the typical flow is:

data.json  ⇐ validate against ⇒  schema.json


…and the schema.json itself declares "$schema": … inside it, so the validator knows it’s 2020-12.

2. How the Python snippet works

The validate_json.py I sketched expects two files:

python tools/validate_json.py schema.json data.json


schema.json = your local schema (e.g. infra/schema/envelope.schema.json).

data.json = a data instance you want to check.

The validator reads the schema, sees its "$schema": "https://json-schema.org/draft/2020-12/schema", and applies the correct rules. You don’t need to pass the meta-schema URL separately.

3. Example

envelope.schema.json

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "envelope.schema.json",
  "type": "object",
  "required": ["id", "ver", "name", "ts", "meta", "payload"],
  "properties": {
    "id": { "type": "string" },
    "ver": { "type": "string", "const": "1" },
    "name": { "type": "string" },
    "ts": { "type": "string", "format": "date-time" },
    "meta": { "type": "object" },
    "payload": {}
  },
  "additionalProperties": false
}


handshake_request.json

{
  "id": "123",
  "ver": "1",
  "name": "system.handshake.request",
  "ts": "2025-08-23T14:05:00Z",
  "meta": { "protocol": "0.1.0" },
  "payload": {
    "client_version": "0.1.0",
    "capabilities": ["welcome"]
  }
}


Run:

python tools/validate_json.py envelope.schema.json handshake_request.json


If handshake_request.json is valid, the script exits 0. If not, it prints schema-driven error messages and exits 1.

4. NDJSON case

If you want to validate an NDJSON file (multiple JSON objects, one per line):

Read the file line by line.

json.loads() each line into a dict.

Call the same validator on each dict.
(That’s a small tweak we can add later.)
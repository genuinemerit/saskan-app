# Messaging Formats

Building on the simple messaging format, service broker, listeners and senders prototyped in DataAdminServices.

Use Avro-like structures as a fundamental part of messaging architecture.

## Schema Registry

- Each type of message has an Avro-ish schema.
- Register each schema in the Schema Registry hosted on __Redis__, keyed by a unique name and version number.
- Use the Schema Registry to lookup a schema by ID and version, retrieve the schema, and validate a message against the schema.
- Access to Schema Registry is handled via __IOServices__.

## Schema in the Messaging Protocol

- Use the schema to encode and decode message bodies.
- Provide the schema ID and version as part of the message protocol.
- Extend the asyncio prototype...
- Each message has 3 parts -->
  - The topic to subscribe to (or \null)
  - The schema ID and version
  - The message body, encoded per the schema

## Tools for Message Schema Design and Build

- Used the "avro" package in PyPI to work on design, but then abandoned it as too complex for my needs (or maybe I just don't understand it)
- Start out simple, and then add more complexity as needed.
- Use plaintext, simple JSON at first, then look at binary, encrypted, compressed options if useful.
- Next, consider how to manage schema definitions as one of the things that can be edited in the `Saskan Eyes` editor. 
  - Automate storing, versioning, monitoring, reporting on them, as with other resoures.
  - Consider use of interim data sets to store them during development. 

### Basic Schema Design

- A Schema minimally has `type` and an object which describes its `form`.
  - Type is an Avro complex types: `record`, enum, array, map, union, fixed.
  - Assume all schemas will be records to start out.
- Usually has a name too.
  - Use the `name` to identify what Message uses the schema.
  - A `namespace` is optional, helps to qualify the name.
    - Maybe it identifies what component of the system "owns" this schema.
- The object is a dictionary of `fields`.
  - Each field has a `name` and `type`. May have optional attributes too, like fixed values or enums.
  - Type is an Avro primitive type: int, long, float, double, string, boolean, bytes, null.
  - Optional attributes include:
    - "default": default value for field
    - "order": order of field in record
    - "aliases": list of aliases for field
    - "doc": documentation for a speicific field
- Everything is JSON.

### Attributes

- Store a `hash` of the schema to assist with automation of versioning.
- The `doc` field is a URL that points to a wiki or something.
- In this example,
  - `Request` lists what SaskanConcepts are desired and what types of code are desired.
  - `Response`a identifies what SaskanConcept, what CodeTypes were created/retrieved, and links to that content. A JSON map is a dict. The keys are always string. Name the concept or code fragment, then provide link to the underlying ontology or code.
- Use Redis to store the contents. The value part of the maps will be a UUID or maybe a named mnemonic key or possibly the hash of the value would be best. Not sure yet which is best.
  - Thinking to optimize BowDataSchema routines.  Check Redis to see if requested object already been recently generated.
  - Use a `handshake` field as follows:
    - Request --> {"handshake": {"`token`": str}} contains a token-key to the requestor's LDAP credentials
    - Response --> {"handshake":
        "`auth`": ["role1", "role2", ...], # list of roles the requestor has which grant permission for requested operation
      }
      - If not authenticated, the handshake/auth response will be empty.

### Authentication/Authorization

- Use LDAP (or alternative, or homegrown prototype) to associate a user with a role. (I was not happy with LDAP.)
- Users in this case refer to the requestor, the Sender objects.
- Roles in this case refer to the Sender's permissions, which are organized by topic/message/authorization level.
- The token-key is a string that is used to identify the user.
  - To start, it can be hard-coded, persistent, maybe sent as a hash for one more layer of security.
- Not sure I like using camel case and then snake case as an alias. Just pick one.

Message schemas look something like this:

```json
/** GetSaskanDataObject Schemas **/

{
  "type": "record",
  "name": "GetSaskanDataObjectRequest",
  "namespace": "net.genuinemerit.data",
  "aliases": ["get_saskan_data_object_request"],
  "doc": "https://github.com/genuinemerit/bow-wiki/wiki/msgs/SaskanConcept/GetSaskanDataObject",
  "fields": [
    {"name": "topics", "type": "array"},
    {"name": "version", "type": "string"},
    {"name": "hash", "type": "string"},
    {"name": "handshake", "type": "map"},
    {"name": "SaskanConcepts", "type": "list"},
    {"name": "CodeTypes", "type": "list"}
  ]
}

{
  "type": "record",
  "name": "GetSaskanDataObjectResponse",
  "namespace": "net.genuinemerit.data",
  "aliases": ["get_saskan_data_object_response"],
  "doc": "https://github.com/genuinemerit/bow-wiki/wiki/msgs/SaskanConcept/GetSaskanDataObject",
  "fields": [
    {"name": "topics", "type": "array"},
    {"name": "version", "type": "string"},
    {"name": "hash", "type": "string"},
    {"name": "handshake", "type": "map"},
    {"name": "SaskanConceptObjects", "type": "map"},
    {"name": "CodeObjects", "type": "map"}
  ]
}
```

Message field _content_ looks something like this.
The message itself is still all bytes, with first 4 bytes being the length of the message. And the message body "header" matches the schema content. The field values are keys to Redis.

```json
/** GetSaskanDataObject message node field values **/

{
  "name": "GetSaskanDataObjectRequest",
  "fields": {
    "topics": ["SaskanConcept", "queue_SaskanConcept"],
    "version": "0.1.0",
    "hash": "asdf98a7d0f897adsf89asdfjksdfkj",
    "SaskanConcepts": ["SaskanResource"],
    "CodeTypes": ["SQLite"]
  }
}

{
  "name": "GetSaskanDataObjectResponse",
  "fields": {
    "topics": ["SaskanConcept", "queue_SaskanConcept"],
    "version": "0.1.0",
    "hash": "9845370asrkjfahsdfopi-908asoifj",

    "SaskanConceptObjects": {
      "SaskanResource": "SaskanConcept.json"
    },
    "CodeTypeObjects": {
      "SQLite": [
        "CREATE_SaskanConcept.sqlite",
        "EXPORT_SaskanConcept.sqlite",
        "DROP_SaskanConcept.sqlite",
        "INSERT_SaskanConcept.sqlite",
        "UPSERT_SaskanConcept.sqlite",
        "QUERY_BY_UID_SaskanConcept.sqlite",
        "QUERY_BY_OID_SaskanConcept.sqlite",
        "QUERY_BY_NAME_LIKE_SaskanConcept.sqlite",
        "DELETE_SaskanConcept.sqlite",
        "LOGICAL_DELETE_SaskanConcept.sqlite",
        "UPDATE_SaskanConcept.sqlite",
        "LOGICAL_UPDATE_SaskanConcept.sqlite"
      ]
    }
  }
}

Need similar documents for each of the messages. See Messages_DataSchemaEvents.md for an example.

Need to be able to return full message body for a given message.  There needs to be another Redis IO service that  returns the full message body for a given message.

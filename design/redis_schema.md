# Redis Schema

Things to consider...

1. How many Redis databases do I need?
2. What should I use for the Redis database names?
3. How should my Redis keys be structured?
4. Which keys should have expirations? Which ones permanent?
5. When should Redis data be SAVED?

## Redis Database Names

- 0: Default database. Use for prototyping --> SANDBOX
- 1: Database for storing Schema data (Avro, Redis itself, Sqlite, Topics, etc.) --> SCHEMA
- 2: Database for storing message result/response data --> RESULT
- 3: Logging and monitoring database using Streams --> LOG

## Redis Keys

- Use colons as separators
- Include tokens as in the keys when it makes sense to do so.
  - For example, if the data is sensitive and the reader should be authorized.
- SCHEMA Key structures
  - SchemaType:SchemaName:SchemaVersion
  - TopicName:MessageName:MessageAction:Version
  - Examples:
    - Avro:UserSchema:0.1.0
    - Avro:MessageRequestSchema:0.1.0
    - Avro:MessageResponseSchema:0.1.0
    - Redis:NamespacesSchema:0.1.0
    - Redis:KeysSchema:0.1.0
    - Sqlite:CreateTableSchema:0.1.0
    - Owl:SaskanOntologySchema:0.1.0
    - Topic:ontology_file:GetOntologyFile:request:0.1.0
    - Topic:ontology_file:GetOntologyFile:response:0.1.0

  - RESULT Key structures
    - Topic:Message:MessageId
    - Examples:
      - ontology_file:GetOntologyFile:asiuofas908r7we9r8h3ruioh3rhupiou8
      - saskan_concept:GetSaskanDataObject:lihkkkldfga980-sadfsdaf-dsfds

  - STREAM Key structures
    - StreamID
    - Examples:
      - [timestamp]-[sequencenumber]

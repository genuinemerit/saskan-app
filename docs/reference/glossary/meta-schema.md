# JSON Schema Meta-Schema and $-Keywords

The meta‑schema defines the structure of a JSON Schema itself. The `$schema` field (e.g., `https://json-schema.org/draft/2020-12/schema`) tells tools which dialect and keywords to use.

Common `$...` control keywords (not data fields):

- `$schema`: which draft/vocabulary to use
- `$id`: canonical identifier/URI for the schema
- `$ref`: reference another schema by URI/ID
- `$defs`: local named subschemas (previously `$definitions`)

Why we use them:

- Consistent tooling behavior (`$schema` = 2020‑12)
- Stable references across files (`$id`)
- Reuse and composition (`$ref`, `$defs`)

Minimal header example:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "envelope.schema.json",
  "type": "object"
}
```

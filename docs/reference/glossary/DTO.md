# Data Transfer Object (DTO)

A simple, serializable container of data used to carry structured information across layers or processes (e.g., UI ↔ client API ↔ engine). DTOs hold fields but no business logic.

- Notes: explicit shape, easy to serialize, often immutable; not an Entity or Domain object.
- Example:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class HandshakeReplyDTO:
    server_version: str
    session_id: str
    motd: str
    accepted_capabilities: List[str]
```

# Triage workflow for mypy

1. Run with codes and show-absolute-error-text:

   ```bash
   mypy --show-error-codes --pretty
   ```

2. Sort by frequency of codes; fix in this order: `return-value`, `arg-type`, `assignment`, `call-arg`, `union-attr`, `operator`, `index`, `has-type`, `attr-defined`, `no-redef`, `override`.
3. Use `reveal_type(x)` in failing scopes to see what mypy thinks you have.

## Fix patterns by error type

## `Optional` / `None` handling (`[assignment]`, `[attr-defined]`, `[union-attr]`)

**Symptom:** “Item of type 'None' has no attribute …”

```py
val: Optional[str] = get_name()
if val is None:
    return "anonymous"
# now val: str
return val.upper()
```

Prefer guards over `cast`. For reused checks, write a type guard:

```py
from typing import Optional, TypeGuard

def is_str(x: Optional[str]) -> TypeGuard[str]:
    return x is not None
```

## Return mismatches (`[return-value]`)

Annotate functions first; ensure all paths return:

```py
def parse(x: str) -> int:
    if x.isdigit():
        return int(x)
    raise ValueError(f"bad: {x}")  # not `return None`
```

## Callable args / kwonly (`[call-arg]`, `[arg-type]`)

Match signatures precisely:

```py
from typing import Callable

THandler = Callable[[str, int], None]
def run(h: THandler) -> None: ...
def handler(name: str, n: int) -> None: ...
run(handler)
```

For keyword-only APIs, reflect with `*` in your stubs or wrappers.

## Dicts that are really records (`[typeddict-item]`, `[index]`)

Stop using `dict[str, Any]` for structured data.

```py
from typing import TypedDict, NotRequired

class UserRow(TypedDict):
    id: int
    name: str
    email: NotRequired[str]

def f(row: UserRow) -> None:
    if 'email' in row:
        send(row['email'])
```

## Dataclasses / DTOs (“no attribute” / constructor issues)

Annotate fields and defaults:

```py
from dataclasses import dataclass, field
from typing import Literal

@dataclass(slots=True)
class ThemeDTO:
    name: str
    mode: Literal['major','minor']
    chords: list[str] = field(default_factory=list)
```

## Union narrowing (`[union-attr]`, `[assignment]`)

Use `isinstance` or `match`:

```py
def area(s: Circle | Rect) -> float:
    if isinstance(s, Circle):
        return 3.14 * s.r * s.r
    return s.w * s.h
```

## `Any` explosions (`[misc]`, `[no-any-return]`)

Quarantine `Any` at boundaries:

```py
from typing import Any, cast

def load_json(raw: str) -> dict[str, object]:
    data: Any = json.loads(raw)
    return cast(dict[str, object], data)
```

## Protocols for “duck types” (`[assignment]`, `[var-annotated]`)

When multiple impls share behavior:

```py
from typing import Protocol

class Logger(Protocol):
    def info(self, msg: str, /) -> None: ...

def use_log(log: Logger) -> None: ...
```

## Overloads for factory funcs (`[call-overload]`)

```py
from typing import overload

@overload
def make(x: int) -> int: ...
@overload
def make(x: str) -> str: ...
def make(x: int | str) -> int | str:
    return x
```

## Iterables / generators (`[type-var]`, `[generator-item-type]`)

Annotate yields:

```py
from collections.abc import Iterator

def chunks(xs: list[int], n: int) -> Iterator[list[int]]:
    for i in range(0, len(xs), n):
        yield xs[i:i+n]
```

## SQLAlchemy / ORM hotspots

* Model attrs: add `typing_extensions.Annotated` or use SQLAlchemy 2.0-style typing.

```py
from sqlalchemy.orm import Mapped, mapped_column
class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

* Session returns `Any` unless typed: annotate query results.

## Typer / Click CLIs

Annotate option/arg types to avoid `Any`:

```py
import typer

def start(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host"),
    port: int = typer.Option(8000, "--port", "-p", help="Port"),
) -> None:
    ...
```

## Pandas / 3rd-party without stubs (`[attr-defined]`)

* Install types if available: `pip install types-requests types-PyYAML`, etc.
* If none exist, isolate to a module and use narrow `Any` + typed wrappers.

# Config hardening (incremental)

`mypy.ini`:

```ini
[mypy]
python_version = 3.12
warn_unused_ignores = True
warn_redundant_casts = True
no_implicit_optional = True
strict_equality = True
disallow_incomplete_defs = True
disallow_untyped_defs = True
disallow_untyped_calls = True
check_untyped_defs = True
show_error_codes = True
pretty = True
implicit_reexport = False

# 3rd-party libs lacking types
[mypy-sqlalchemy.*]
ignore_missing_imports = True

[mypy-typer.*]
ignore_missing_imports = True

# Allow legacy modules to compile; ratchet later
[mypy-saskan.legacy.*]
disallow_untyped_defs = False
disallow_untyped_calls = False
```

# Tactics that save hours

* **Guard > cast**: prefer flow-sensitive checks; reserve `cast` for trusted conversions.
* **`Final` & `Literal`**: lock down constants and mode strings to eliminate branch noise.
* **`assert` after invariants**: both documents assumptions and narrows types.
* **Local ignores with reasons**: `# type: ignore[arg-type]  # external lib mismatch`—and keep `warn_unused_ignores` on.

# Quick fixes you’ll likely need in Saskan

* DTOs: add explicit field types + `slots=True`.
* CLI: annotate Typer options and return `None` explicitly.
* JSON schema layer: introduce `TypedDict` shapes for loaded schema fragments consumed by DTO constructors.
* Music/theory utilities: replace numeric tuples with small `NamedTuple`/`dataclass` types to stop tuple length/type drift.

Paste a few representative mypy errors (with codes) and I’ll hand back precise patches you can drop in.

# from typing import Mapping

In typing, Mapping[K, V] means a read-only dict-like object with keys of type K and values of type V.

It is s an abstract type: many objects (dicts, default dicts, ChainMap) satisfy Mapping[str, str].

In our case, _load_bundle() returns a dict from yaml.safe_load, but annotating as Mapping[str, str] is more general.
It promises only that callers can look up keys/values, not mutate them.

So...

```python
def _load_bundle(locale: str) -> Mapping[str, str]:
````

... this returns something like a dictionary from str → str.
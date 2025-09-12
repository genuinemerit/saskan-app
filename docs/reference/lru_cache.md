# from functools import lru_cache

lru_cache = Least Recently Used cache.

Applied as a decorator (@lru_cache), it memoizes the results of a function call, keyed by its arguments.

Why here? Loading a YAML file from disk every time you need a translation would be wasteful.

With @lru_cache, the function load_bundle("es-ES") runs once, then returns the cached dict on every subsequent call.

Example:

```python
@lru_cache(maxsize=4)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
```

This makes recursive Fibonacci actually fast, because results are cached.

Python's LRU (Least Recently Used) cache is a caching mechanism that stores a limited number of results from function calls, automatically discarding the least recently used entries when the cache reaches its capacity. It is implemented using the @lru_cache decorator from the functools module, which helps improve performance by avoiding repeated calculations for the same inputs.

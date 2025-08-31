# from __future__ import annotations

A future import changes how the Python parser behaves.

This one makes type annotations “lazy” strings instead of actual objects at runtime.

Without it, Python tries to resolve type hints immediately, which can cause circular import problems.

With it, `Mapping[str, str]`, for example, is just stored as the string "Mapping[str, str]" until a type checker inspects it.

Recommended in modern codebases (and default in Python 3.11+) for speed and fewer import headaches.

Rule of thumb: keep it at the top of modules that use type hints — it makes your type hints future-proof.

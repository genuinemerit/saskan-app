# full gate

## Full Gate (slang):
The complete set of checks (lint, typecheck, tests, etc.) that code must pass before merging. Developers “run the full gate” locally to avoid embarrassment when CI plays gatekeeper. (Also: something only the heppest of cats remember to do.)

“run the full gate” is a bit of dev-slang that crept in from CI/CD land. It isn’t really “the kids these days” so much as a shorthand from build/release engineers:

“The gate” = the whole set of quality checks you must pass before code is allowed to merge (like a gatekeeper).

“Run the full gate” = run all of those checks locally before you push/PR, so you don’t waste a CI run (or your teammates’ time).

In our repo, the “gate” is basically:

Lint → code style (black/isort/flake8/pre-commit hooks)

Typecheck → mypy

Tests → pytest

CI glue → make sure everything wires up as expected

That’s exactly what your make check target is doing: one-command to simulate what CI will do.

“run the complete quality checks” or “do a local CI run.”



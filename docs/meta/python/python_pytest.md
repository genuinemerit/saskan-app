# Pytest

## not part of package

Should tests/ contain an __init__.py?

No. With pytest, you typically do not make tests/ a package. Skipping __init__.py avoids import path weirdness and keeps conftest.py discovery simple. Only add __init__.py if you have a very specific reason to treat tests as importable package code (rare).

## tests/conftest.py

What is conftest.py?

A test-only Python file that pytest auto-discovers (no imports needed) in a test directory and its subdirs.

It’s the right place to put shared fixtures, hooks, and test config that multiple tests need.

You can have multiple conftest.py files at different directory levels; scope is hierarchical.

Put fixtures in tests/conftest.py (no imports needed—pytest auto-discovers it). Keep fixtures fast and deterministic in unit tests; push I/O or external deps to integration and mark them so CI or local runs can include/exclude intentionally.

## fixtures

What’s a fixture?

A function decorated with @pytest.fixture that provides reusable setup/teardown for tests.

Tests request fixtures by naming them as function args.

Common uses: test clients/runners, temp dirs/files, environment patches, sample data, DB sessions, etc.

### Fixture basics
```python
import pytest

@pytest.fixture
def sample_user():
    return {"name": "Phoenix"}
```

Usage:

```python
def test_greets(sample_user):
    assert sample_user["name"] == "Phoenix"
```

### Fixture scopes

function (default): new instance per test.

class: once per test class.

module: once per file.

package: once per package (pytest ≥ 8).

session: once for the entire test run.

```python
@pytest.fixture(scope="module")
def expensive_resource():
    ...
```

### Autouse fixtures (auto use)

Run automatically (don’t have to be named in tests). Handy for global env tweaks or cleanup.

```python
@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.delattr("socket.socket.connect")
```
### Handy built-in fixtures you’ll likely use soon

tmp_path / tmp_path_factory: per-test temp directories for file I/O.

monkeypatch: temporarily set env vars, attributes, or sys.path.

def test_env(monkeypatch):
    monkeypatch.setenv("FOO", "bar")


capsys / caplog: capture stdout/stderr or logs.

request: introspect the current test node (rarely needed).

Best practices (quick)

Keep fixtures small, explicit, and fast (especially in unit tests).

Prefer factory-style fixtures to generate data:

@pytest.fixture
def make_user():
    def _make_user(name="Phoenix"):
        return {"name": name}
    return _make_user


Avoid deep fixture nesting; compose simple ones instead.

Put widely used fixtures in top-level tests/conftest.py; niche ones next to the tests that need them.

Optional: register markers (now or later)

In pyproject.toml, you can predeclare markers you’ll use:

[tool.pytest.ini_options]
markers = [
  "integration: hits real I/O",
  "e2e: full stack",
  "slow: long-running"
]

## multiple test directories

Separate /unit, /integration, /user now?

Not yet. Keep it simple for the first PR. Start with a single tests/ (or saskan/tests/ if you’ve committed to in-package tests) and use markers to distinguish test types. You can split into subfolders later when you actually need them.

When the suite grows, you can move to:

tests/
  unit/
  integration/
  e2e/

…and keep using markers. Subfolders + markers make selection crystal clear, but there’s no benefit until you actually have enough tests to justify the structure.

## markers

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]  # or ["saskan/tests"] if you keep tests alongside package
markers = [
  "integration: tests that hit real I/O or services",
  "e2e: end-to-end tests",
  "slow: long-running tests"
]
```
Run patterns you’ll use:

```bash
# all unit tests (assuming you mark non-unit tests)
pytest -m "not integration and not e2e and not slow"

# only integration tests
pytest -m "integration"
```


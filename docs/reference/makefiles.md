# Makefiles

Here’s the high-level playbook for using **Makefiles** in a **Poetry-centric** Python repo.

### Why use `make` with Poetry

* **Unified entrypoints**: `make` gives short, memorable commands that wrap `poetry run …`.
* **Composable tasks**: encode task dependencies (e.g., `test` depends on `lint`).
* **CI parity**: same targets locally and in GitHub Actions.

### Core principles

* **All commands run via Poetry**: `poetry run …` so you’re always inside the venv (no reliance on `poetry shell`).
* **Idempotent targets**: safe to run repeatedly (`install`, `format`, `test`).
* **Small, focused targets**: avoid “god” tasks; compose instead.
* **Use `.PHONY`** for non-file targets.

### Typical target set

* `init`: `poetry install` (optionally `poetry lock --no-update`).
* `lock`: update lockfile (`poetry lock && poetry install`).
* `lint`: `ruff` + `flake8` (if both) + `isort --check` + `black --check`.
* `format`: `isort . && black .`.
* `type`: `mypy`.
* `test`: `pytest -q` (optionally with coverage).
* `cov`: run coverage + report (HTML optional).
* `run`: your CLI (`poetry run saskan …`).
* `clean`: remove caches (`.pytest_cache`, `__pycache__`, `htmlcov`, dist artifacts).
* `release` (optional): tag + build + publish (if/when you publish).

### Cross-platform notes

* **GNU Make** is standard on Linux/macOS. On Windows, use Git Bash/Mingw or WSL.
* Keep shell features simple (portable `sh`), avoid bash-isms when possible.

### How it fits with Poetry

* **Dependency resolution**: leave to Poetry (`poetry install`, `poetry lock`).
* **Execution**: wrap tools with `poetry run` so they use project’s pinned versions.
* **Config**: put tool configs in `pyproject.toml` (black, isort, ruff, mypy, pytest), not in the Makefile.

### Minimal example (for reference later)

```make
# Makefile (Poetry-centric)
.PHONY: init lock lint format type test cov run clean

init:
	poetry install

lock:
	poetry lock
	poetry install

lint:
	poetry run ruff check .
	poetry run isort . --check-only
	poetry run black . --check

format:
	poetry run isort .
	poetry run black .

type:
	poetry run mypy

test:
	poetry run pytest -q

cov:
	poetry run coverage run -m pytest
	poetry run coverage report -m

run:
	poetry run saskan --help

clean:
	rm -rf .pytest_cache __pycache__ */__pycache__ htmlcov dist build .ruff_cache .mypy_cache .coverage coverage.xml
```

For first actual prototype, see:  saskan-app/Makefile


### Variations to consider later

* **Parametrized targets**: `make run ARGS="--seed=42"` → `poetry run saskan $(ARGS)`.
* **Task dependencies**: `test: lint type` to enforce quality gates.
* **Release automation**: integrate `release-drafter`, tagging, `poetry build`, `poetry publish`.
* **Matrix runners**: pair with CI to call the same targets (`make lint test`).

When you’re ready, tailor a Makefile to your exact toolchain and CI triggers.


### Best practices baked in

- Everything via Poetry (poetry run …) so tools use the project venv.

- Single-source line length/format: formatters/lints rely on your pyproject.toml.

- `check` bundles quality gates for CI and local use.

- Guarded release: refuses to run on a dirty tree; uses poetry version for semver bumps and creates a git tag. You still publish manually (aligns with Release Drafter).

#### Useful variations you can add later

- DB helpers (if you adopt Docker): db-up, db-down, db-migrate, gated to only run if docker-compose.yml exists.

- Smoke tests: a fast subset for pre-push hook or make smoke.

- Docs: docs-serve for local preview (if you add MkDocs/Sphinx).

See version of Makefile for old saskan-app project for examples of generating docs and running test suites.

- Perf checks: bench running pytest-benchmark and storing .benchmarks/.

- Type levels: type-strict vs. type to allow gradual mypy adoption.

We can adapt the release target to auto-push and/or to call `gh release create` with the draft notes from Release Drafter, but keeping “manual push” is safer until we’re comfortable with the process.

### Summary of what to go ahead and add now based on using the GitFlow pattern

Guards: guard-clean, guard-branch-*, guard-branch-pattern-*

Dev UX bundle: setup, fmt, lint, test, check

Version helpers: version, bump

GitFlow ops: start-release, finish-release, start-hotfix, finish-hotfix

Packaging: build, clean-dist

Optional: gh-release, ci-pr, ci-tag

### How to use (GitFlow path) from Makefile:

Start release: make start-release RELEASE=1.2.0

Stabilize on release/1.2.0 (fixes/docs only). Optionally make bump BUMP=patch.

Finish release (from that branch): make finish-release

Hotfix flow mirrors the above with start-hotfix / finish-hotfix.

This keeps our existing release target as a legacy/manual option while nudging toward the GitFlow cadence.


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

### Variations to consider later

* **Parametrized targets**: `make run ARGS="--seed=42"` → `poetry run saskan $(ARGS)`.
* **Task dependencies**: `test: lint type` to enforce quality gates.
* **Release automation**: integrate `release-drafter`, tagging, `poetry build`, `poetry publish`.
* **Matrix runners**: pair with CI to call the same targets (`make lint test`).

When you’re ready, tailor a Makefile to your exact toolchain and CI triggers.


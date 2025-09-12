# Poetry

## `pyproject.toml` notes

- Flat layout: keep `__init__.py` in importable package dirs (`core`, `engine`, …)
- CLI: add `ui_cli/manage.py` with a `cli()` entrypoint (Typer/Click)
- DB: default to SQLite via SQLAlchemy; enable Postgres with extras/groups
- Dev toolchain: black, isort, ruff, pytest, coverage, mypy via `[tool.*]` stanzas
- Heavy/optional deps: install on demand via extras (e.g., `--with analytics`)

## Basics

- Install deps and create a venv for the project:

```bash
poetry install
```

- Run inside the venv without activating it:

```bash
poetry run <command>
```

- Inspect the current environment:

```bash
poetry env info
```

### Shell access

Starting with Poetry 2.x, the `shell` command moved to a plugin.

- Install the plugin if you prefer `poetry shell`:

```bash
poetry self add poetry-plugin-shell
poetry shell
```

- Without the plugin, you can activate the env explicitly:

```bash
# POSIX shells
eval "$(poetry env activate)"
# or
source "$(poetry env info --path)/bin/activate"
```

References: [managing environments](https://python-poetry.org/docs/managing-environments/)

## Refresh the environment (nuke & pave)

Check environments Poetry knows about:

```bash
poetry env list
```

Remove the current one and recreate it:

```bash
poetry env remove python            # or provide the path from `poetry env list`
poetry install
```

Commit the new `poetry.lock` (applications should commit lockfiles).

## Activate / deactivate

- Activate:

```bash
eval "$(poetry env activate)"      # recommended
# or, if you prefer
source "$(poetry env info --path)/bin/activate"
```

- Deactivate:

```bash
deactivate
```

- Alternative to activation for one‑off commands:

```bash
poetry run pytest
```

## Refresh after editing `pyproject.toml`

- Metadata‑only changes (name, description, classifiers, package layout): no action
- Added/removed/updated dependencies:

```bash
poetry install
```

- Big cleanup / ensure lock and venv are synced:

```bash
poetry lock --no-update
poetry install
```

Best practice

- Run dependency management commands (`poetry install/add/update`) outside an activated venv
- Use `poetry run …` or an activated shell to execute code

## Quick helper (optional)

Create a tiny helper to activate the env quickly:

`tools/poetry_activate`:

```bash
#!/usr/bin/env bash
source "$(poetry env info --path)/bin/activate"
```

Make it executable and source it:

```bash
chmod +x tools/poetry_activate
source tools/poetry_activate
```

## Makefile

Also see helpers created in Makefile for standard poetry commands

## References

- [Poetry docs](https://python-poetry.org/docs/)
- [Managing environments](https://python-poetry.org/docs/managing-environments/)
- [CLI (env)](https://python-poetry.org/docs/cli/#env)
- [`poetry shell` plugin](https://github.com/python-poetry/poetry-plugin-shell)
